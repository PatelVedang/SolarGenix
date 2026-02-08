const DashboardPage = () => {
  return (
    <div className="min-h-screen bg-slate-100 p-10">
      <h2 className="text-3xl font-bold mb-8 text-slate-800">📊 Dashboard</h2>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-md">
          <h3 className="text-xl font-semibold mb-2">Total Predictions</h3>
          <p className="text-3xl font-bold text-yellow-500">128</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-md">
          <h3 className="text-xl font-semibold mb-2">Avg Output</h3>
          <p className="text-3xl font-bold text-green-500">5.6 kWh</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-md">
          <h3 className="text-xl font-semibold mb-2">System Status</h3>
          <p className="text-3xl font-bold text-blue-500">Active</p>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
