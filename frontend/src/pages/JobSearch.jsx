import { useState, useEffect } from 'react';
import { Search, MapPin, Briefcase, DollarSign, Filter, Building, ExternalLink } from 'lucide-react';
import { jobApi } from '../services/api';

function JobSearch() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [filters, setFilters] = useState({
        location: '',
        jobType: '',
        remoteOption: ''
    });
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    useEffect(() => {
        fetchJobs();
    }, [page, filters]);

    const fetchJobs = async () => {
        setLoading(true);
        try {
            const response = await jobApi.list({
                page,
                per_page: 10,
                query: searchQuery || undefined,
                location: filters.location || undefined,
                job_type: filters.jobType || undefined,
                remote_option: filters.remoteOption || undefined
            });
            setJobs(response.data.jobs);
            setTotalPages(response.data.total_pages);
        } catch (error) {
            console.error('Failed to fetch jobs:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = (e) => {
        e.preventDefault();
        setPage(1);
        fetchJobs();
    };

    const getScoreColor = (score) => {
        if (!score) return 'text-dark-400';
        if (score >= 80) return 'score-excellent';
        if (score >= 60) return 'score-good';
        if (score >= 40) return 'score-moderate';
        return 'score-low';
    };

    return (
        <div className="max-w-6xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold font-display mb-2">Browse Jobs</h1>
                <p className="text-dark-400">
                    Explore job opportunities and find your perfect match.
                </p>
            </div>

            {/* Search & Filters */}
            <div className="card mb-6">
                <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
                    <div className="flex-1 relative">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search jobs, companies, skills..."
                            className="input pl-12"
                        />
                    </div>
                    <button type="submit" className="btn-primary">
                        Search
                    </button>
                </form>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <select
                        value={filters.location}
                        onChange={(e) => setFilters({ ...filters, location: e.target.value })}
                        className="input"
                    >
                        <option value="">All Locations</option>
                        <option value="Remote">Remote</option>
                        <option value="New York">New York</option>
                        <option value="San Francisco">San Francisco</option>
                        <option value="London">London</option>
                    </select>

                    <select
                        value={filters.jobType}
                        onChange={(e) => setFilters({ ...filters, jobType: e.target.value })}
                        className="input"
                    >
                        <option value="">All Job Types</option>
                        <option value="Full-time">Full-time</option>
                        <option value="Part-time">Part-time</option>
                        <option value="Contract">Contract</option>
                        <option value="Freelance">Freelance</option>
                    </select>

                    <select
                        value={filters.remoteOption}
                        onChange={(e) => setFilters({ ...filters, remoteOption: e.target.value })}
                        className="input"
                    >
                        <option value="">All Work Types</option>
                        <option value="Remote">Remote</option>
                        <option value="Hybrid">Hybrid</option>
                        <option value="On-site">On-site</option>
                    </select>
                </div>
            </div>

            {/* Jobs List */}
            {loading ? (
                <div className="flex justify-center py-12">
                    <div className="spinner"></div>
                </div>
            ) : jobs.length === 0 ? (
                <div className="card text-center py-12">
                    <Briefcase className="w-12 h-12 text-dark-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">No jobs found</h3>
                    <p className="text-dark-400">Try adjusting your search or filters</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {jobs.map((job) => (
                        <div
                            key={job.id}
                            className="card card-hover cursor-pointer group"
                        >
                            <div className="flex flex-col md:flex-row md:items-start gap-4">
                                {/* Company Logo Placeholder */}
                                <div className="w-12 h-12 bg-gradient-to-br from-primary-500/20 to-purple-500/20 
                                rounded-xl flex items-center justify-center flex-shrink-0">
                                    <Building className="w-6 h-6 text-primary-400" />
                                </div>

                                {/* Job Info */}
                                <div className="flex-1 min-w-0">
                                    <h3 className="text-lg font-semibold group-hover:text-primary-400 transition-colors">
                                        {job.title}
                                    </h3>
                                    <p className="text-dark-300 mb-3">{job.company}</p>

                                    <div className="flex flex-wrap gap-4 text-sm text-dark-400">
                                        {job.location && (
                                            <div className="flex items-center gap-1">
                                                <MapPin className="w-4 h-4" />
                                                {job.location}
                                            </div>
                                        )}
                                        {job.job_type && (
                                            <div className="flex items-center gap-1">
                                                <Briefcase className="w-4 h-4" />
                                                {job.job_type}
                                            </div>
                                        )}
                                        {job.salary_min && (
                                            <div className="flex items-center gap-1">
                                                <DollarSign className="w-4 h-4" />
                                                ${job.salary_min.toLocaleString()} - ${job.salary_max?.toLocaleString()}
                                            </div>
                                        )}
                                    </div>

                                    {/* Skills */}
                                    {job.skills_required && job.skills_required.length > 0 && (
                                        <div className="flex flex-wrap gap-2 mt-3">
                                            {job.skills_required.slice(0, 5).map((skill, i) => (
                                                <span
                                                    key={i}
                                                    className="px-2 py-1 bg-dark-700 rounded-lg text-xs text-dark-200"
                                                >
                                                    {skill}
                                                </span>
                                            ))}
                                            {job.skills_required.length > 5 && (
                                                <span className="px-2 py-1 text-xs text-dark-400">
                                                    +{job.skills_required.length - 5} more
                                                </span>
                                            )}
                                        </div>
                                    )}

                                    {job.apply_url && (
                                        <div className="mt-4">
                                            <a
                                                href={job.apply_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="btn-primary py-1.5 px-4 text-xs inline-flex items-center gap-2"
                                                onClick={(e) => e.stopPropagation()}
                                            >
                                                Apply Now
                                                <ExternalLink className="w-3.5 h-3.5" />
                                            </a>
                                        </div>
                                    )}
                                </div>

                                {/* Match Score */}
                                {job.match_score && (
                                    <div className="text-right">
                                        <div className={`text-2xl font-bold ${getScoreColor(job.match_score)}`}>
                                            {job.match_score}%
                                        </div>
                                        <div className="text-xs text-dark-400">Match</div>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex justify-center gap-2 mt-8">
                    <button
                        onClick={() => setPage(Math.max(1, page - 1))}
                        disabled={page === 1}
                        className="btn-secondary disabled:opacity-50"
                    >
                        Previous
                    </button>
                    <span className="px-4 py-2 text-dark-400">
                        Page {page} of {totalPages}
                    </span>
                    <button
                        onClick={() => setPage(Math.min(totalPages, page + 1))}
                        disabled={page === totalPages}
                        className="btn-secondary disabled:opacity-50"
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
}

export default JobSearch;
