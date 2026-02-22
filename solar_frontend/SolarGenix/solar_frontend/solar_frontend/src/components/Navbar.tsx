import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

const Navbar = () => {
    const location = useLocation();
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const navItems = [
        { path: "/", label: "Home" },
        { path: "/dashboard", label: "Dashboard" },
        { path: "/solar-predict", label: "Solar Prediction" },
        { path: "/bill-predict", label: "Bill Prediction" },
    ];

    return (
        <>
            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Space+Mono:wght@400;700&display=swap');
                
                .solar-nav {
                    font-family: 'Outfit', sans-serif;
                }
                
                .solar-glow {
                    position: absolute;
                    width: 300px;
                    height: 300px;
                    background: radial-gradient(circle, rgba(251, 191, 36, 0.15) 0%, transparent 70%);
                    pointer-events: none;
                    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                .nav-link {
                    position: relative;
                    overflow: hidden;
                }
                
                .nav-link::before {
                    content: '';
                    position: absolute;
                    bottom: -2px;
                    left: 0;
                    width: 0;
                    height: 2px;
                    background: linear-gradient(90deg, #fbbf24, #f59e0b);
                    transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                .nav-link:hover::before,
                .nav-link.active::before {
                    width: 100%;
                }
                
                .nav-link::after {
                    content: '';
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: 0;
                    height: 0;
                    border-radius: 50%;
                    background: rgba(251, 191, 36, 0.1);
                    transform: translate(-50%, -50%);
                    transition: width 0.6s, height 0.6s;
                }
                
                .nav-link:hover::after {
                    width: 200px;
                    height: 200px;
                }
                
                .logo-text {
                    font-family: 'Space Mono', monospace;
                    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #fbbf24 100%);
                    background-size: 200% auto;
                    -webkit-background-clip: text;
                    background-clip: text;
                    -webkit-text-fill-color: transparent;
                    animation: shine 3s linear infinite;
                }
                
                @keyframes shine {
                    to {
                        background-position: 200% center;
                    }
                }
                
                .sun-icon {
                    display: inline-block;
                    animation: rotate 20s linear infinite;
                    filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.6));
                }
                
                @keyframes rotate {
                    from {
                        transform: rotate(0deg);
                    }
                    to {
                        transform: rotate(360deg);
                    }
                }
                
                .energy-particle {
                    position: absolute;
                    width: 3px;
                    height: 3px;
                    background: #fbbf24;
                    border-radius: 50%;
                    animation: float 4s ease-in-out infinite;
                    opacity: 0.6;
                    box-shadow: 0 0 6px #fbbf24;
                }
                
                @keyframes float {
                    0%, 100% {
                        transform: translateY(0) translateX(0);
                        opacity: 0;
                    }
                    50% {
                        opacity: 0.6;
                    }
                    100% {
                        transform: translateY(-100px) translateX(20px);
                        opacity: 0;
                    }
                }
                
                .nav-backdrop {
                    backdrop-filter: blur(16px);
                    -webkit-backdrop-filter: blur(16px);
                }
                
                @keyframes slideDown {
                    from {
                        transform: translateY(-100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }
                
                .solar-nav {
                    animation: slideDown 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                .beam-line {
                    position: absolute;
                    height: 1px;
                    background: linear-gradient(90deg, transparent, #fbbf24, transparent);
                    bottom: 0;
                    left: 0;
                    right: 0;
                    opacity: 0.3;
                }
            `}</style>
            
            <nav className={`solar-nav fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
                scrolled 
                    ? 'bg-slate-950/95 shadow-2xl shadow-amber-500/5' 
                    : 'bg-gradient-to-b from-slate-950 to-slate-950/80'
            }`}>
                <div className="nav-backdrop">
                    <div className="max-w-7xl mx-auto px-6 lg:px-8">
                        <div className="flex justify-between items-center h-20">
                            {/* Logo Section */}
                            <Link to="/" className="flex items-center gap-3 group relative z-10">
                                <div className="relative">
                                    <span className="sun-icon text-4xl">☀️</span>
                                    {/* Energy particles */}
                                    <div className="energy-particle" style={{ left: '50%', top: '0', animationDelay: '0s' }}></div>
                                    <div className="energy-particle" style={{ left: '70%', top: '20%', animationDelay: '1s' }}></div>
                                    <div className="energy-particle" style={{ left: '30%', top: '10%', animationDelay: '2s' }}></div>
                                </div>
                                <div>
                                    <h1 className="logo-text text-3xl font-bold tracking-tight">
                                        SolarAI
                                    </h1>
                                    <p className="text-amber-400/60 text-xs font-light tracking-widest uppercase">
                                        Energy Intelligence
                                    </p>
                                </div>
                            </Link>

                            {/* Navigation Links */}
                            <div className="flex items-center gap-1">
                                {navItems.map((item, index) => {
                                    const isActive = location.pathname === item.path;
                                    return (
                                        <Link
                                            key={item.path}
                                            to={item.path}
                                            className={`nav-link px-6 py-2.5 text-sm font-medium tracking-wide transition-all duration-300 relative ${
                                                isActive 
                                                    ? 'text-amber-400 active' 
                                                    : 'text-slate-300 hover:text-amber-400'
                                            }`}
                                            style={{
                                                animationDelay: `${index * 0.1}s`
                                            }}
                                        >
                                            <span className="relative z-10">{item.label}</span>
                                        </Link>
                                    );
                                })}
                            </div>

                            {/* Optional: Action Button */}
                            <div className="hidden lg:block">
                                <button className="group relative px-6 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 text-slate-900 font-semibold text-sm rounded-full overflow-hidden transition-all duration-300 hover:shadow-lg hover:shadow-amber-500/50 hover:scale-105">
                                    <span className="relative z-10 flex items-center gap-2">
                                        Get Started
                                        <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                        </svg>
                                    </span>
                                    <div className="absolute inset-0 bg-gradient-to-r from-orange-500 to-amber-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    {/* Animated bottom border */}
                    <div className="beam-line"></div>
                </div>
            </nav>
            
            {/* Spacer to prevent content from hiding under fixed navbar */}
            <div className="h-20"></div>
        </>
    );
};

export default Navbar;