import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Menu, Bell, Search, User, LogOut } from 'lucide-react';

function Header() {
    const { user, logout } = useAuth();
    const [showDropdown, setShowDropdown] = useState(false);

    return (
        <header className="fixed top-0 right-0 left-0 lg:left-64 z-40 bg-dark-900/80 backdrop-blur-lg border-b border-white/5">
            <div className="flex items-center justify-between px-6 py-4">
                {/* Mobile Menu Button */}
                <button className="lg:hidden p-2 hover:bg-dark-800 rounded-lg transition-colors">
                    <Menu className="w-5 h-5" />
                </button>

                {/* Search */}
                <div className="hidden md:flex flex-1 max-w-md mx-4">
                    <div className="relative w-full">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
                        <input
                            type="text"
                            placeholder="Search jobs, skills..."
                            className="w-full pl-10 pr-4 py-2 bg-dark-800 border border-white/10 rounded-xl
                         focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/20
                         text-sm placeholder-dark-400 transition-all"
                        />
                    </div>
                </div>

                {/* Right Side */}
                <div className="flex items-center gap-4">
                    {/* Notifications */}
                    <button className="relative p-2 hover:bg-dark-800 rounded-lg transition-colors">
                        <Bell className="w-5 h-5" />
                        <span className="absolute top-1 right-1 w-2 h-2 bg-accent-500 rounded-full"></span>
                    </button>

                    {/* User Menu */}
                    <div className="relative">
                        <button
                            onClick={() => setShowDropdown(!showDropdown)}
                            className="flex items-center gap-3 p-2 hover:bg-dark-800 rounded-xl transition-colors"
                        >
                            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-500 rounded-lg
                              flex items-center justify-center">
                                <User className="w-4 h-4" />
                            </div>
                            <span className="hidden sm:block text-sm font-medium">
                                {user?.full_name || user?.email || 'User'}
                            </span>
                        </button>

                        {/* Dropdown */}
                        {showDropdown && (
                            <div className="absolute right-0 mt-2 w-48 bg-dark-800 border border-white/10 rounded-xl
                              shadow-xl animate-slide-down overflow-hidden">
                                <div className="px-4 py-3 border-b border-white/10">
                                    <p className="text-sm font-medium">{user?.full_name}</p>
                                    <p className="text-xs text-dark-400">{user?.email}</p>
                                </div>
                                <button
                                    onClick={() => {
                                        logout();
                                        setShowDropdown(false);
                                    }}
                                    className="w-full flex items-center gap-2 px-4 py-3 text-sm text-red-400
                             hover:bg-dark-700 transition-colors"
                                >
                                    <LogOut className="w-4 h-4" />
                                    Sign Out
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
}

export default Header;
