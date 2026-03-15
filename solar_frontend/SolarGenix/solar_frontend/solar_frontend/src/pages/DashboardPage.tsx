const DashboardPage = () => {
  return (
    <div className="min-h-screen bg-slate-950 p-4 md:p-10 relative overflow-hidden">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
        
        .dashboard-container {
          font-family: 'Outfit', sans-serif;
        }
        
        .glass-card {
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          background: rgba(30, 41, 59, 0.4);
          border: 1px solid rgba(251, 191, 36, 0.1);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .glass-card:hover {
          transform: translateY(-4px);
          border-color: rgba(251, 191, 36, 0.3);
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
        }

        .gradient-text {
          background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .solar-glow {
          position: absolute;
          width: 500px;
          height: 500px;
          background: radial-gradient(circle, rgba(251, 191, 36, 0.05) 0%, transparent 70%);
          pointer-events: none;
          z-index: 0;
        }
      `}</style>

      <div className="solar-glow -top-64 -right-64"></div>
      <div className="solar-glow -bottom-64 -left-64"></div>

      <div className="relative z-10 max-w-7xl mx-auto dashboard-container">
        <header className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-black text-white mb-2">User <span className="gradient-text">Dashboard</span></h1>
            <p className="text-slate-400">Welcome back to your solar intelligence overview.</p>
          </div>
          <div className="flex gap-3">
             <div className="px-4 py-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-slate-300 text-sm">
                System: <span className="text-emerald-400 font-bold">Optimal 🟢</span>
             </div>
          </div>
        </header>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="glass-card p-8 rounded-3xl group">
            <div className="w-12 h-12 bg-amber-500/10 rounded-2xl flex items-center justify-center text-2xl mb-6 group-hover:scale-110 transition-transform">
              📊
            </div>
            <h3 className="text-slate-400 font-semibold mb-2 uppercase tracking-wider text-xs">Total Predictions</h3>
            <p className="text-4xl font-black text-white">128</p>
            <div className="mt-4 flex items-center gap-2 text-emerald-400 text-sm font-bold">
              <span>↑ 12%</span>
              <span className="text-slate-500 font-normal italic">vs last month</span>
            </div>
          </div>

          <div className="glass-card p-8 rounded-3xl group">
            <div className="w-12 h-12 bg-emerald-500/10 rounded-2xl flex items-center justify-center text-2xl mb-6 group-hover:scale-110 transition-transform">
              ⚡
            </div>
            <h3 className="text-slate-400 font-semibold mb-2 uppercase tracking-wider text-xs">Avg Daily Output</h3>
            <p className="text-4xl font-black text-white">5.6 <span className="text-xl font-bold text-slate-500">kWh</span></p>
            <div className="mt-4 flex items-center gap-2 text-amber-400 text-sm font-bold">
              <span>★ High</span>
              <span className="text-slate-500 font-normal italic">Efficiency</span>
            </div>
          </div>

          <div className="glass-card p-8 rounded-3xl group sm:col-span-2 lg:col-span-1">
            <div className="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center text-2xl mb-6 group-hover:scale-110 transition-transform">
              🛡️
            </div>
            <h3 className="text-slate-400 font-semibold mb-2 uppercase tracking-wider text-xs">System Health</h3>
            <p className="text-4xl font-black text-white">Active</p>
            <div className="mt-4 flex items-center gap-2 text-emerald-400 text-sm font-bold">
              <span>✓ All clear</span>
              <span className="text-slate-500 font-normal italic">No alerts</span>
            </div>
          </div>
        </div>

        {/* Placeholder for more content */}
        <div className="mt-10 grid grid-cols-1 lg:grid-cols-2 gap-8 text-white">
            <div className="glass-card p-6 rounded-3xl min-h-[300px] flex items-center justify-center border-dashed border-2 border-slate-800 bg-transparent">
                <p className="text-slate-600 font-medium italic">Production History Chart (Coming Soon)</p>
            </div>
            <div className="glass-card p-6 rounded-3xl min-h-[300px] flex items-center justify-center border-dashed border-2 border-slate-800 bg-transparent">
                <p className="text-slate-600 font-medium italic">Recent Activity Log (Coming Soon)</p>
            </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
