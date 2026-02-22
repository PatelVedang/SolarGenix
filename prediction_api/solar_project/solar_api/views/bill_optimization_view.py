from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from solar_api.serializers import (
    BillOptimizationRequestSerializer,
    BillOptimizationResponseSerializer,
)
from solar_api.services.bill_optimization_service import BillOptimizationService

# Stateless service — safe to instantiate once at module level
_service = BillOptimizationService()


class BillOptimizationView(APIView):
    """
    POST /api/solar/bill-optimization-slab/

    Calculates the recommended solar capacity to reduce a monthly electricity
    bill from a current amount to a target amount, using Indian slab-based
    tariff calculations.
    """

    @swagger_auto_schema(
        operation_summary="Solar bill optimisation (slab tariff)",
        operation_description=(
            "Accepts the user's current electricity bill and a desired target bill, "
            "then calculates the required solar capacity (kW) and number of panels "
            "needed to bridge the gap using Indian slab-based tariff rates.\n\n"
            "**Tariff slabs (₹/unit)**\n"
            "| Slab | Rate |\n"
            "|------|------|\n"
            "| 0 – 50 units | ₹3.00 |\n"
            "| 51 – 100 units | ₹3.50 |\n"
            "| 101 – 200 units | ₹5.00 |\n"
            "| 201+ units | ₹7.00 |\n\n"
            "**Assumptions**: 1 kW solar → 120 units/month · panel size = 540 W"
        ),
        request_body=BillOptimizationRequestSerializer,
        responses={
            200: BillOptimizationResponseSerializer,
            400: "Validation error — see error details in response body.",
            500: "Internal server error.",
        },
        tags=["Solar Optimisation"],
    )
    def post(self, request):
        # ── 1. Validate & deserialize request ────────────────────────
        req_serializer = BillOptimizationRequestSerializer(data=request.data)
        if not req_serializer.is_valid():
            return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # ── 2. Run pure-calculation service ───────────────────────────
        result, status_code = _service.optimize(req_serializer.validated_data)

        if status_code != 200:
            return Response(result, status=status_code)

        # ── 3. Serialize & return response ────────────────────────────
        resp_serializer = BillOptimizationResponseSerializer(result)
        return Response(resp_serializer.data, status=status.HTTP_200_OK)
