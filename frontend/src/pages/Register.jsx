import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sparkles, AlertCircle, CheckCircle } from 'lucide-react';

function Register() {
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);

    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (password.length < 8) {
            setError('Password must be at least 8 characters');
            return;
        }

        setLoading(true);

        try {
            await register(email, password, fullName);
            setSuccess(true);
            setTimeout(() => navigate('/login'), 2000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to register. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-dark-950 flex items-center justify-center px-6 py-12">
            {/* Background Effects */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute top-1/4 -left-1/4 w-1/2 h-1/2 bg-primary-500/10 rounded-full blur-3xl"></div>
                <div className="absolute bottom-1/4 -right-1/4 w-1/2 h-1/2 bg-purple-500/10 rounded-full blur-3xl"></div>
            </div>

            <div className="relative w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <Link to="/" className="inline-flex items-center gap-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-purple-500 rounded-xl
                            flex items-center justify-center shadow-lg shadow-primary-500/25">
                            <Sparkles className="w-6 h-6" />
                        </div>
                        <span className="text-2xl font-bold font-display">TalentLens AI</span>
                    </Link>
                </div>

                {/* Form Card */}
                <div className="glass rounded-2xl p-8">
                    <h1 className="text-2xl font-bold text-center mb-2">Create Account</h1>
                    <p className="text-dark-400 text-center mb-8">Start your job matching journey</p>

                    {error && (
                        <div className="flex items-center gap-2 p-4 bg-red-500/10 border border-red-500/20 
                            rounded-xl text-red-400 text-sm mb-6">
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            {error}
                        </div>
                    )}

                    {success && (
                        <div className="flex items-center gap-2 p-4 bg-accent-500/10 border border-accent-500/20 
                            rounded-xl text-accent-400 text-sm mb-6">
                            <CheckCircle className="w-5 h-5 flex-shrink-0" />
                            Account created! Redirecting to login...
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label className="label">Full Name</label>
                            <input
                                type="text"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                className="input"
                                placeholder="John Doe"
                                required
                            />
                        </div>

                        <div>
                            <label className="label">Email Address</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="input"
                                placeholder="you@example.com"
                                required
                            />
                        </div>

                        <div>
                            <label className="label">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="input"
                                placeholder="Min. 8 characters"
                                required
                            />
                        </div>

                        <div>
                            <label className="label">Confirm Password</label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                className="input"
                                placeholder="••••••••"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading || success}
                            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                    Creating account...
                                </span>
                            ) : (
                                'Create Account'
                            )}
                        </button>
                    </form>

                    <p className="text-center text-dark-400 mt-6">
                        Already have an account?{' '}
                        <Link to="/login" className="text-primary-400 hover:text-primary-300 transition-colors">
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Register;
