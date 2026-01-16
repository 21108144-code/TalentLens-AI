import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { FileText, Target, TrendingUp, Zap, Award, ArrowUpRight } from 'lucide-react';
import { resumeApi, matchApi } from '../services/api';

function Dashboard() {
    const [stats, setStats] = useState({ resumes: 0, matches: 0, avgScore: 0, topMatch: 0 });
    const [resumes, setResumes] = useState([]);
    const [skillData, setSkillData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const resumeRes = await resumeApi.list();
            const resumeList = resumeRes.data;
            setResumes(resumeList);

            let totalMatches = 0;
            let totalScore = 0;
            let maxScore = 0;
            const skillCounts = {};

            if (resumeList.length > 0) {
                // Fetch matches for the most recent resume to show on dashboard
                try {
                    const matchRes = await matchApi.getForResume(resumeList[0].id);
                    const matches = matchRes.data.matches || [];
                    totalMatches = matches.length;

                    if (totalMatches > 0) {
                        totalScore = matches.reduce((acc, m) => acc + m.overall_score, 0);
                        maxScore = Math.max(...matches.map(m => m.overall_score));
                    }
                } catch (e) {
                    console.error('Failed to fetch matches:', e);
                }

                // Aggregate skills across all resumes
                resumeList.forEach(r => {
                    const skills = r.skills || [];
                    skills.forEach(s => {
                        skillCounts[s] = (skillCounts[s] || 0) + 1;
                    });
                });
            }

            // Convert skill counts to chart data
            const formattedSkills = Object.entries(skillCounts)
                .map(([name, count]) => ({ name, value: count * 20 })) // Scale for visualization
                .sort((a, b) => b.value - a.value)
                .slice(0, 5);

            setSkillData(formattedSkills.length > 0 ? formattedSkills : [
                { name: 'Python', value: 0 },
                { name: 'React', value: 0 },
                { name: 'ML', value: 0 },
                { name: 'SQL', value: 0 },
                { name: 'AWS', value: 0 },
            ]);

            setStats({
                resumes: resumeList.length,
                matches: totalMatches,
                avgScore: totalMatches > 0 ? Math.round(totalScore / totalMatches) : 0,
                topMatch: Math.round(maxScore)
            });
        } catch (error) {
            console.error('Failed to fetch data:', error);
        } finally {
            setLoading(false);
        }
    };

    const COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#c084fc', '#d8b4fe'];

    return (
        <div className="max-w-7xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold font-display mb-2">Dashboard</h1>
                <p className="text-dark-400">Overview of your job matching activity and insights.</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                {[
                    { icon: FileText, label: 'Resumes', value: stats.resumes, color: 'from-blue-500 to-cyan-500' },
                    { icon: Target, label: 'Matches', value: stats.matches, color: 'from-purple-500 to-pink-500' },
                    { icon: TrendingUp, label: 'Avg Score', value: `${stats.avgScore}%`, color: 'from-accent-500 to-emerald-500' },
                    { icon: Award, label: 'Top Match', value: `${stats.topMatch}%`, color: 'from-amber-500 to-orange-500' },
                ].map((stat, i) => (
                    <div key={i} className="card">
                        <div className="flex items-center gap-4">
                            <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl 
                              flex items-center justify-center`}>
                                <stat.icon className="w-6 h-6" />
                            </div>
                            <div>
                                <p className="text-dark-400 text-sm">{stat.label}</p>
                                <p className="text-2xl font-bold">{stat.value}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
                {/* Skill Chart */}
                <div className="card">
                    <h3 className="font-semibold mb-4">Top Skills</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={skillData} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis type="number" domain={[0, 100]} stroke="#64748b" />
                                <YAxis dataKey="name" type="category" stroke="#64748b" width={60} />
                                <Tooltip
                                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                    labelStyle={{ color: '#f1f5f9' }}
                                />
                                <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="card">
                    <h3 className="font-semibold mb-4">Recent Activity</h3>
                    {resumes.length === 0 ? (
                        <div className="text-center py-8 text-dark-400">
                            <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                            <p>No recent activity</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {resumes.slice(0, 5).map((resume, i) => (
                                <div key={resume.id} className="flex items-center gap-3 p-3 bg-dark-700/50 rounded-xl">
                                    <div className="w-10 h-10 bg-primary-500/20 rounded-lg flex items-center justify-center">
                                        <FileText className="w-5 h-5 text-primary-400" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="font-medium truncate">{resume.filename}</p>
                                        <p className="text-xs text-dark-400">
                                            {new Date(resume.created_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <ArrowUpRight className="w-4 h-4 text-dark-400" />
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
