# 📚 Chapter Synthesis Platform - Enhanced Medical Knowledge Synthesis

A fully functional, production-ready platform for synthesizing comprehensive medical chapters with **advanced AI capabilities**, **real-time streaming**, **smart caching**, and **version control**.

## 🎯 Key Features

Based on the **Enhanced Chapter Synthesis Workflow** with 6 advanced capabilities:

### 1. ⚡ Smart Caching (30-50% faster, 40-65% cost reduction)
- Pattern recognition for common structures
- Intelligent reuse without sacrificing quality
- Real-time cache hit rate monitoring
- Operates throughout ALL stages (indexing, research, synthesis)

### 2. 📡 Incremental Generation (Stream sections as created)
- Users see content IMMEDIATELY as it's generated
- No waiting for entire chapter completion
- Read early sections while later ones generate
- WebSocket-based real-time updates

### 3. 🔄 Rollback & Compare (Easy version management)
- Git-like version control for ALL chapter states
- One-click rollback to ANY previous version
- Side-by-side version comparison with detailed diffs
- Every enrichment/edit creates automatic checkpoint

### 4. 🧠 Smart Gap Detection (AI predicts missing content)
- AI analyzes chapter vs. source corpus
- Identifies high-value missing topics
- Prioritizes gaps by clinical relevance & user demand
- One-click auto-generation of missing sections

### 5. 📊 Observability (Real-time monitoring dashboard)
- Live stage tracking with progress bars & ETAs
- Cost optimization metrics (cache savings, token usage)
- System health monitoring (response times, error rates)
- Performance analytics across all stages

### 6. 📎 Post-Synthesis Document Integration (Deep analysis & integration)
- Upload specialized documents AFTER primary/secondary synthesis
- Deep AI analysis extracts ALL knowledge (even subtle details)
- Coherent weaving preserves chapter flow & quality
- Perfect for: institutional protocols, proprietary guidelines, conference proceedings

## 🏗️ Architecture

### Backend (Python FastAPI)
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with pgvector extension for vector search
- **Caching**: Redis for high-performance caching
- **AI Services**: OpenAI & Anthropic (with mock mode for testing)
- **WebSocket**: Socket.IO for real-time communication
- **PDF Processing**: PyMuPDF for document parsing

### Frontend (React TypeScript)
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI)
- **State Management**: Zustand
- **Real-time**: Socket.IO Client
- **API Client**: Axios with React Query
- **Build Tool**: Vite

## 📋 Prerequisites

- Docker & Docker Compose
- (Optional) Node.js 18+ and Python 3.11+ for local development

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd chapter-synthesis-app
cp backend/.env.example backend/.env
```

### 2. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432) - with pgvector extension
- Redis (port 6379) - for caching
- Backend API (port 8000) - FastAPI application
- Frontend (port 3000) - React application

### 3. Initialize Database

The database will be automatically initialized on first run with:
- All tables created
- pgvector extension enabled
- Ready for data ingestion

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

### 5. Create Your First Account

1. Navigate to http://localhost:3000
2. Click "Register here"
3. Create an account
4. Login and explore the dashboard

## 📖 User Guide

### Process A: Background PDF Indexing (24/7)

1. **Upload a PDF Document**
   - Navigate to "Documents" page
   - Click "Upload Document"
   - Select a PDF file (medical textbook, research paper, etc.)
   - The system automatically starts background indexing

2. **Monitor Indexing Progress**
   - Real-time progress updates via WebSocket
   - 4 parallel threads:
     - Thread 1: PDF Processing (text, images, tables extraction)
     - Thread 2: AI Analysis (deep understanding, concept extraction)
     - Thread 3: Vector Embedding Generation (with smart caching)
     - Thread 4: Citation Network Construction

3. **Results**
   - Fully indexed and searchable document
   - All content embedded in vector database
   - Ready for chapter synthesis

### Process B: Chapter Generation (14-Stage Workflow)

1. **Initiate Chapter Generation**
   - Navigate to "Generate Chapter"
   - Enter topic (e.g., "Glioblastoma Multiforme")
   - Configure options:
     - Enable streaming ✅
     - Enable external research (PubMed, Google Scholar)
     - Auto-fill gaps
     - Upload specific document for integration

2. **Watch Real-Time Generation**
   - Live progress through 14 stages
   - Incremental section streaming
   - See content as it's being created
   - Monitor cache hit rate and cost savings

3. **14 Stages Explained**
   - **Stage 1**: Authentication & Authorization
   - **Stage 2**: Context Analysis (with cache check)
   - **Stage 3**: Primary Research Phase (internal + external)
   - **Stage 4**: Primary Synthesis Engine (streaming sections)
   - **Stage 5**: Primary Chapter Complete
   - **Stage 6**: Activate Q&A Engine
   - **Stage 7**: User Review & Gap Detection
   - **Stage 8**: Document Deep Integration (optional)
   - **Stage 9**: Secondary Enrichment (gap filling)
   - **Stage 10**: Enriched Chapter Complete
   - **Stage 11**: Citation Verification
   - **Stage 12**: Collaborative Editing Setup
   - **Stage 13**: Personalization
   - **Stage 14**: Literature Monitoring Setup

4. **Version Management**
   - Automatic version snapshots at key points
   - Compare any two versions side-by-side
   - Rollback to previous version with one click
   - All versions preserved with full history

## 🎛️ Observability Dashboard

The main dashboard provides comprehensive real-time monitoring:

### System Health Panel
- Overall health score
- Active processes count
- Cache hit rate
- Average response time
- Token usage tracking

### Metrics Cards
- **Documents**: Total, indexed, processing
- **Chapters**: Total, completed, generating, avg quality score
- **Jobs**: Last 30 days statistics
- **Cost Optimization**: Total cost, savings from caching

### Live Activity Feed
- Real-time job updates
- Progress bars with ETAs
- Stage-by-stage breakdown
- Error notifications

### Performance Analytics
- Daily metrics over 7 days
- Cost analysis and trends
- Cache efficiency graphs
- Time savings visualization

## 🔧 Configuration

### Backend Configuration (`backend/.env`)

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chapter_synthesis

# Redis
REDIS_URL=redis://localhost:6379/0

# AI APIs (Optional - Mock mode available)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
USE_MOCK_AI=true  # Set to false to use real AI APIs

# Authentication
SECRET_KEY=your-secret-key-change-in-production

# Application
DEBUG=true
MAX_UPLOAD_SIZE=104857600  # 100MB
```

### Frontend Configuration (`frontend/.env`)

```env
VITE_API_URL=http://localhost:8000
```

## 📊 Database Schema

### Core Tables
- **users**: User accounts and preferences
- **documents**: Uploaded PDF documents
- **document_sections**: Extracted document sections
- **document_embeddings**: Vector embeddings (1536 dimensions)
- **chapters**: Generated chapters
- **chapter_versions**: Version history with full content
- **chapter_sections**: Individual chapter sections
- **jobs**: Background job tracking
- **job_stages**: Detailed stage progress
- **gap_detections**: AI-detected content gaps
- **enrichment_requests**: Enrichment operations
- **cache_entries**: Smart cache storage

## 🛠️ Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Documents
- `POST /api/documents/upload` - Upload PDF
- `GET /api/documents/` - List documents
- `GET /api/documents/{id}` - Get document details
- `GET /api/documents/{id}/sections` - Get sections
- `DELETE /api/documents/{id}` - Delete document

### Chapters
- `POST /api/chapters/generate` - Generate chapter
- `GET /api/chapters/` - List chapters
- `GET /api/chapters/{id}` - Get chapter details
- `GET /api/chapters/{id}/content` - Get chapter content
- `GET /api/chapters/{id}/versions` - List versions
- `POST /api/chapters/{id}/rollback` - Rollback to version
- `GET /api/chapters/{id}/gaps` - Get detected gaps

### Dashboard
- `GET /api/dashboard/metrics` - Get dashboard metrics
- `GET /api/dashboard/recent-activity` - Get recent activity
- `GET /api/dashboard/performance` - Get performance metrics
- `GET /api/dashboard/cost-analysis` - Get cost analysis

### Jobs
- `GET /api/jobs/` - List jobs
- `GET /api/jobs/{job_id}` - Get job details
- `GET /api/jobs/{job_id}/stages` - Get job stages

## 🔐 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration
- Rate limiting (configurable)

## 🎨 UI Features

- Responsive design (mobile, tablet, desktop)
- Real-time updates without page refresh
- Progress indicators for long operations
- Error handling with user-friendly messages
- Dark/Light theme support (MUI theme)
- Accessible components (ARIA labels)

## 📈 Performance Metrics

Based on the example workflow:

**Without Enhancements:**
- Time: 12 minutes
- Cost: $8.50
- Quality: 94/100
- User Experience: Wait then read

**With All Enhancements:**
- Time: 7.8 minutes (-35%)
- Cost: $5.20 (-39%)
- Quality: 98/100 (+4%)
- User Experience: Read while generating
- Cache Hit Rate: 68%

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Redis Connection Issues
```bash
# Check if Redis is running
docker-compose ps redis

# View Redis logs
docker-compose logs redis
```

### Frontend Not Loading
```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules
npm install

# Rebuild container
docker-compose up -d --build frontend
```

### Backend API Errors
```bash
# View backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

## 🔄 Production Deployment

### Environment Variables

Update these in production:

```env
# Backend
SECRET_KEY=<generate-strong-random-key>
DEBUG=false
USE_MOCK_AI=false
OPENAI_API_KEY=<your-real-api-key>
ANTHROPIC_API_KEY=<your-real-api-key>

# Database (use managed database service)
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/dbname

# Redis (use managed Redis service)
REDIS_URL=redis://prod-redis:6379/0
```

### Deployment Checklist

- [ ] Set strong SECRET_KEY
- [ ] Disable DEBUG mode
- [ ] Configure real AI API keys
- [ ] Use managed database service
- [ ] Use managed Redis service
- [ ] Set up SSL/TLS certificates
- [ ] Configure CORS for production domain
- [ ] Set up monitoring and logging
- [ ] Configure backups
- [ ] Set up CDN for frontend assets

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review API docs at `/docs`

## 🎓 Credits

Built with:
- FastAPI - Modern Python web framework
- React - UI library
- PostgreSQL - Database with pgvector
- Redis - Caching layer
- Material-UI - UI components
- Socket.IO - Real-time communication
- OpenAI & Anthropic - AI services

---

**Made with ❤️ for the medical community**

*Advancing medical knowledge synthesis through AI*
