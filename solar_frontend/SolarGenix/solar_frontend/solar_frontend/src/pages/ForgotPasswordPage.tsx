import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { sendOtp, resetPasswordOtp } from "../api/authApi";

const ForgotPasswordPage = () => {
    const [step, setStep] = useState<1 | 2>(1);
    const [email, setEmail] = useState("");
    const [otp, setOtp] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [loading, setLoading] = useState(false);

    // UI state
    const [message, setMessage] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const navigate = useNavigate();

    const handleSendOtp = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            await sendOtp(email);
            setMessage("An OTP has been sent to your registered phone number.");
            setStep(2);
        } catch (err: any) {
            setError(err.response?.data?.message || err.response?.data?.detail || "Failed to send OTP. Check your email.");
        }
        setLoading(false);
    };

    const handleResetPassword = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setMessage(null);

        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            setLoading(false);
            return;
        }

        try {
            await resetPasswordOtp({
                email,
                otp,
                password,
                confirm_password: confirmPassword
            });
            setMessage("Password reset successfully! Redirecting to login...");
            setTimeout(() => navigate("login"), 3000);
        } catch (err: any) {
            // Detailed error extraction based on DRF return format
            let errStr = "Failed to reset password. Please check your data.";
            const resData = err.response?.data;
            if (resData) {
                if (typeof resData === 'string') {
                    errStr = resData;
                } else if (resData.message) {
                    errStr = resData.message;
                } else if (resData.password) {
                    errStr = resData.password[0] || resData.password;
                } else if (resData.detail) {
                    errStr = resData.detail;
                }
            }
            setError(String(errStr).replace('__custom', ''));
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 relative overflow-hidden">
            <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
        
        .forgot-password-card {
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
          border-color: rgba(251, 191, 36, 0.5);
          box-shadow: 0 0 0 2px rgba(251, 191, 36, 0.1);
        }
        
        .gradient-text {
          background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #fbbf24 100%);
          background-size: 200% auto;
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .bg-pattern {
          background-image: radial-gradient(circle at 2px 2px, rgba(251, 191, 36, 0.15) 1px, transparent 0);
          background-size: 32px 32px;
        }
      `}</style>

            {/* Background elements */}
            <div className="absolute inset-0 bg-pattern opacity-30"></div>
            <div className="absolute -top-40 -right-40 w-96 h-96 bg-amber-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-20 animate-pulse"></div>
            <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-orange-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-20"></div>

            <div className="forgot-password-card w-full max-w-md p-10 rounded-3xl relative z-10 transition-all duration-500 hover:border-amber-400/30">
                <div className="text-center mb-10">
                    <div className="text-5xl mb-4">🔐</div>
                    <h1 className="text-4xl font-black text-white mb-2">
                        Reset <span className="gradient-text">Password</span>
                    </h1>
                    <p className="text-slate-400">
                        {step === 1 ? "Enter your email to receive an OTP." : "Enter the OTP sent to your phone and choose a new password."}
                    </p>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm text-center">
                        {error}
                    </div>
                )}
                {message && (
                    <div className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 text-sm text-center">
                        {message}
                    </div>
                )}

                {step === 1 ? (
                    <form onSubmit={handleSendOtp} className="space-y-6">
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

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 font-bold py-4 rounded-xl transition-all hover:scale-[1.02] hover:shadow-lg hover:shadow-amber-500/20 active:scale-[0.98] disabled:opacity-50"
                        >
                            {loading ? "Sending..." : "Send OTP"}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleResetPassword} className="space-y-5">
                        <div className="text-sm text-slate-400 mb-2 bg-slate-900/50 p-3 rounded-lg flex justify-between items-center border border-slate-800">
                            <span>Email: <strong className="text-white">{email}</strong></span>
                            <button type="button" onClick={() => setStep(1)} className="text-amber-500 hover:text-amber-400 text-xs font-semibold">
                                Edit
                            </button>
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-slate-300 mb-2">4-Digit OTP</label>
                            <input
                                type="text"
                                required
                                maxLength={6}
                                value={otp}
                                onChange={(e) => setOtp(e.target.value.replace(/[^0-9]/g, ''))}
                                placeholder="e.g. 1234"
                                className="input-field w-full p-4 rounded-xl placeholder:text-slate-600 tracking-widest text-center text-xl font-mono"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-slate-300 mb-2">New Password</label>
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                className="input-field w-full p-4 rounded-xl placeholder:text-slate-600"
                            />
                            <p className="text-xs text-slate-500 mt-2">
                                Must be at least 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char.
                            </p>
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-slate-300 mb-2">Confirm Password</label>
                            <input
                                type="password"
                                required
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                placeholder="••••••••"
                                className="input-field w-full p-4 rounded-xl placeholder:text-slate-600"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold py-4 rounded-xl transition-all hover:scale-[1.02] hover:shadow-lg hover:shadow-emerald-500/20 active:scale-[0.98] disabled:opacity-50 mt-4"
                        >
                            {loading ? "Resetting..." : "Reset Password"}
                        </button>
                    </form>
                )}

                <div className="mt-8 text-center">
                    <Link to="/login" className="text-slate-400 text-sm hover:text-white transition-colors">
                        ← Back to Login
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default ForgotPasswordPage;
