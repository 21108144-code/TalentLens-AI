import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    Upload,
    Briefcase,
    Target,
    Lightbulb,
    Sparkles
} from 'lucide-react';
import clsx from 'clsx';

const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/upload', icon: Upload, label: 'Upload Resume' },
    { path: '/jobs', icon: Briefcase, label: 'Browse Jobs' },
    { path: '/matches', icon: Target, label: 'Match Results' },
    { path: '/recommendations', icon: Lightbulb, label: 'Recommendations' },
];

function Sidebar() {
    return (
        <aside className="fixed left-0 top-0 bottom-0 w-64 bg-dark-900 border-r border-white/5
                      hidden lg:flex flex-col z-50">
            {/* Logo */}
            <div className="p-6 border-b border-white/5">
                <a href="/" className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-500 rounded-xl
                          flex items-center justify-center shadow-lg shadow-primary-500/25">
                        <Sparkles className="w-5 h-5" />
                    </div>
                    <div>
                        <span className="text-lg font-bold font-display">TalentLens</span>
                        <span className="text-xs text-primary-400 block -mt-1">AI</span>
                    </div>
                </a>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => clsx(
                            'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
                            isActive
                                ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                                : 'text-dark-300 hover:bg-dark-800 hover:text-white'
                        )}
                    >
                        <item.icon className="w-5 h-5" />
                        <span className="font-medium">{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            {/* Bottom Section */}
            <div className="p-4 border-t border-white/5">
                <div className="bg-gradient-to-br from-primary-500/20 to-purple-500/20 rounded-xl p-4
                        border border-primary-500/20">
                    <p className="text-sm font-medium mb-2">Need Help?</p>
                    <p className="text-xs text-dark-400 mb-3">
                        Learn how to maximize your job matches.
                    </p>
                    <button className="w-full py-2 bg-primary-500/20 hover:bg-primary-500/30 
                             rounded-lg text-sm font-medium text-primary-400 transition-colors">
                        View Guide
                    </button>
                </div>
            </div>
        </aside>
    );
}

export default Sidebar;
