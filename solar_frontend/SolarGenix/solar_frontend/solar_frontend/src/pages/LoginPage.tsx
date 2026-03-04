import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { loginUser } from "../api/authApi";
import { useAuth } from "../context/AuthContext";

const LoginPage = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const from = location.state?.from?.pathname || "/dashboard";

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const data = await loginUser({ email, password });
            // The auth_api returns { user, tokens: { access, refresh } }
            login(data.user, data.tokens.access);
            navigate(from, { replace: true });
        } catch (err: any) {
            alert(err.response?.data?.detail || "Login failed. Check your credentials.");
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 relative overflow-hidden">
            <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
        
        .login-card {
          font-family: 'Outfit', sans-serif;
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          background: rgba(15, 23, 42, 0.8);
          border: 1px solid rgba(251, 191, 36, 0.2);
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        
        .input-field {
          background: rgba(30, 41, 59, 0.5);
          border: 1px solid rgba(251, 191, 36, 0.1);
          color: white;
          transition: all 0.3s ease;
        }
        
        .input-field:focus {
          border-color: #fbbf24;
          box-shadow: 0 0 0 4px rgba(251, 191, 36, 0.1);
          outline: none;
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
          background: radial-gradient(circle, rgba(251, 191, 36, 0.1) 0%, transparent 70%);
          pointer-events: none;
          z-index: 0;
        }
      `}</style>

            <div className="solar-glow top-[-250px] left-[-250px]"></div>
            <div className="solar-glow bottom-[-250px] right-[-250px]"></div>

            <div className="login-card w-full max-w-md p-10 rounded-3xl relative z-10 animate-in fade-in zoom-in duration-500">
                <div className="text-center mb-10">
                    <div className="text-5xl mb-4">☀️</div>
                    <h1 className="text-4xl font-black text-white mb-2">Welcome <span className="gradient-text">Back</span></h1>
                    <p className="text-slate-400">Secure access to your Solar Intelligence</p>
                </div>

                <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                        <label className="block text-sm font-semibold text-slate-300 mb-2">Email Address</label>
                        <input
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="name@company.com"
                            className="input-field w-full p-4 rounded-xl placeholder:text-slate-600"
                        />
                    </div>

                    <div>
                        <div className="flex justify-between mb-2">
                            <label className="text-sm font-semibold text-slate-300">Password</label>
                            <a href="#" className="text-xs text-amber-500 hover:text-amber-400 transition-colors">Forgot Password?</a>
                        </div>
                        <input
                            type="password"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            className="input-field w-full p-4 rounded-xl placeholder:text-slate-600"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 font-bold py-4 rounded-xl transition-all hover:scale-[1.02] hover:shadow-lg hover:shadow-amber-500/20 active:scale-[0.98] disabled:opacity-50"
                    >
                        {loading ? "Authenticating..." : "Sign In"}
                    </button>
                </form>

                <div className="mt-8 text-center">
                    <p className="text-slate-400 text-sm">
                        Don't have an account?{" "}
                        <Link to="/register" className="text-amber-500 font-bold hover:text-amber-400 transition-colors">
                            Create Account
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
