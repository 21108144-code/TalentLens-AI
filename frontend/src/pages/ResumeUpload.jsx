import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, CheckCircle, AlertCircle, X } from 'lucide-react';
import { resumeApi } from '../services/api';

function ResumeUpload() {
    const [file, setFile] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadResult, setUploadResult] = useState(null);
    const [error, setError] = useState('');

    const navigate = useNavigate();

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    }, []);

    const handleFile = (selectedFile) => {
        setError('');

        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!validTypes.includes(selectedFile.type)) {
            setError('Please upload a PDF or DOCX file');
            return;
        }

        if (selectedFile.size > 10 * 1024 * 1024) {
            setError('File size must be less than 10MB');
            return;
        }

        setFile(selectedFile);
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setError('');

        try {
            const response = await resumeApi.upload(file);
            setUploadResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to upload resume. Please try again.');
        } finally {
            setUploading(false);
        }
    };

    const removeFile = () => {
        setFile(null);
        setUploadResult(null);
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold font-display mb-2">Upload Your Resume</h1>
                <p className="text-dark-400">
                    Upload your resume and our AI will extract your skills and experience automatically.
                </p>
            </div>

            {/* Success State */}
            {uploadResult && (
                <div className="card bg-accent-500/10 border-accent-500/20 mb-6 animate-scale-in">
                    <div className="flex items-start gap-4">
                        <div className="w-12 h-12 bg-accent-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
                            <CheckCircle className="w-6 h-6 text-accent-400" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold text-accent-400 mb-1">Resume Uploaded Successfully!</h3>
                            <p className="text-dark-300 mb-4">{uploadResult.message}</p>

                            <div className="flex items-center gap-6 text-sm">
                                <div>
                                    <span className="text-dark-400">File:</span>{' '}
                                    <span className="font-medium">{uploadResult.filename}</span>
                                </div>
                                <div>
                                    <span className="text-dark-400">Skills Extracted:</span>{' '}
                                    <span className="font-medium text-accent-400">{uploadResult.skills_extracted}</span>
                                </div>
                            </div>

                            <div className="flex gap-3 mt-6">
                                <button
                                    onClick={() => navigate('/recommendations')}
                                    className="btn-primary"
                                >
                                    View Recommendations
                                </button>
                                <button
                                    onClick={() => navigate('/matches')}
                                    className="btn-secondary"
                                >
                                    Browse Matches
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Error State */}
            {error && (
                <div className="flex items-center gap-2 p-4 bg-red-500/10 border border-red-500/20 
                        rounded-xl text-red-400 text-sm mb-6">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    {error}
                </div>
            )}

            {/* Upload Area */}
            {!uploadResult && (
                <div
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    className={`
            relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300
            ${dragActive
                            ? 'border-primary-500 bg-primary-500/10'
                            : 'border-white/10 hover:border-white/20 bg-dark-800/30'
                        }
            ${file ? 'border-accent-500 bg-accent-500/5' : ''}
          `}
                >
                    <input
                        type="file"
                        accept=".pdf,.docx"
                        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />

                    {file ? (
                        <div className="animate-fade-in">
                            <div className="w-16 h-16 bg-accent-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                <FileText className="w-8 h-8 text-accent-400" />
                            </div>
                            <p className="text-lg font-medium mb-1">{file.name}</p>
                            <p className="text-dark-400 text-sm mb-6">
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                            <div className="flex items-center justify-center gap-3">
                                <button
                                    onClick={(e) => {
                                        e.preventDefault();
                                        removeFile();
                                    }}
                                    className="btn-secondary flex items-center gap-2"
                                >
                                    <X className="w-4 h-4" />
                                    Remove
                                </button>
                                <button
                                    onClick={(e) => {
                                        e.preventDefault();
                                        handleUpload();
                                    }}
                                    disabled={uploading}
                                    className="btn-primary flex items-center gap-2"
                                >
                                    {uploading ? (
                                        <>
                                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                            Analyzing...
                                        </>
                                    ) : (
                                        <>
                                            <Upload className="w-5 h-5" />
                                            Upload & Analyze
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <>
                            <div className="w-16 h-16 bg-dark-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                <Upload className="w-8 h-8 text-dark-400" />
                            </div>
                            <p className="text-lg font-medium mb-1">
                                Drag and drop your resume here
                            </p>
                            <p className="text-dark-400 text-sm mb-4">
                                or click to browse files
                            </p>
                            <p className="text-dark-500 text-xs">
                                Supports PDF and DOCX (max 10MB)
                            </p>
                        </>
                    )}
                </div>
            )}

            {/* Tips Section */}
            <div className="grid md:grid-cols-3 gap-4 mt-8">
                {[
                    { title: 'Keep it Updated', desc: 'Include your latest skills and experience' },
                    { title: 'Be Specific', desc: 'List technical skills and tools you know' },
                    { title: 'Quantify Results', desc: 'Include measurable achievements' },
                ].map((tip, i) => (
                    <div key={i} className="card">
                        <h4 className="font-medium mb-1">{tip.title}</h4>
                        <p className="text-dark-400 text-sm">{tip.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ResumeUpload;
