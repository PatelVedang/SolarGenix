import math


# ---------------------------------------------------------------------------
# Indian Electricity Tariff Slabs (monthly, residential)
# Rates are in ₹ per unit (kWh).
# Add or adjust slabs here without touching any other code.
# ---------------------------------------------------------------------------
DEFAULT_TARIFF_SLABS = [
    {"min": 0,   "max": 50,   "rate": 3.0},
    {"min": 51,  "max": 100,  "rate": 3.5},
    {"min": 101, "max": 200,  "rate": 5.0},
    {"min": 201, "max": None, "rate": 7.0},   # None → unbounded
]

# Solar generation assumptions (India average)
UNITS_PER_KW_PER_MONTH: float = 120.0   # 1 kW produces ~120 units/month
DEFAULT_PANEL_WATT: float = 540.0        # Standard panel size in watts


class BillOptimizationService:
    """
    Pure-calculation service for solar bill optimisation using Indian
    slab-based electricity tariffs.

    No machine learning. No external I/O. Fully stateless — every call to
    ``optimize()`` is independent.

    Design principles
    -----------------
    * Forward calculation : ``calculate_bill_from_units`` → bill amount given units.
    * Reverse calculation : ``estimate_units_from_bill`` → units given bill amount.
    * Solar sizing        : derives required kW and panel count from unit delta.
    * Safety guards       : clamps negative solar values; validates all inputs.
    """

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def optimize(self, validated_data: dict) -> tuple[dict, int]:
        """
        Main method called by the view layer.

        Parameters
        ----------
        validated_data : dict
            Already-validated data from ``BillOptimizationRequestSerializer``.
            All fields are guaranteed to be present with correct Python types.

        Returns
        -------
        (response_dict, http_status_code)
        """
        try:
            # ── 1. EXTRACT FIELDS (types already guaranteed by serializer) ──
            current_bill: float     = validated_data["current_bill"]
            target_bill: float      = validated_data["target_bill"]
            has_solar: bool         = validated_data.get("has_solar", False)
            solar_capacity_kw: float = validated_data.get("solar_capacity_kw") or 0.0

            slabs = DEFAULT_TARIFF_SLABS

            # ── 2. SLAB-BASED REVERSE CALCULATIONS ────────────────────
            current_units: float   = self.estimate_units_from_bill(current_bill, slabs)
            target_units: float    = self.estimate_units_from_bill(target_bill, slabs)
            units_to_offset: float = max(0.0, current_units - target_units)

            # ── 3. SOLAR SIZING ───────────────────────────────────────
            if has_solar:
                existing_generation = solar_capacity_kw * UNITS_PER_KW_PER_MONTH
                required_kw = (
                    current_units - existing_generation - target_units
                ) / UNITS_PER_KW_PER_MONTH
            else:
                required_kw = units_to_offset / UNITS_PER_KW_PER_MONTH

            # Safety clamp — never return negative solar capacity
            required_kw = max(0.0, required_kw)

            # Panel count — round UP so the target is always met
            panel_kw   = DEFAULT_PANEL_WATT / 1000.0   # 0.54 kW per panel
            num_panels = math.ceil(required_kw / panel_kw) if required_kw > 0 else 0

            estimated_monthly_generation = round(required_kw * UNITS_PER_KW_PER_MONTH, 2)

            # ── 4. RESPONSE ───────────────────────────────────────────
            return {
                "current_units":                round(current_units, 2),
                "target_units":                 round(target_units, 2),
                "units_to_offset":              round(units_to_offset, 2),
                "recommended_solar_kw":         round(required_kw, 3),
                "recommended_panels":           num_panels,
                "estimated_monthly_generation": estimated_monthly_generation,
            }, 200

        except Exception as exc:
            return {"error": "Internal server error", "details": str(exc)}, 500

    # ------------------------------------------------------------------
    # Core calculation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_bill_from_units(units: float, slabs: list[dict]) -> float:
        """
        Forward calculation: compute the electricity bill (₹) for a given
        number of consumed units using the provided tariff slabs.

        Parameters
        ----------
        units : float
            Total electricity consumed in kWh.
        slabs : list[dict]
            Ordered list of slab dicts with keys ``min``, ``max``, ``rate``.
            ``max`` of ``None`` means the slab is unbounded.

        Returns
        -------
        float
            Total bill amount in ₹.
        """
        bill = 0.0
        remaining = units

        for slab in slabs:
            if remaining <= 0:
                break

            slab_min: int   = slab["min"]
            slab_max        = slab["max"]   # None for last slab
            rate: float     = slab["rate"]

            # Effective width of this slab
            if slab_max is None:
                slab_units = remaining          # consume all that's left
            else:
                slab_capacity = slab_max - slab_min + 1
                slab_units    = min(remaining, slab_capacity)

            bill      += slab_units * rate
            remaining -= slab_units

        return round(bill, 2)

    @staticmethod
    def estimate_units_from_bill(bill: float, slabs: list[dict]) -> float:
        """
        Reverse calculation: estimate total kWh consumed to produce a given
        monthly bill amount using progressive slab accumulation.

        Parameters
        ----------
        bill : float
            Monthly electricity bill in ₹.
        slabs : list[dict]
            Same slab structure as ``calculate_bill_from_units``.

        Returns
        -------
        float
            Estimated units consumed in kWh.
        """
        units     = 0.0
        remaining = bill

        for slab in slabs:
            if remaining <= 0:
                break

            slab_min: int   = slab["min"]
            slab_max        = slab["max"]
            rate: float     = slab["rate"]

            if slab_max is None:
                # Last slab — consume all remaining bill at this rate
                units     += remaining / rate
                remaining  = 0.0
            else:
                slab_capacity  = slab_max - slab_min + 1          # units in slab
                slab_full_cost = slab_capacity * rate              # ₹ to exhaust slab

                if remaining >= slab_full_cost:
                    # Entire slab consumed
                    units     += slab_capacity
                    remaining -= slab_full_cost
                else:
                    # Partial slab
                    units     += remaining / rate
                    remaining  = 0.0

        return round(units, 4)

    # Validation is fully delegated to BillOptimizationRequestSerializer.
    # The service trusts that validated_data already contains correct types.
