import { Link } from 'react-router-dom';
import {
    ArrowRight,
    Upload,
    Target,
    Lightbulb,
    BarChart3,
    CheckCircle,
    Sparkles,
    Zap,
    Shield,
    Brain
} from 'lucide-react';

function LandingPage() {
    return (
        <div className="min-h-screen bg-dark-950">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 bg-dark-950/80 backdrop-blur-lg border-b border-white/5">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-500 rounded-xl
                              flex items-center justify-center shadow-lg shadow-primary-500/25">
                                <Sparkles className="w-5 h-5" />
                            </div>
                            <span className="text-xl font-bold font-display">TalentLens AI</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <Link to="/login" className="text-dark-300 hover:text-white transition-colors">
                                Sign In
                            </Link>
                            <Link to="/register" className="btn-primary">
                                Get Started
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative pt-32 pb-20 px-6 overflow-hidden">
                {/* Background Effects */}
                <div className="absolute inset-0 overflow-hidden">
                    <div className="absolute top-1/4 -left-1/4 w-1/2 h-1/2 bg-primary-500/20 rounded-full blur-3xl"></div>
                    <div className="absolute bottom-1/4 -right-1/4 w-1/2 h-1/2 bg-purple-500/20 rounded-full blur-3xl"></div>
                </div>

                <div className="relative max-w-7xl mx-auto text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500/10 border border-primary-500/20
                          rounded-full text-primary-400 text-sm mb-8 animate-fade-in">
                        <Zap className="w-4 h-4" />
                        AI-Powered Career Intelligence
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold font-display mb-6 animate-slide-up">
                        Find Your Perfect
                        <span className="gradient-text block">Job Match</span>
                    </h1>

                    <p className="text-xl text-dark-300 max-w-2xl mx-auto mb-10 animate-slide-up" style={{ animationDelay: '0.1s' }}>
                        Upload your resume and let our AI analyze your skills, experience, and potential
                        to match you with the perfect opportunities.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up" style={{ animationDelay: '0.2s' }}>
                        <Link to="/register" className="btn-primary flex items-center gap-2">
                            Start Free Analysis
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                        <a href="#features" className="btn-secondary">
                            Learn More
                        </a>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-3 gap-8 mt-20 max-w-3xl mx-auto">
                        {[
                            { value: '95%', label: 'Match Accuracy' },
                            { value: '10K+', label: 'Jobs Analyzed' },
                            { value: '50+', label: 'Skills Tracked' },
                        ].map((stat, i) => (
                            <div key={i} className="text-center animate-fade-in" style={{ animationDelay: `${0.3 + i * 0.1}s` }}>
                                <div className="text-4xl font-bold gradient-text mb-2">{stat.value}</div>
                                <div className="text-dark-400">{stat.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="py-20 px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="section-title mb-4">
                            Intelligent Career <span className="gradient-text">Matching</span>
                        </h2>
                        <p className="section-subtitle mx-auto">
                            Our AI analyzes your resume and provides personalized job recommendations
                            with clear explanations.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {[
                            {
                                icon: Upload,
                                title: 'Smart Upload',
                                description: 'Upload PDF or DOCX resumes with automatic skill extraction.',
                                color: 'from-blue-500 to-cyan-500'
                            },
                            {
                                icon: Brain,
                                title: 'AI Analysis',
                                description: 'Deep learning models analyze your experience and skills.',
                                color: 'from-purple-500 to-pink-500'
                            },
                            {
                                icon: Target,
                                title: 'Precise Matching',
                                description: 'Get match scores with detailed skill gap analysis.',
                                color: 'from-amber-500 to-orange-500'
                            },
                            {
                                icon: Lightbulb,
                                title: 'Clear Explanations',
                                description: 'Understand exactly why each job is recommended.',
                                color: 'from-accent-500 to-emerald-500'
                            },
                        ].map((feature, i) => (
                            <div
                                key={i}
                                className="card card-hover group animate-fade-in"
                                style={{ animationDelay: `${i * 0.1}s` }}
                            >
                                <div className={`w-12 h-12 bg-gradient-to-br ${feature.color} rounded-xl
                                flex items-center justify-center mb-4 shadow-lg
                                group-hover:scale-110 transition-transform duration-300`}>
                                    <feature.icon className="w-6 h-6" />
                                </div>
                                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                                <p className="text-dark-400 text-sm">{feature.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="py-20 px-6 bg-dark-900/50">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="section-title mb-4">
                            How It <span className="gradient-text">Works</span>
                        </h2>
                        <p className="section-subtitle mx-auto">
                            Three simple steps to find your perfect job match.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            {
                                step: '01',
                                title: 'Upload Resume',
                                description: 'Upload your resume in PDF or DOCX format. Our AI extracts skills and experience automatically.'
                            },
                            {
                                step: '02',
                                title: 'AI Analysis',
                                description: 'Our ML models analyze your profile and compare it with thousands of job listings.'
                            },
                            {
                                step: '03',
                                title: 'Get Matches',
                                description: 'Receive personalized job recommendations with match scores and skill gap insights.'
                            },
                        ].map((item, i) => (
                            <div key={i} className="relative">
                                <div className="text-8xl font-bold text-dark-800/50 absolute -top-6 -left-4 font-display">
                                    {item.step}
                                </div>
                                <div className="relative card">
                                    <h3 className="text-xl font-semibold mb-3">{item.title}</h3>
                                    <p className="text-dark-400">{item.description}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 px-6">
                <div className="max-w-4xl mx-auto text-center">
                    <div className="glass rounded-3xl p-12">
                        <h2 className="section-title mb-4">
                            Ready to Find Your <span className="gradient-text">Dream Job?</span>
                        </h2>
                        <p className="section-subtitle mx-auto mb-8">
                            Join thousands of professionals who have found their perfect match with TalentLens AI.
                        </p>
                        <Link to="/register" className="btn-primary inline-flex items-center gap-2">
                            Get Started Free
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-8 px-6 border-t border-white/5">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-500 rounded-lg
                            flex items-center justify-center">
                            <Sparkles className="w-4 h-4" />
                        </div>
                        <span className="font-bold font-display">TalentLens AI</span>
                    </div>
                    <p className="text-dark-400 text-sm">
                        © 2024 TalentLens AI. All rights reserved.
                    </p>
                </div>
            </footer>
        </div>
    );
}

export default LandingPage;
