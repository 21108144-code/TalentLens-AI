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
        <div className="min-h-screen bg-dark-900">
            <Sidebar />
            <div className="lg:ml-64">
                <Header />
                <main className="p-6 pt-20 lg:pt-6">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}

export default Layout;
