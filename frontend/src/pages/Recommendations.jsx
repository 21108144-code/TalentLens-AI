import { useState, useEffect } from 'react';
import { Lightbulb, Star, MapPin, DollarSign, CheckCircle, AlertTriangle, ExternalLink } from 'lucide-react';
import { recommendationApi, resumeApi } from '../services/api';

function Recommendations() {
    const [recommendations, setRecommendations] = useState([]);
    const [resumes, setResumes] = useState([]);
    const [selectedResume, setSelectedResume] = useState(null);
    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        fetchResumes();
    }, []);

    const fetchResumes = async () => {
        try {
            const response = await resumeApi.list();
            setResumes(response.data);
            if (response.data.length > 0) {
                setSelectedResume(response.data[0].id);
            }
        } catch (error) {
            console.error('Failed to fetch resumes:', error);
        }
    };

    const generateRecommendations = async () => {
        if (!selectedResume) return;
        setGenerating(true);
        try {
            const response = await recommendationApi.generate(selectedResume, {}, 5);
            setRecommendations(response.data.recommendations);
        } catch (error) {
            console.error('Failed to generate recommendations:', error);
        } finally {
            setGenerating(false);
        }
    };

    const getScoreColor = (score) => {
        if (score >= 80) return 'text-accent-400';
        if (score >= 60) return 'text-blue-400';
        return 'text-amber-400';
    };

    return (
        <div className="max-w-6xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold font-display mb-2">Job Recommendations</h1>
                <p className="text-dark-400">AI-powered personalized job recommendations based on your profile.</p>
            </div>

            <div className="card mb-6">
                <div className="flex flex-col md:flex-row gap-4 items-end">
                    <div className="flex-1">
                        <label className="label">Select Resume</label>
                        <select
                            value={selectedResume || ''}
                            onChange={(e) => setSelectedResume(Number(e.target.value))}
                            className="input"
                        >
                            {resumes.map((resume) => (
                                <option key={resume.id} value={resume.id}>{resume.filename}</option>
                            ))}
                        </select>
                    </div>
                    <button
                        onClick={generateRecommendations}
                        disabled={generating || !selectedResume}
                        className="btn-primary"
                    >
                        {generating ? 'Generating...' : 'Generate Recommendations'}
                    </button>
                </div>
            </div>

            {recommendations.length === 0 ? (
                <div className="card text-center py-12">
                    <Lightbulb className="w-12 h-12 text-dark-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">No recommendations yet</h3>
                    <p className="text-dark-400">Select a resume and generate recommendations.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {recommendations.map((rec, i) => (
                        <div key={rec.job_id} className="card card-hover">
                            <div className="flex items-start gap-4">
                                <div className="w-10 h-10 bg-primary-500/20 rounded-xl flex items-center justify-center">
                                    <span className="font-bold text-primary-400">#{rec.rank}</span>
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-start justify-between gap-4">
                                        <div>
                                            <h3 className="text-lg font-semibold">{rec.title}</h3>
                                            <p className="text-dark-400">{rec.company}</p>
                                        </div>
                                        <div className={`text-2xl font-bold ${getScoreColor(rec.score)}`}>
                                            {Math.round(rec.score)}%
                                        </div>
                                    </div>

                                    <div className="flex flex-wrap gap-4 text-sm text-dark-400 mt-2">
                                        {rec.location && (
                                            <span className="flex items-center gap-1">
                                                <MapPin className="w-4 h-4" />{rec.location}
                                            </span>
                                        )}
                                        {rec.salary_range && (
                                            <span className="flex items-center gap-1">
                                                <DollarSign className="w-4 h-4" />{rec.salary_range}
                                            </span>
                                        )}
                                    </div>

                                    <p className="text-dark-300 text-sm mt-3">{rec.explanation}</p>

                                    {rec.skill_overlap?.length > 0 && (
                                        <div className="flex flex-wrap gap-2 mt-3">
                                            {rec.skill_overlap.slice(0, 4).map((skill, j) => (
                                                <span key={j} className="px-2 py-1 bg-accent-500/10 border border-accent-500/20 
                                                  rounded-lg text-xs text-accent-400">
                                                    {skill}
                                                </span>
                                            ))}
                                        </div>
                                    )}

                                    {rec.apply_url && (
                                        <div className="mt-4">
                                            <a
                                                href={rec.apply_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="btn-primary py-2 px-4 text-sm inline-flex items-center gap-2"
                                            >
                                                Apply Now
                                                <ExternalLink className="w-4 h-4" />
                                            </a>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default Recommendations;
