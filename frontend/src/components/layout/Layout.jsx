import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Header from './Header';
import Sidebar from './Sidebar';

function Layout() {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen bg-dark-900 flex items-center justify-center">
                <div className="spinner"></div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className="h-screen flex overflow-hidden bg-dark-900">
            <Sidebar />
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden lg:ml-64">
                <Header />
                <main className="flex-1 relative overflow-y-auto focus:outline-none p-6 pt-24">
                    <div className="max-w-7xl mx-auto">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    );
}

export default Layout;
