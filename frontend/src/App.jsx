import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/layout/Layout';
import LandingPage from './pages/LandingPage';
import ResumeUpload from './pages/ResumeUpload';
import JobSearch from './pages/JobSearch';
import MatchResults from './pages/MatchResults';
import Recommendations from './pages/Recommendations';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    {/* Public Routes */}
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />

                    {/* Protected Routes */}
                    <Route element={<Layout />}>
                        <Route path="/upload" element={<ResumeUpload />} />
                        <Route path="/jobs" element={<JobSearch />} />
                        <Route path="/matches" element={<MatchResults />} />
                        <Route path="/recommendations" element={<Recommendations />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                    </Route>
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;
