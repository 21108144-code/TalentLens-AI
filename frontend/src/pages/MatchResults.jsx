import { useState, useEffect } from 'react';
import { Target, TrendingUp, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { matchApi, resumeApi } from '../services/api';

function MatchResults() {
    const [matches, setMatches] = useState([]);
    const [resumes, setResumes] = useState([]);
    const [selectedResume, setSelectedResume] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedMatch, setSelectedMatch] = useState(null);

    useEffect(() => {
        fetchResumes();
    }, []);

    useEffect(() => {
        if (selectedResume) {
            fetchMatches();
        }
    }, [selectedResume]);

    const fetchResumes = async () => {
        try {
            const response = await resumeApi.list();
            setResumes(response.data);
            if (response.data.length > 0) {
                setSelectedResume(response.data[0].id);
            }
        } catch (error) {
            console.error('Failed to fetch resumes:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchMatches = async () => {
        if (!selectedResume) return;
        setLoading(true);
        try {
            const response = await matchApi.getForResume(selectedResume);
            setMatches(response.data.matches);
        } catch (error) {
            console.error('Failed to fetch matches:', error);
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score) => {
        if (score >= 80) return 'text-accent-400';
        if (score >= 60) return 'text-blue-400';
        if (score >= 40) return 'text-amber-400';
        return 'text-red-400';
    };

    return (
        <div className="max-w-6xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold font-display mb-2">Match Results</h1>
                <p className="text-dark-400">View detailed match scores for your resume.</p>
            </div>

            {resumes.length > 0 && (
                <div className="card mb-6">
                    <label className="label">Select Resume</label>
                    <select
                        value={selectedResume || ''}
                        onChange={(e) => setSelectedResume(Number(e.target.value))}
                        className="input max-w-md"
                    >
                        {resumes.map((resume) => (
                            <option key={resume.id} value={resume.id}>{resume.filename}</option>
                        ))}
                    </select>
                </div>
            )}

            {loading ? (
                <div className="flex justify-center py-12"><div className="spinner"></div></div>
            ) : matches.length === 0 ? (
                <div className="card text-center py-12">
                    <Target className="w-12 h-12 text-dark-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">No matches yet</h3>
                    <p className="text-dark-400">Upload a resume and browse jobs to generate match scores.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {matches.map((match) => (
                        <div key={match.id} className="card card-hover">
                            <div className="flex items-center gap-4">
                                <div className={`text-2xl font-bold ${getScoreColor(match.overall_score)}`}>
                                    {Math.round(match.overall_score)}%
                                </div>
                                <div className="flex-1">
                                    <h3 className="font-semibold">{match.job_title || 'Job'}</h3>
                                    <p className="text-dark-400 text-sm">{match.job_company || 'Company'}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default MatchResults;
