import { useState } from "react";
import { predictSolarGeneration } from "../api/predictionApi";

type TabType = "summary" | "forecast" | "details";

const SolarPredictionPage = () => {
  const [form, setForm] = useState({
    pincode: "",
    sunlight_time: "",
    panels: "",
    panel_condition: "good",
  });

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>("summary");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handlePredict = async () => {
    if (!form.pincode || !form.sunlight_time || !form.panels) {
      alert("Please fill all fields");
      return;
    }

    if (Number(form.sunlight_time) <= 0 || Number(form.panels) <= 0) {
      alert("Sunlight hours and panels must be greater than 0");
      return;
    }

    setLoading(true);
    try {
      const data = await predictSolarGeneration({
        pincode: form.pincode,
        sunlight_time: Number(form.sunlight_time),
        panels: Number(form.panels),
        panel_condition: form.panel_condition as "good" | "average" | "bad",
      });

      setResult(data);
      setActiveTab("summary");
    } catch (err) {
      console.error(err);
      alert("Prediction failed. Check backend or inputs.");
    }
    setLoading(false);
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap');
        
        .solar-prediction-page {
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
        
        .table-row {
          transition: all 0.2s;
          border-bottom: 1px solid rgba(51, 65, 85, 0.5);
        }
        
        .table-row:hover {
          background: linear-gradient(90deg, rgba(251, 191, 36, 0.05), transparent);
          transform: translateX(4px);
        }
        
        .pulse-dot {
          animation: pulse-dot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse-dot {
          0%, 100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.5;
            transform: scale(1.1);
          }
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
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
        
        .metric-number {
          font-family: 'JetBrains Mono', monospace;
          font-weight: 700;
        }
        
        .floating-particle {
          position: absolute;
          width: 6px;
          height: 6px;
          background: #fbbf24;
          border-radius: 50%;
          opacity: 0;
          animation: floatParticle 4s ease-in-out infinite;
          box-shadow: 0 0 10px #fbbf24;
        }
        
        @keyframes floatParticle {
          0%, 100% {
            opacity: 0;
            transform: translateY(0) translateX(0);
          }
          50% {
            opacity: 0.6;
          }
          100% {
            transform: translateY(-120px) translateX(30px);
          }
        }

        .grid-pattern {
          background-image: 
            linear-gradient(rgba(251, 191, 36, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(251, 191, 36, 0.03) 1px, transparent 1px);
          background-size: 50px 50px;
        }
      `}</style>

      <div className="solar-prediction-page min-h-screen bg-slate-950 relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 grid-pattern opacity-50"></div>

        {/* Floating Particles */}
        <div className="floating-particle" style={{ left: '10%', top: '20%', animationDelay: '0s' }}></div>
        <div className="floating-particle" style={{ left: '80%', top: '40%', animationDelay: '1.5s' }}></div>
        <div className="floating-particle" style={{ left: '50%', top: '60%', animationDelay: '3s' }}></div>
        <div className="floating-particle" style={{ left: '25%', top: '80%', animationDelay: '2s' }}></div>

        <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
          {/* Header Section */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-amber-500/10 border border-amber-500/20 rounded-full text-amber-400 text-sm font-semibold mb-6 backdrop-blur-sm">
              <span className="pulse-dot w-2 h-2 bg-amber-400 rounded-full"></span>
              AI-Powered Prediction
            </div>
            <h1 className="text-5xl md:text-6xl font-black text-white mb-4">
              Solar Energy <span className="bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Prediction</span>
            </h1>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Get accurate solar generation forecasts using advanced machine learning and real-time environmental data
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8 items-start">
            {/* LEFT: Input Form */}
            <div className="gradient-border p-8">
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
                  <span className="text-3xl">⚙️</span>
                  Input Parameters
                </h2>
                <p className="text-slate-400 text-sm">Enter your solar panel details for prediction</p>
              </div>

              <div className="space-y-6">
                {/* Pincode Input */}
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    📍 Location Pincode
                  </label>
                  <input
                    name="pincode"
                    placeholder="Enter your pincode"
                    onChange={handleChange}
                    value={form.pincode}
                    className="input-glow w-full bg-slate-900/50 border-2 border-slate-700 text-white p-4 rounded-xl transition-all placeholder:text-slate-500"
                  />
                </div>

                {/* Sunlight Hours */}
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    ☀️ Average Sunlight Hours (per day)
                  </label>
                  <div className="relative">
                    <input
                      name="sunlight_time"
                      type="number"
                      step="0.1"
                      min="0"
                      placeholder="e.g., 6.5"
                      onChange={handleChange}
                      value={form.sunlight_time}
                      className="input-glow w-full bg-slate-900/50 border-2 border-slate-700 text-white p-4 rounded-xl transition-all placeholder:text-slate-500"
                    />
                    <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 text-sm">hours</span>
                  </div>
                </div>

                {/* Number of Panels */}
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    🔆 Number of Solar Panels
                  </label>
                  <input
                    name="panels"
                    type="number"
                    min="1"
                    placeholder="e.g., 10"
                    onChange={handleChange}
                    value={form.panels}
                    className="input-glow w-full bg-slate-900/50 border-2 border-slate-700 text-white p-4 rounded-xl transition-all placeholder:text-slate-500"
                  />
                </div>

                {/* Panel Condition */}
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    ⚡ Panel Condition
                  </label>
                  <select
                    name="panel_condition"
                    onChange={handleChange}
                    value={form.panel_condition}
                    className="input-glow w-full bg-slate-900/50 border-2 border-slate-700 text-white p-4 rounded-xl transition-all cursor-pointer"
                  >
                    <option value="good" className="bg-slate-900">Good - Optimal Performance</option>
                    <option value="average" className="bg-slate-900">Average - Standard Performance</option>
                    <option value="bad" className="bg-slate-900">Bad - Reduced Performance</option>
                  </select>
                </div>

                {/* Submit Button */}
                <button
                  onClick={handlePredict}
                  disabled={loading}
                  className="group relative w-full bg-gradient-to-r from-amber-500 to-orange-500 text-slate-900 font-bold text-lg py-5 rounded-xl overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-amber-500/50 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02]"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-3">
                      <div className="loading-spinner"></div>
                      Analyzing Data...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      🚀 Generate Prediction
                      <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </span>
                  )}
                  <div className="energy-wave"></div>
                </button>
              </div>

              {/* Help Text */}
              <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                <p className="text-sm text-blue-300">
                  💡 <span className="font-semibold">Tip:</span> For best results, enter accurate sunlight hours based on your location and season.
                </p>
              </div>
            </div>

            {/* RIGHT: Results Section */}
            <div className="lg:sticky lg:top-24">
              {!result ? (
                <div className="gradient-border p-12 text-center">
                  <div className="text-7xl mb-6 opacity-50">📊</div>
                  <h3 className="text-2xl font-bold text-white mb-3">No Prediction Yet</h3>
                  <p className="text-slate-400">
                    Fill in the form and click "Generate Prediction" to see your solar energy forecast
                  </p>
                </div>
              ) : (
                <div className="result-card space-y-6">
                  {/* Tab Navigation */}
                  <div className="gradient-border p-2">
                    <div className="relative flex gap-2">
                      <button
                        onClick={() => setActiveTab('summary')}
                        className={`flex-1 py-3 px-4 font-semibold rounded-lg transition-all ${activeTab === 'summary'
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'text-slate-400 hover:text-white'
                          }`}
                      >
                        📊 Summary
                      </button>
                      <button
                        onClick={() => setActiveTab('forecast')}
                        className={`flex-1 py-3 px-4 font-semibold rounded-lg transition-all ${activeTab === 'forecast'
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'text-slate-400 hover:text-white'
                          }`}
                      >
                        📅 Forecast
                      </button>
                      <button
                        onClick={() => setActiveTab('details')}
                        className={`flex-1 py-3 px-4 font-semibold rounded-lg transition-all ${activeTab === 'details'
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'text-slate-400 hover:text-white'
                          }`}
                      >
                        📍 Details
                      </button>
                    </div>
                  </div>

                  {/* SUMMARY Tab */}
                  {activeTab === 'summary' && (
                    <div className="space-y-6">
                      {/* Main Stats Grid */}
                      <div className="grid md:grid-cols-3 gap-4">
                        <div className="stat-card bg-gradient-to-br from-amber-500/20 to-orange-500/20 border border-amber-500/30 p-6 rounded-2xl">
                          <div className="flex items-center justify-between mb-3">
                            <span className="text-3xl">⚡</span>
                            <div className="pulse-dot w-2 h-2 bg-amber-400 rounded-full"></div>
                          </div>
                          <p className="text-sm text-slate-400 mb-1">Total Energy (10 days)</p>
                          <p className="metric-number text-3xl font-bold text-amber-400">
                            {result.total_energy_10_days_kWh}
                          </p>
                          <p className="text-xs text-slate-500 mt-1">kWh</p>
                        </div>

                        <div className="stat-card bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 p-6 rounded-2xl">
                          <div className="flex items-center justify-between mb-3">
                            <span className="text-3xl">📈</span>
                            <div className="pulse-dot w-2 h-2 bg-emerald-400 rounded-full"></div>
                          </div>
                          <p className="text-sm text-slate-400 mb-1">Panel Efficiency</p>
                          <p className="metric-number text-3xl font-bold text-emerald-400">
                            {(result.panel_efficiency * 100).toFixed(0)}%
                          </p>
                          <p className="text-xs text-slate-500 mt-1">Performance</p>
                        </div>

                        <div className="stat-card bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-blue-500/30 p-6 rounded-2xl">
                          <div className="flex items-center justify-between mb-3">
                            <span className="text-3xl">🔆</span>
                            <div className="pulse-dot w-2 h-2 bg-blue-400 rounded-full"></div>
                          </div>
                          <p className="text-sm text-slate-400 mb-1">Active Panels</p>
                          <p className="metric-number text-3xl font-bold text-blue-400">
                            {result.number_of_panels}
                          </p>
                          <p className="text-xs text-slate-500 mt-1">Units</p>
                        </div>
                      </div>

                      {/* Average Daily Production */}
                      <div className="gradient-border p-6">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <span className="text-2xl">💡</span>
                            Average Daily Production
                          </h3>
                        </div>
                        <div className="flex items-end gap-4">
                          <div className="metric-number text-5xl font-bold text-amber-400">
                            {(result.total_energy_10_days_kWh / 10).toFixed(2)}
                          </div>
                          <div className="text-slate-400 mb-2">kWh per day</div>
                        </div>
                        <div className="mt-4 h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full transition-all duration-1000"
                            style={{ width: `${Math.min((result.panel_efficiency * 100), 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* FORECAST Tab */}
                  {activeTab === 'forecast' && result.daily_predictions && (
                    <div className="gradient-border p-6">
                      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <span className="text-2xl">📅</span>
                        10-Day Energy Forecast
                      </h3>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-slate-700">
                              <th className="text-left py-3 px-4 text-slate-400 font-semibold">Date</th>
                              <th className="text-left py-3 px-4 text-slate-400 font-semibold">Energy (kWh)</th>
                              <th className="text-left py-3 px-4 text-slate-400 font-semibold">Temperature</th>
                              <th className="text-left py-3 px-4 text-slate-400 font-semibold">Status</th>
                            </tr>
                          </thead>
                          <tbody>
                            {result.daily_predictions.map((day: any, index: number) => (
                              <tr key={index} className="table-row">
                                <td className="py-4 px-4 text-white font-medium">
                                  {new Date(day.date).toLocaleDateString('en-US', {
                                    month: 'short',
                                    day: 'numeric'
                                  })}
                                </td>
                                <td className="py-4 px-4">
                                  <span className="metric-number text-emerald-400 font-bold">
                                    {day.predicted_energy_kWh}
                                  </span>
                                </td>
                                <td className="py-4 px-4 text-slate-300">
                                  {day.ambient_temperature}°C
                                </td>
                                <td className="py-4 px-4">
                                  <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${parseFloat(day.predicted_energy_kWh) > (result.total_energy_10_days_kWh / 10)
                                    ? 'bg-emerald-500/20 text-emerald-400'
                                    : 'bg-blue-500/20 text-blue-400'
                                    }`}>
                                    {parseFloat(day.predicted_energy_kWh) > (result.total_energy_10_days_kWh / 10) ? '📈 High' : '📊 Normal'}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* DETAILS Tab */}
                  {activeTab === 'details' && (
                    <div className="gradient-border p-6">
                      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <span className="text-2xl">📍</span>
                        Location & System Details
                      </h3>
                      <div className="space-y-4">
                        <div className="grid md:grid-cols-2 gap-4">
                          <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                            <p className="text-xs text-slate-500 mb-1">Pincode</p>
                            <p className="text-lg font-semibold text-white">{result.pincode}</p>
                          </div>
                          <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                            <p className="text-xs text-slate-500 mb-1">Coordinates</p>
                            <p className="text-lg font-semibold text-white">
                              {result.latitude}, {result.longitude}
                            </p>
                          </div>
                          <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                            <p className="text-xs text-slate-500 mb-1">Sunlight Hours</p>
                            <p className="text-lg font-semibold text-amber-400">{result.sunlight_time_hours} hrs/day</p>
                          </div>
                          <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                            <p className="text-xs text-slate-500 mb-1">Panel Condition</p>
                            <p className="text-lg font-semibold text-white capitalize">{result.panel_condition}</p>
                          </div>
                        </div>

                        <div className="bg-gradient-to-br from-violet-500/10 to-purple-500/10 border border-violet-500/20 p-6 rounded-xl">
                          <div className="flex items-start gap-3">
                            <span className="text-2xl">💡</span>
                            <div>
                              <h4 className="font-bold text-white mb-2">System Performance</h4>
                              <p className="text-sm text-slate-300 leading-relaxed">
                                Your solar panel system is operating at <span className="text-emerald-400 font-semibold">{(result.panel_efficiency * 100).toFixed(0)}%</span> efficiency
                                with <span className="text-blue-400 font-semibold">{result.number_of_panels} panels</span>,
                                generating approximately <span className="text-amber-400 font-semibold">{(result.total_energy_10_days_kWh / 10).toFixed(2)} kWh</span> per day.
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default SolarPredictionPage;