# TalentLens AI

<div align="center">

![TalentLens AI](https://img.shields.io/badge/TalentLens-AI-blue?style=for-the-badge&logo=brain)
[![Python](https://img.shields.io/badge/Python-3.10+-green?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue?style=flat-square&logo=react)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**AI-Powered Resume Analysis & Job Matching Platform**

[Features](#features) • [Architecture](#architecture) • [Installation](#installation) • [Usage](#usage) • [API Docs](#api-documentation) • [Contributing](#contributing)

</div>

---

## 🎯 Overview

TalentLens AI is a production-ready, end-to-end AI platform that:
- **Analyzes resumes** using NLP & deep learning
- **Matches candidates to jobs** using machine learning
- **Recommends top jobs** with clear explainability
- Provides a **professional SaaS-style dashboard**

> ⚠️ **100% Free & Open Source** - No paid APIs or cloud services required.

---

## ✨ Features

### 🔍 Resume Analysis
- PDF/DOCX document parsing
- Intelligent skill extraction using NER
- Semantic understanding with transformer models

### 🎯 Job Matching
- AI-powered resume-job matching
- Multi-algorithm comparison (Logistic Regression, Random Forest, Gradient Boosting)
- Real-time match score calculation

### 💡 Smart Recommendations
- Hybrid recommendation engine
- Content-based + semantic similarity
- Personalized top-5 job recommendations

### 📊 Explainability
- Feature importance visualization
- Skill overlap analysis
- Clear textual explanations

### 🎨 Professional UI/UX
- Modern, responsive SaaS interface
- Interactive dashboard with analytics
- Mobile-friendly design

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TALENTLENS AI PLATFORM                           │
├─────────────────────────────────────────────────────────────────────────┤
│  FRONTEND (React + TailwindCSS)                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ Landing  │ │  Upload  │ │  Search  │ │  Match   │ │Dashboard │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
├─────────────────────────────────────────────────────────────────────────┤
│  BACKEND (FastAPI)                                                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────┐  │
│  │  Auth   │ │ Resume  │ │  Jobs   │ │  Match  │ │ Recommendations │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│  ML PIPELINE                                                            │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────────────────┐  │
│  │ NLP Processing │ │ Embeddings     │ │ Classification & Ranking  │  │
│  │ (spaCy, NLTK)  │ │ (MiniLM)       │ │ (Scikit-learn)            │  │
│  └────────────────┘ └────────────────┘ └────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│  DATA LAYER (SQLite/PostgreSQL + SQLAlchemy)                            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
TalentLens-AI/
├── frontend/              # React Frontend
│   └── src/
│       ├── components/    # Reusable UI components
│       ├── pages/         # Page components
│       ├── services/      # API services
│       └── context/       # React Context
├── backend/               # FastAPI Backend
│   ├── api/               # API routes
│   ├── models/            # SQLAlchemy models
│   ├── services/          # Business logic
│   ├── database/          # Database connection
│   └── schemas/           # Pydantic schemas
├── ml/                    # Machine Learning Pipeline
│   ├── preprocessing/     # Text preprocessing
│   ├── embeddings/        # Embedding generation
│   ├── training/          # Model training
│   ├── evaluation/        # Model evaluation
│   └── inference/         # Inference pipeline
├── data/                  # Datasets
├── notebooks/             # Jupyter notebooks
└── deployment/            # Docker configs
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, TailwindCSS, Recharts, Lucide Icons |
| **Backend** | FastAPI, SQLAlchemy, Pydantic, JWT Auth |
| **ML/NLP** | spaCy, NLTK, Sentence-Transformers, Scikit-learn |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Deployment** | Docker, Docker Compose |

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Clone Repository
```bash
git clone https://github.com/yourusername/TalentLens-AI.git
cd TalentLens-AI
```

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm

# Run backend
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Docker (Recommended)
```bash
docker-compose up --build
```

---

## 📖 Usage

1. **Upload Resume**: Upload your PDF/DOCX resume
2. **View Analysis**: See extracted skills and experience
3. **Browse Jobs**: Search and filter job listings
4. **Get Matches**: View AI-generated match scores
5. **Recommendations**: Get personalized job recommendations

---

## 📚 API Documentation

Once the backend is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/login` | User login |
| POST | `/api/resumes/upload` | Upload resume |
| GET | `/api/jobs` | List jobs |
| GET | `/api/matches/{resume_id}` | Get match scores |
| GET | `/api/recommendations/{resume_id}` | Get recommendations |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=backend --cov=ml
```

---

## 📊 Model Performance

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Logistic Regression | 0.85 | 0.84 | 0.86 | 0.85 |
| Random Forest | 0.88 | 0.87 | 0.89 | 0.88 |
| Gradient Boosting | **0.90** | **0.89** | **0.91** | **0.90** |

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md).

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file.



 👤 Author

Abdul Mueed Kakar
- GitHub: [@21108144-code](https://github.com/21108144-code)

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

</div>
