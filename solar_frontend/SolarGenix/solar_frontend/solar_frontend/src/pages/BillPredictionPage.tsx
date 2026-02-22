import { useState } from "react";
import { predictElectricityBill } from "../api/predictionApi";

type TabType = "summary" | "forecast" | "details";

const BillPredictionPage = () => {
    // Get current date and calculate last 6 months
    const getMonthLabels = () => {
        const labels = [];
        const now = new Date();
        for (let i = 5; i >= 0; i--) {
            const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
            labels.push(date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }));
        }
        return labels;
    };

    const monthLabels = getMonthLabels();

    const [history, setHistory] = useState<string[]>(Array(6).fill(""));
    const [cycleIndex, setCycleIndex] = useState("1");
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState<TabType>("summary");

    const handleHistoryChange = (index: number, value: string) => {
        const updated = [...history];
        updated[index] = value;
        setHistory(updated);
    };

    const handlePredict = async () => {
        // Validate all fields are filled
        if (history.some(val => !val || val === "")) {
            alert("Please fill all 6 months of consumption data");
            return;
        }

        // Validate all are positive numbers
        if (history.some(val => Number(val) <= 0)) {
            alert("All consumption values must be greater than 0");
            return;
        }

        setLoading(true);
        try {
            const data = await predictElectricityBill({
                consumption_history: history.map(Number),
                cycle_index: Number(cycleIndex),
            });
            setResult(data);
            setActiveTab("summary");
        } catch (error) {
            console.error(error);
            alert("Prediction failed. Check backend or inputs.");
        }
        setLoading(false);
    };

    return (
        <>
            <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap');
        
        .bill-prediction-page {
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
          background: linear-gradient(135deg, #3b82f6, #8b5cf6, #3b82f6);
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
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
          border-color: #3b82f6;
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
          border: 3px solid rgba(59, 130, 246, 0.3);
          border-top-color: #3b82f6;
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
          background: linear-gradient(90deg, transparent, #3b82f6, transparent);
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
          background: #3b82f6;
          border-radius: 50%;
          opacity: 0;
          animation: floatParticle 4s ease-in-out infinite;
          box-shadow: 0 0 10px #3b82f6;
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
            linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
          background-size: 50px 50px;
        }

        .table-row {
          transition: all 0.2s;
          border-bottom: 1px solid rgba(51, 65, 85, 0.5);
        }
        
        .table-row:hover {
          background: linear-gradient(90deg, rgba(59, 130, 246, 0.05), transparent);
          transform: translateX(4px);
        }
      `}</style>

            <div className="bill-prediction-page min-h-screen bg-slate-950 relative overflow-hidden">
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
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-sm font-semibold mb-6 backdrop-blur-sm">
                            <span className="pulse-dot w-2 h-2 bg-blue-400 rounded-full"></span>
                            AI-Powered Bill Prediction
                        </div>
                        <h1 className="text-5xl md:text-6xl font-black text-white mb-4">
                            Electricity Bill <span className="bg-gradient-to-r from-blue-400 to-violet-500 bg-clip-text text-transparent">Prediction</span>
                        </h1>
                        <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                            Predict your future electricity consumption using advanced machine learning based on your historical usage patterns
                        </p>
                    </div>

                    <div className="grid lg:grid-cols-2 gap-8 items-start">
                        {/* LEFT: Input Form */}
                        <div className="gradient-border p-8">
                            <div className="mb-8">
                                <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
                                    <span className="text-3xl">📊</span>
                                    Consumption History
                                </h2>
                                <p className="text-slate-400 text-sm">Enter your last 6 months electricity usage (in kWh)</p>
                            </div>

                            <div className="space-y-6">
                                {/* 6 Month Inputs */}
                                <div className="grid grid-cols-2 gap-4">
                                    {history.map((val, i) => (
                                        <div key={i}>
                                            <label className="block text-sm font-semibold text-slate-300 mb-2">
                                                📅 {monthLabels[i]}
                                            </label>
                                            <input
                                                type="number"
                                                min="0"
                                                step="0.1"
                                                placeholder="e.g., 250"
                                                value={val}
                                                onChange={(e) => handleHistoryChange(i, e.target.value)}
                                                className="input-glow w-full bg-slate-900/50 border-2 border-slate-700 text-white p-4 rounded-xl transition-all placeholder:text-slate-500"
                                            />
                                        </div>
                                    ))}
                                </div>

                                {/* Billing Cycle Selector */}
                                <div>
                                    <label className="block text-sm font-semibold text-slate-300 mb-2">
                                        🔄 Billing Cycle to Predict
                                    </label>
                                    <select
                                        value={cycleIndex}
                                        onChange={(e) => setCycleIndex(e.target.value)}
                                        className="input-glow w-full bg-slate-900/50 border-2 border-slate-700 text-white p-4 rounded-xl transition-all cursor-pointer"
                                    >
                                        <option value="1" className="bg-slate-900">Cycle 1 (Next 2 months)</option>
                                        <option value="2" className="bg-slate-900">Cycle 2 (Months 3-4)</option>
                                        <option value="3" className="bg-slate-900">Cycle 3 (Months 5-6)</option>
                                        <option value="4" className="bg-slate-900">Cycle 4 (Months 7-8)</option>
                                        <option value="5" className="bg-slate-900">Cycle 5 (Months 9-10)</option>
                                        <option value="6" className="bg-slate-900">Cycle 6 (Months 11-12)</option>
                                    </select>
                                </div>

                                {/* Submit Button */}
                                <button
                                    onClick={handlePredict}
                                    disabled={loading}
                                    className="group relative w-full bg-gradient-to-r from-blue-500 to-violet-500 text-white font-bold text-lg py-5 rounded-xl overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/50 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02]"
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
                                    💡 <span className="font-semibold">Tip:</span> Enter accurate consumption data from your electricity bills for the most precise predictions.
                                </p>
                            </div>
                        </div>

                        {/* RIGHT: Results Section */}
                        <div className="lg:sticky lg:top-24">
                            {!result ? (
                                <div className="gradient-border p-12 text-center">
                                    <div className="text-7xl mb-6 opacity-50">💡</div>
                                    <h3 className="text-2xl font-bold text-white mb-3">No Prediction Yet</h3>
                                    <p className="text-slate-400">
                                        Fill in your consumption history and click "Generate Prediction" to see your electricity bill forecast
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
                                                        ? 'bg-blue-500/20 text-blue-400'
                                                        : 'text-slate-400 hover:text-white'
                                                    }`}
                                            >
                                                📊 Summary
                                            </button>
                                            <button
                                                onClick={() => setActiveTab('forecast')}
                                                className={`flex-1 py-3 px-4 font-semibold rounded-lg transition-all ${activeTab === 'forecast'
                                                        ? 'bg-blue-500/20 text-blue-400'
                                                        : 'text-slate-400 hover:text-white'
                                                    }`}
                                            >
                                                📈 Analysis
                                            </button>
                                            <button
                                                onClick={() => setActiveTab('details')}
                                                className={`flex-1 py-3 px-4 font-semibold rounded-lg transition-all ${activeTab === 'details'
                                                        ? 'bg-blue-500/20 text-blue-400'
                                                        : 'text-slate-400 hover:text-white'
                                                    }`}
                                            >
                                                📋 Details
                                            </button>
                                        </div>
                                    </div>

                                    {/* SUMMARY Tab */}
                                    {activeTab === 'summary' && (
                                        <div className="space-y-6">
                                            {/* Main Prediction Card */}
                                            <div className="gradient-border p-8">
                                                <div className="flex items-center justify-between mb-4">
                                                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                                        <span className="text-3xl">💰</span>
                                                        Predicted Consumption
                                                    </h3>
                                                    <div className="pulse-dot w-3 h-3 bg-blue-400 rounded-full"></div>
                                                </div>
                                                <div className="flex items-end gap-4 mb-2">
                                                    <div className="metric-number text-6xl font-bold bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
                                                        {result.predicted_next_bill_kWh}
                                                    </div>
                                                    <div className="text-slate-400 mb-3 text-xl">kWh</div>
                                                </div>
                                                <p className="text-sm text-slate-400">
                                                    For Cycle #{result.predicted_cycle} using <span className="text-blue-400 font-semibold">{result.model_used}</span> model
                                                </p>
                                                <div className="mt-4 h-2 bg-slate-800 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-gradient-to-r from-blue-500 to-violet-500 rounded-full transition-all duration-1000"
                                                        style={{ width: '85%' }}
                                                    ></div>
                                                </div>
                                            </div>

                                            {/* Stats Grid */}
                                            <div className="grid md:grid-cols-2 gap-4">
                                                <div className="stat-card bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-blue-500/30 p-6 rounded-2xl">
                                                    <div className="flex items-center justify-between mb-3">
                                                        <span className="text-3xl">📊</span>
                                                        <div className="pulse-dot w-2 h-2 bg-blue-400 rounded-full"></div>
                                                    </div>
                                                    <p className="text-sm text-slate-400 mb-1">Last Bill Usage</p>
                                                    <p className="metric-number text-3xl font-bold text-blue-400">
                                                        {result.features_used.last_bill_kWh}
                                                    </p>
                                                    <p className="text-xs text-slate-500 mt-1">kWh</p>
                                                </div>

                                                <div className="stat-card bg-gradient-to-br from-violet-500/20 to-purple-500/20 border border-violet-500/30 p-6 rounded-2xl">
                                                    <div className="flex items-center justify-between mb-3">
                                                        <span className="text-3xl">📈</span>
                                                        <div className="pulse-dot w-2 h-2 bg-violet-400 rounded-full"></div>
                                                    </div>
                                                    <p className="text-sm text-slate-400 mb-1">Avg Last 3 Bills</p>
                                                    <p className="metric-number text-3xl font-bold text-violet-400">
                                                        {result.features_used.avg_last_3_bills_kWh}
                                                    </p>
                                                    <p className="text-xs text-slate-500 mt-1">kWh</p>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* ANALYSIS Tab */}
                                    {activeTab === 'forecast' && (
                                        <div className="gradient-border p-6">
                                            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                                <span className="text-2xl">🔬</span>
                                                Model Feature Analysis
                                            </h3>
                                            <div className="grid md:grid-cols-2 gap-4">
                                                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                                                    <p className="text-xs text-slate-500 mb-1">Last Bill Usage</p>
                                                    <p className="metric-number text-lg font-semibold text-blue-400">{result.features_used.last_bill_kWh} kWh</p>
                                                </div>

                                                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                                                    <p className="text-xs text-slate-500 mb-1">Avg of Last 2 Bills</p>
                                                    <p className="metric-number text-lg font-semibold text-violet-400">{result.features_used.avg_last_2_bills_kWh} kWh</p>
                                                </div>

                                                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                                                    <p className="text-xs text-slate-500 mb-1">Avg of Last 3 Bills</p>
                                                    <p className="metric-number text-lg font-semibold text-cyan-400">{result.features_used.avg_last_3_bills_kWh} kWh</p>
                                                </div>

                                                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                                                    <p className="text-xs text-slate-500 mb-1">Std Dev (Last 3)</p>
                                                    <p className="metric-number text-lg font-semibold text-emerald-400">{result.features_used.std_last_3_bills_kWh}</p>
                                                </div>

                                                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                                                    <p className="text-xs text-slate-500 mb-1">Slope (Trend)</p>
                                                    <p className="metric-number text-lg font-semibold text-amber-400">{result.features_used.slope_last_3_bills}</p>
                                                </div>

                                                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                                                    <p className="text-xs text-slate-500 mb-1">Relative Change</p>
                                                    <p className="metric-number text-lg font-semibold text-rose-400">{result.features_used.relative_change_last_bill}</p>
                                                </div>

                                                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                                                    <p className="text-xs text-slate-500 mb-1">Cycle Sin</p>
                                                    <p className="metric-number text-lg font-semibold text-indigo-400">{result.features_used.cycle_sin}</p>
                                                </div>

                                                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                                                    <p className="text-xs text-slate-500 mb-1">Cycle Cos</p>
                                                    <p className="metric-number text-lg font-semibold text-pink-400">{result.features_used.cycle_cos}</p>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* DETAILS Tab */}
                                    {activeTab === 'details' && (
                                        <div className="gradient-border p-6">
                                            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                                <span className="text-2xl">📋</span>
                                                Consumption History Used
                                            </h3>
                                            <div className="space-y-3">
                                                {history.map((val, i) => (
                                                    <div key={i} className="table-row bg-slate-900/50 p-4 rounded-xl border border-slate-800 flex justify-between items-center">
                                                        <div className="flex items-center gap-3">
                                                            <span className="text-2xl">📅</span>
                                                            <span className="font-semibold text-white">{monthLabels[i]}</span>
                                                        </div>
                                                        <span className="metric-number text-lg font-bold text-blue-400">{val} kWh</span>
                                                    </div>
                                                ))}
                                            </div>

                                            <div className="mt-6 bg-gradient-to-br from-violet-500/10 to-purple-500/10 border border-violet-500/20 p-6 rounded-xl">
                                                <div className="flex items-start gap-3">
                                                    <span className="text-2xl">💡</span>
                                                    <div>
                                                        <h4 className="font-bold text-white mb-2">Prediction Insights</h4>
                                                        <p className="text-sm text-slate-300 leading-relaxed">
                                                            Based on your consumption pattern, the model predicts <span className="text-blue-400 font-semibold">{result.predicted_next_bill_kWh} kWh</span> for
                                                            cycle <span className="text-violet-400 font-semibold">#{result.predicted_cycle}</span> using the <span className="text-emerald-400 font-semibold">{result.model_used}</span> algorithm.
                                                        </p>
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

export default BillPredictionPage;
