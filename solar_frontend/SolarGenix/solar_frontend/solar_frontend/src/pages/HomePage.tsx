import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const HomePage = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isVisible, setIsVisible] = useState({});

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  useEffect(() => {
    const observers = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible((prev) => ({ ...prev, [entry.target.id]: true }));
          }
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll('[data-animate]').forEach((el) => {
      observers.observe(el);
    });

    return () => observers.disconnect();
  }, []);

  const features = [
    {
      icon: "🌞",
      title: "Solar Generation Prediction",
      description: "AI-powered forecasting of solar panel output based on weather patterns and environmental data",
      color: "from-amber-500 to-orange-500"
    },
    {
      icon: "💰",
      title: "Electricity Bill Estimation",
      description: "Calculate your potential savings and predict monthly electricity costs with solar energy",
      color: "from-emerald-500 to-teal-500"
    },
  
  ];

  const stats = [
    { value: "98.5%", label: "Prediction Accuracy", icon: "🎯" },
    { value: "50K+", label: "Predictions Made", icon: "📈" },
    { value: "24/7", label: "Real-time Monitoring", icon: "⚡" },
    { value: "15+", label: "Data Parameters", icon: "🔬" }
  ];

  const howItWorks = [
    {
      step: "01",
      title: "Input Your Data",
      description: "Enter your location, panel specifications, and environmental conditions",
      icon: "📝"
    },
    {
      step: "02",
      title: "AI Analysis",
      description: "Our machine learning model processes weather data and historical patterns",
      icon: "🤖"
    },
    {
      step: "03",
      title: "Get Predictions",
      description: "Receive accurate forecasts for energy generation and cost estimates",
      icon: "📊"
    },
    {
      step: "04",
      title: "Optimize & Save",
      description: "Use insights to maximize efficiency and reduce electricity bills",
      icon: "💡"
    }
  ];

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap');
        
        .homepage-container {
          font-family: 'Outfit', sans-serif;
        }
        
        .gradient-text {
          background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #fbbf24 100%);
          background-size: 200% auto;
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: shimmer 3s linear infinite;
        }
        
        @keyframes shimmer {
          to {
            background-position: 200% center;
          }
        }
        
        .solar-orb {
          position: fixed;
          width: 600px;
          height: 600px;
          background: radial-gradient(circle, rgba(251, 191, 36, 0.15) 0%, transparent 70%);
          pointer-events: none;
          transition: all 0.3s ease;
          z-index: 0;
          filter: blur(40px);
        }
        
        .grid-pattern {
          background-image: 
            linear-gradient(rgba(251, 191, 36, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(251, 191, 36, 0.03) 1px, transparent 1px);
          background-size: 50px 50px;
        }
        
        .feature-card {
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .feature-card:hover {
          transform: translateY(-8px) scale(1.02);
        }
        
        .stat-number {
          font-family: 'JetBrains Mono', monospace;
          font-weight: 700;
        }
        
        .pulse-ring {
          animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
        
        .fade-in-up {
          animation: fadeInUp 0.8s ease-out forwards;
          opacity: 0;
        }
        
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .stagger-1 { animation-delay: 0.1s; }
        .stagger-2 { animation-delay: 0.2s; }
        .stagger-3 { animation-delay: 0.3s; }
        .stagger-4 { animation-delay: 0.4s; }
        
        .section-visible {
          animation: fadeInUp 0.8s ease-out forwards;
        }
        
        .energy-beam {
          position: absolute;
          height: 2px;
          background: linear-gradient(90deg, transparent, #fbbf24, transparent);
          animation: beam 3s linear infinite;
        }
        
        @keyframes beam {
          0% {
            left: -100%;
            width: 100%;
          }
          100% {
            left: 100%;
            width: 100%;
          }
        }
        
        .particle {
          position: absolute;
          width: 4px;
          height: 4px;
          background: #fbbf24;
          border-radius: 50%;
          animation: float 6s ease-in-out infinite;
          box-shadow: 0 0 10px #fbbf24;
        }
        
        @keyframes float {
          0%, 100% {
            transform: translateY(0) translateX(0);
            opacity: 0;
          }
          50% {
            opacity: 1;
          }
        }
        
        .glow-effect {
          box-shadow: 0 0 30px rgba(251, 191, 36, 0.3);
        }
      `}</style>

      <div className="homepage-container relative overflow-hidden bg-slate-950">
        {/* Animated cursor glow */}
        <div 
          className="solar-orb"
          style={{
            left: mousePosition.x - 300,
            top: mousePosition.y - 300,
          }}
        />

        {/* Section 1: Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center grid-pattern">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950"></div>
          
          {/* Floating particles */}
          <div className="particle" style={{ left: '10%', top: '20%', animationDelay: '0s' }}></div>
          <div className="particle" style={{ left: '80%', top: '30%', animationDelay: '2s' }}></div>
          <div className="particle" style={{ left: '60%', top: '70%', animationDelay: '4s' }}></div>
          <div className="particle" style={{ left: '30%', top: '60%', animationDelay: '3s' }}></div>
          
          <div className="relative z-10 max-w-6xl mx-auto px-6 text-center">
            <div className="fade-in-up stagger-1">
              <div className="inline-block mb-6">
                <span className="px-6 py-2 bg-amber-500/10 border border-amber-500/20 rounded-full text-amber-400 text-sm font-semibold tracking-wider uppercase backdrop-blur-sm">
                  🚀 Powered by Advanced AI
                </span>
              </div>
            </div>
            
            <h1 className="fade-in-up stagger-2 text-7xl md:text-8xl font-black mb-8 leading-tight">
              <span className="gradient-text">Solar Energy</span>
              <br />
              <span className="text-white">Prediction System</span>
            </h1>
            
            <p className="fade-in-up stagger-3 max-w-3xl mx-auto text-xl md:text-2xl text-slate-400 mb-12 leading-relaxed font-light">
              Harness the power of artificial intelligence to predict solar energy generation 
              and optimize your electricity consumption with unprecedented accuracy.
            </p>
            
            <div className="fade-in-up stagger-4 flex flex-col sm:flex-row gap-6 justify-center items-center">
              <Link 
                to="/solar-predict"
                className="group relative px-10 py-5 bg-gradient-to-r from-amber-500 to-orange-500 text-slate-900 font-bold text-lg rounded-full overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-amber-500/50 hover:scale-105"
              >
                <span className="relative z-10 flex items-center gap-3">
                  Start Predicting
                  <svg className="w-5 h-5 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-orange-500 to-amber-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </Link>
              
              <Link 
                to="/dashboard"
                className="px-10 py-5 bg-slate-800/50 backdrop-blur-sm border-2 border-slate-700 text-white font-bold text-lg rounded-full hover:bg-slate-700/50 hover:border-amber-500/50 transition-all duration-300"
              >
                View Dashboard
              </Link>
            </div>
            
            <div className="mt-20 flex justify-center gap-12 text-sm text-slate-500">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full pulse-ring"></div>
                No Installation Required
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full pulse-ring"></div>
                Real-time Processing
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-amber-500 rounded-full pulse-ring"></div>
                100% Free to Use
              </div>
            </div>
          </div>
        </section>

        {/* Section 2: Key Features */}
        <section 
          id="features" 
          data-animate
          className={`relative py-32 px-6 ${isVisible.features ? 'section-visible' : 'opacity-0'}`}
        >
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
                Powerful <span className="gradient-text">Features</span>
              </h2>
              <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                Everything you need to predict, analyze, and optimize your solar energy production
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-8">
              {features.map((feature, index) => (
                <div 
                  key={index}
                  className="feature-card group relative bg-slate-900/50 border border-slate-800 rounded-3xl p-8 hover:border-amber-500/30 overflow-hidden"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="energy-beam top-0"></div>
                  
                  <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} mb-6 text-3xl group-hover:scale-110 transition-transform`}>
                    {feature.icon}
                  </div>
                  
                  <h3 className="text-2xl font-bold text-white mb-4">
                    {feature.title}
                  </h3>
                  
                  <p className="text-slate-400 text-lg leading-relaxed">
                    {feature.description}
                  </p>
                  
                  <div className="mt-6">
                    <span className="text-amber-400 font-semibold group-hover:gap-3 flex items-center gap-2 transition-all">
                      Learn more 
                      <svg className="w-5 h-5 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                      </svg>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Section 3: Stats Counter */}
        <section 
          id="stats"
          data-animate
          className={`relative py-24 px-6 ${isVisible.stats ? 'section-visible' : 'opacity-0'}`}
        >
          <div className="max-w-7xl mx-auto">
            <div className="relative bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-amber-500/10 border border-amber-500/20 rounded-3xl p-12 backdrop-blur-xl overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-slate-900/50 to-slate-900/80"></div>
              
              <div className="relative z-10 grid grid-cols-2 md:grid-cols-4 gap-8">
                {stats.map((stat, index) => (
                  <div key={index} className="text-center group">
                    <div className="text-5xl mb-4 group-hover:scale-125 transition-transform">
                      {stat.icon}
                    </div>
                    <div className="stat-number text-4xl md:text-5xl font-bold gradient-text mb-2">
                      {stat.value}
                    </div>
                    <div className="text-slate-400 font-medium">
                      {stat.label}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Section 4: How It Works */}
        <section 
          id="how-it-works"
          data-animate
          className={`relative py-32 px-6 ${isVisible['how-it-works'] ? 'section-visible' : 'opacity-0'}`}
        >
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
                How It <span className="gradient-text">Works</span>
              </h2>
              <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                Simple, fast, and accurate solar energy predictions in four easy steps
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {howItWorks.map((item, index) => (
                <div 
                  key={index}
                  className="relative group"
                  style={{ animationDelay: `${index * 0.15}s` }}
                >
                  <div className="relative bg-slate-900/50 border border-slate-800 rounded-3xl p-8 hover:border-amber-500/30 transition-all duration-300 h-full">
                    {/* Step number */}
                    <div className="absolute -top-6 -left-6 w-16 h-16 bg-gradient-to-br from-amber-500 to-orange-500 rounded-2xl flex items-center justify-center text-2xl font-black text-slate-900 shadow-lg shadow-amber-500/50 group-hover:scale-110 transition-transform">
                      {item.step}
                    </div>
                    
                    <div className="pt-8">
                      <div className="text-5xl mb-6 group-hover:scale-110 transition-transform">
                        {item.icon}
                      </div>
                      
                      <h3 className="text-2xl font-bold text-white mb-4">
                        {item.title}
                      </h3>
                      
                      <p className="text-slate-400 leading-relaxed">
                        {item.description}
                      </p>
                    </div>
                  </div>
                  
                  {/* Connector line */}
                  {index < howItWorks.length - 1 && (
                    <div className="hidden lg:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-amber-500/50 to-transparent"></div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Section 5: Technology Stack */}
        <section 
          id="technology"
          data-animate
          className={`relative py-32 px-6 ${isVisible.technology ? 'section-visible' : 'opacity-0'}`}
        >
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
                Powered by <span className="gradient-text">Advanced AI</span>
              </h2>
              <p className="text-xl text-slate-400 max-w-3xl mx-auto">
                Our prediction system leverages cutting-edge machine learning algorithms and comprehensive data analysis
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 hover:border-blue-500/30 transition-all">
                <div className="text-4xl mb-6">🧠</div>
                <h3 className="text-2xl font-bold text-white mb-4">Machine Learning</h3>
                <p className="text-slate-400 mb-4">Neural networks trained on millions of data points for maximum accuracy</p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-sm">TensorFlow</span>
                  <span className="px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-sm">Scikit-learn</span>
                  <span className="px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-sm">PyTorch</span>
                </div>
              </div>
              
              <div className="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 hover:border-emerald-500/30 transition-all">
                <div className="text-4xl mb-6">🌦️</div>
                <h3 className="text-2xl font-bold text-white mb-4">Weather Analysis</h3>
                <p className="text-slate-400 mb-4">Real-time weather data integration for precise environmental modeling</p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-400 text-sm">Live Data</span>
                  <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-400 text-sm">15+ Parameters</span>
                  <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-400 text-sm">Historical</span>
                </div>
              </div>
              
              <div className="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 hover:border-violet-500/30 transition-all">
                <div className="text-4xl mb-6">⚡</div>
                <h3 className="text-2xl font-bold text-white mb-4">Energy Optimization</h3>
                <p className="text-slate-400 mb-4">Smart algorithms to maximize efficiency and minimize costs</p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-violet-500/10 border border-violet-500/20 rounded-full text-violet-400 text-sm">Smart Grid</span>
                  <span className="px-3 py-1 bg-violet-500/10 border border-violet-500/20 rounded-full text-violet-400 text-sm">Real-time</span>
                  <span className="px-3 py-1 bg-violet-500/10 border border-violet-500/20 rounded-full text-violet-400 text-sm">Adaptive</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 6: Data Parameters */}
        <section 
          id="parameters"
          data-animate
          className={`relative py-32 px-6 bg-slate-900/30 ${isVisible.parameters ? 'section-visible' : 'opacity-0'}`}
        >
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
                Comprehensive <span className="gradient-text">Data Analysis</span>
              </h2>
              <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                Our AI analyzes multiple environmental and technical parameters for accurate predictions
              </p>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {[
                { icon: "🌡️", label: "Temperature", color: "from-red-500 to-orange-500" },
                { icon: "💨", label: "Wind Speed", color: "from-cyan-500 to-blue-500" },
                { icon: "💧", label: "Humidity", color: "from-blue-500 to-indigo-500" },
                { icon: "🌤️", label: "Cloud Cover", color: "from-slate-400 to-slate-600" },
                { icon: "☀️", label: "Solar Radiation", color: "from-amber-500 to-yellow-500" },
                { icon: "🧭", label: "Panel Orientation", color: "from-emerald-500 to-green-500" },
                { icon: "📐", label: "Tilt Angle", color: "from-violet-500 to-purple-500" },
                { icon: "⏰", label: "Time of Day", color: "from-orange-500 to-amber-500" },
                { icon: "📅", label: "Season", color: "from-teal-500 to-cyan-500" },
                { icon: "🔆", label: "UV Index", color: "from-pink-500 to-rose-500" },
              ].map((param, index) => (
                <div 
                  key={index}
                  className="group bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-amber-500/30 transition-all text-center hover:scale-105"
                >
                  <div className={`inline-flex items-center justify-center w-16 h-16 rounded-xl bg-gradient-to-br ${param.color} mb-4 text-3xl group-hover:rotate-12 transition-transform`}>
                    {param.icon}
                  </div>
                  <div className="text-white font-semibold">{param.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Section 7: Call to Action */}
        <section className="relative py-32 px-6">
          <div className="max-w-5xl mx-auto text-center">
            <div className="relative bg-gradient-to-br from-amber-500/20 via-orange-500/20 to-amber-500/20 border border-amber-500/30 rounded-3xl p-16 backdrop-blur-xl overflow-hidden glow-effect">
              <div className="absolute inset-0 bg-gradient-to-br from-slate-900/70 to-slate-900/90"></div>
              
              {/* Animated background elements */}
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-amber-500 to-transparent opacity-50"></div>
              
              <div className="relative z-10">
                <div className="text-6xl mb-8">🚀</div>
                <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
                  Ready to <span className="gradient-text">Optimize</span> Your Solar Energy?
                </h2>
                <p className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto">
                  Start making data-driven decisions about your solar energy production today. It's completely free!
                </p>
                
                <div className="flex flex-col sm:flex-row gap-6 justify-center">
                  <Link 
                    to="/solar-predict"
                    className="group relative px-12 py-6 bg-gradient-to-r from-amber-500 to-orange-500 text-slate-900 font-black text-xl rounded-full overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-amber-500/50 hover:scale-105"
                  >
                    <span className="relative z-10 flex items-center justify-center gap-3">
                      Predict Solar Energy
                      <svg className="w-6 h-6 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </span>
                  </Link>
                  
                  <Link 
                    to="/bill-predict"
                    className="px-12 py-6 bg-slate-800/80 backdrop-blur-sm border-2 border-slate-600 text-white font-black text-xl rounded-full hover:bg-slate-700/80 hover:border-amber-500/50 transition-all duration-300"
                  >
                    Calculate Bill Savings
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="relative py-12 px-6 border-t border-slate-800">
          <div className="max-w-7xl mx-auto text-center">
            <p className="text-slate-500 text-sm">
              © 2024 SolarAI - Advanced Solar Energy Prediction System
            </p>
            <p className="text-slate-600 text-xs mt-2">
              Powered by Machine Learning & Environmental Data Analysis
            </p>
          </div>
        </footer>
      </div>
    </>
  );
};

export default HomePage;