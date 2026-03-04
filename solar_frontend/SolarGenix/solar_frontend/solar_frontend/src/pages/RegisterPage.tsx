import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../api/authApi";

const RegisterPage = () => {
    const [formData, setFormData] = useState({
        first_name: "",
        last_name: "",
        email: "",
        password: "",
    });
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await registerUser(formData);
            alert("Registration successful! Please login.");
            navigate("/login");
        } catch (err: any) {
            alert(err.response?.data?.detail || "Registration failed. Check your details.");
        }
        setLoading(false);
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 relative overflow-hidden">
            <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
        
        .register-card {
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

            <div className="solar-glow top-[-250px] right-[-250px]"></div>
            <div className="solar-glow bottom-[-250px] left-[-250px]"></div>

            <div className="register-card w-full max-w-lg p-10 rounded-3xl relative z-10 animate-in fade-in zoom-in duration-500">
                <div className="text-center mb-10">
                    <div className="text-5xl mb-4">✨</div>
                    <h1 className="text-4xl font-black text-white mb-2">Create <span className="gradient-text">Account</span></h1>
                    <p className="text-slate-400">Join the Solar Intelligence revolution</p>
                </div>

                <form onSubmit={handleRegister} className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-semibold text-slate-300 mb-2">First Name</label>
                            <input
                                name="first_name"
                                type="text"
                                required
                                value={formData.first_name}
                                onChange={handleChange}
                                placeholder="John"
                                className="input-field w-full p-4 rounded-xl placeholder:text-slate-600"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-slate-300 mb-2">Last Name</label>
                            <input
                                name="last_name"
                                type="text"
                                required
                                value={formData.last_name}
                                onChange={handleChange}
                                placeholder="Doe"
                                className="input-field w-full p-4 rounded-xl placeholder:text-slate-600"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-slate-300 mb-2">Email Address</label>
                        <input
                            name="email"
                            type="email"
                            required
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="name@company.com"
                            className="input-field w-full p-4 rounded-xl placeholder:text-slate-600"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-slate-300 mb-2">Password</label>
                        <input
                            name="password"
                            type="password"
                            required
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="••••••••"
                            className="input-field w-full p-4 rounded-xl placeholder:text-slate-600"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 font-bold py-4 rounded-xl transition-all hover:scale-[1.02] hover:shadow-lg hover:shadow-amber-500/20 active:scale-[0.98] disabled:opacity-50"
                    >
                        {loading ? "Creating Account..." : "Register Now"}
                    </button>
                </form>

                <div className="mt-8 text-center">
                    <p className="text-slate-400 text-sm">
                        Already have an account?{" "}
                        <Link to="/login" className="text-amber-500 font-bold hover:text-amber-400 transition-colors">
                            Sign In
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default RegisterPage;
