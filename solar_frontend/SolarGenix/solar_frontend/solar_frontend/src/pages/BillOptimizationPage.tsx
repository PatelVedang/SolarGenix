import { useState } from "react";
import { optimizeBill } from "../api/predictionApi";

const BillOptimizationPage = () => {
  const [form, setForm] = useState({
    current_bill: "",
    target_bill: "",
    location: "",
    has_solar: false,
    solar_capacity_kw: "",
  });

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const val = type === "checkbox" ? (e.target as HTMLInputElement).checked : value;
    setForm({ ...form, [name]: val });
  };

  const handleOptimize = async () => {
    if (!form.current_bill || !form.target_bill) {
      alert("Please enter both current and target bill amounts.");
      return;
    }

    if (Number(form.target_bill) > Number(form.current_bill)) {
      alert("Target bill must be less than or equal to current bill.");
      return;
    }

    if (form.has_solar && !form.solar_capacity_kw) {
      alert("Please enter your existing solar capacity.");
      return;
    }

    setLoading(true);
    try {
      const data = await optimizeBill({
        current_bill: Number(form.current_bill),
        target_bill: Number(form.target_bill),
        location: form.location,
        has_solar: form.has_solar,
        solar_capacity_kw: form.has_solar ? Number(form.solar_capacity_kw) : null,
      });

      setResult(data);
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.target_bill || "Optimization failed. Check backend or inputs.");
    }
    setLoading(false);
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap');
        
        .bill-optimization-page {
          font-family: 'Outfit', sans-serif;
        }
        
        .gradient-border {
          position: relative;
          background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
          border-radius: 24px;
        }
        
        .gradient-border::before {
          content: '';
          position: absolute;
          inset: -2px;
          border-radius: 24px;
          padding: 2px;
          background: linear-gradient(135deg, #fbbf24, #f59e0b, #fbbf24);
          background-size: 200% 200%;
          -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
          -webkit-mask-composite: xor;
          mask-composite: exclude;
          opacity: 0.5;
          animation: borderRotate 3s linear infinite;
          z-index: 0;
          pointer-events: none;
        }
        
        .gradient-border > * {
          position: relative;
          z-index: 1;
        }
        
        @keyframes borderRotate {
          to {
            background-position: 200% center;
          }
        }
        
        .input-glow {
          transition: all 0.3s ease;
        }
        
        .input-glow:focus {
          box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.2);
          border-color: #fbbf24;
          outline: none;
        }
        
        .result-card {
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          animation: slideUp 0.5s ease-out;
        }
        
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .stat-card {
          position: relative;
          overflow: hidden;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .stat-card:hover {
          transform: translateY(-4px) scale(1.02);
        }
        
        .stat-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
          transition: left 0.5s;
        }
        
        .stat-card:hover::before {
          left: 100%;
        }
        
        .loading-spinner {
          border: 3px solid rgba(251, 191, 36, 0.3);
          border-top-color: #fbbf24;
          border-radius: 50%;
          width: 24px;
          height: 24px;
          animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .pulse-dot {
          animation: pulse-dot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse-dot {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.1); }
        }
        
        .energy-wave {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          height: 4px;
          background: linear-gradient(90deg, transparent, #fbbf24, transparent);
          animation: wave 2s linear infinite;
        }
        
        @keyframes wave {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        .metric-number {
          font-family: 'JetBrains Mono', monospace;
          font-weight: 700;
        }

        .grid-pattern {
          background-image: 
            linear-gradient(rgba(251, 191, 36, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(251, 191, 36, 0.03) 1px, transparent 1px);
          background-size: 50px 50px;
        }
      `}</style>

      <div className="bill-optimization-page min-h-screen bg-slate-950 relative overflow-hidden">
        <div className="absolute inset-0 grid-pattern opacity-50"></div>

        <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
          {/* Header Section */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-amber-500/10 border border-amber-500/20 rounded-full text-amber-400 text-sm font-semibold mb-6 backdrop-blur-sm">
              <span className="pulse-dot w-2 h-2 bg-amber-400 rounded-full"></span>
              Smart Solar Optimization
            </div>
            <h1 className="text-5xl md:text-6xl font-black text-white mb-4">
              Bill <span className="bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Optimization</span>
            </h1>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Calculate precisely how much solar capacity you need to slash your electricity bills.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8 items-start">
            {/* LEFT: Input Form */}
            <div className="gradient-border p-8">
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
                  <span className="text-3xl">💰</span>
                  Input Details
                </h2>
                <p className="text-slate-400 text-sm">Enter your current bill and desired target</p>
              </div>

              <div className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-2">
                      ₹ Current Monthly Bill
                    </label>
                    <input
                      name="current_bill"
                      type="number"
                      placeholder="e.g., 5000"
                      onChange={handleChange}
                      value={form.current_bill}
                      className="input-glow w-full bg-slate-900/50 border-2 border-slate-700 text-white p-4 rounded-xl transition-all placeholder:text-slate-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-2">
                      ₹ Target Monthly Bill
                    </label>
                    <input
                      name="target_bill"
                      type="number"
                      placeholder="e.g., 500"
                      onChange={handleChange}
                      value={form.target_bill}
                      className="input-glow w-full bg-slate-900/50 border-2 border-slate-700 text-white p-4 rounded-xl transition-all placeholder:text-slate-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    📍 Location (Optional)
                  </label>
                  <input
                    name="location"
                    placeholder="e.g., Mumbai, Maharashtra"
                    onChange={handleChange}
                    value={form.location}
                    className="input-glow w-full bg-slate-900/50 border-2 border-slate-700 text-white p-4 rounded-xl transition-all placeholder:text-slate-500"
                  />
                </div>

                <div className="flex items-center gap-3 p-4 bg-slate-900/50 border-2 border-slate-700 rounded-xl">
                  <input
                    name="has_solar"
                    type="checkbox"
                    checked={form.has_solar}
                    onChange={handleChange}
                    className="w-5 h-5 rounded border-slate-700 text-amber-500 focus:ring-amber-500 cursor-pointer"
                  />
                  <label className="text-sm font-semibold text-slate-300 cursor-pointer">
                    Already have solar panels installed?
                  </label>
                </div>

                {form.has_solar && (
                  <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                    <label className="block text-sm font-semibold text-slate-300 mb-2">
                      ⚡ Existing Solar Capacity (kW)
                    </label>
                    <input
                      name="solar_capacity_kw"
                      type="number"
                      step="0.1"
                      placeholder="e.g., 2.5"
                      onChange={handleChange}
                      value={form.solar_capacity_kw}
                      className="input-glow w-full bg-slate-900/50 border-2 border-slate-700 text-white p-4 rounded-xl transition-all placeholder:text-slate-500"
                    />
                  </div>
                )}

                <button
                  onClick={handleOptimize}
                  disabled={loading}
                  className="group relative w-full bg-gradient-to-r from-amber-500 to-orange-500 text-slate-900 font-bold text-lg py-5 rounded-xl overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-amber-500/50 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02]"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-3">
                      <div className="loading-spinner"></div>
                      Optimizing...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      ⚡ Calculate Optimization
                      <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </span>
                  )}
                  <div className="energy-wave"></div>
                </button>
              </div>
            </div>

            {/* RIGHT: Results Section */}
            <div className="lg:sticky lg:top-24">
              {!result ? (
                <div className="gradient-border p-12 text-center">
                  <div className="text-7xl mb-6 opacity-50">📉</div>
                  <h3 className="text-2xl font-bold text-white mb-3">No Results Yet</h3>
                  <p className="text-slate-400">
                    Enter your bill details to see your customized solar recommendation.
                  </p>
                </div>
              ) : (
                <div className="result-card space-y-6">
                  {/* MAIN RECOMMENDATION */}
                  <div className="gradient-border p-8 bg-gradient-to-br from-amber-500/20 to-orange-500/20">
                    <p className="text-amber-400 font-bold text-sm uppercase tracking-wider mb-2">Recommended System</p>
                    <div className="flex items-baseline gap-2 mb-4">
                      <span className="metric-number text-6xl font-black text-white">{result.recommended_solar_kw}</span>
                      <span className="text-2xl font-bold text-amber-400">kW</span>
                    </div>
                    <div className="flex items-center gap-3 text-slate-300 font-medium">
                      <span className="text-2xl">🧩</span>
                      Requires approximately <span className="text-white font-bold">{result.recommended_panels} panels</span> (540W each)
                    </div>
                  </div>

                  {/* STATS GRID */}
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="stat-card bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
                      <p className="text-sm text-slate-400 mb-1">Units to Offset</p>
                      <p className="metric-number text-3xl font-bold text-emerald-400">
                        {Math.round(result.units_to_offset)}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">kWh / Month</p>
                    </div>

                    <div className="stat-card bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
                      <p className="text-sm text-slate-400 mb-1">Estimated Generation</p>
                      <p className="metric-number text-3xl font-bold text-blue-400">
                        {Math.round(result.estimated_monthly_generation)}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">kWh / Month</p>
                    </div>

                    <div className="stat-card bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
                      <p className="text-sm text-slate-400 mb-1">Current Units</p>
                      <p className="metric-number text-3xl font-bold text-slate-300">
                        {Math.round(result.current_units)}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">Estimated Consumption</p>
                    </div>

                    <div className="stat-card bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
                      <p className="text-sm text-slate-400 mb-1">Target Units</p>
                      <p className="metric-number text-3xl font-bold text-amber-500">
                        {Math.round(result.target_units)}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">Estimated Post-Solar</p>
                    </div>
                  </div>

                  {/* SUMMARY INFO */}
                  <div className="p-6 bg-blue-500/10 border border-blue-500/20 rounded-2xl">
                    <div className="flex items-start gap-4">
                      <span className="text-2xl">💡</span>
                      <p className="text-sm text-blue-300 leading-relaxed">
                        By installing a <span className="text-white font-bold">{result.recommended_solar_kw} kW</span> system, 
                        you can reduce your monthly consumption from <span className="text-white">{Math.round(result.current_units)}</span> to 
                        <span className="text-white"> {Math.round(result.target_units)} units</span>, achieving your target bill of 
                        <span className="text-white font-bold"> ₹{form.target_bill}</span>.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default BillOptimizationPage;
