# 🚀 Quick Start Guide

Get the Chapter Synthesis Platform running in **5 minutes**!

## Prerequisites

- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- 8GB RAM minimum
- 10GB free disk space

## Step 1: Start the Application

```bash
cd chapter-synthesis-app
./start.sh
```

That's it! The script will:
- ✅ Create configuration files
- ✅ Start PostgreSQL with pgvector
- ✅ Start Redis for caching
- ✅ Start the backend API
- ✅ Start the frontend

## Step 2: Create Your Account

1. Open http://localhost:3000
2. Click **"Register here"**
3. Fill in:
   - Username: `demo`
   - Email: `demo@example.com`
   - Password: `demo123`
4. Click **"Register"**

You'll be automatically logged in!

## Step 3: Explore the Dashboard

You'll see the **Observability Dashboard** with:
- 📊 System health metrics (98% health score)
- 📚 Document and chapter statistics
- 💰 Cost optimization analytics
- 🔴 Live active jobs tracking

## Step 4: Try the System

### Option A: Generate a Chapter (Fastest)

1. Click **"Generate New Chapter"** button
2. Enter topic: `Glioblastoma Multiforme`
3. Keep defaults:
   - ✅ Enable streaming
   - ✅ Auto-fill gaps
4. Click **"Generate"**
5. Watch real-time generation with streaming sections!

### Option B: Upload & Index a Document

1. Click **"Upload Document"**
2. Select a PDF file (any medical textbook or paper)
3. Watch background indexing in real-time:
   - Thread 1: PDF Processing
   - Thread 2: AI Analysis
   - Thread 3: Vector Embeddings
   - Thread 4: Citation Network

## What You'll See

### During Chapter Generation

```
🔴 LIVE - Generating Chapter: Glioblastoma Multiforme

✅ 1. INTRODUCTION                    [2,340 words]
✅ 2. EPIDEMIOLOGY & DEMOGRAPHICS     [1,890 words]
✅ 3. PATHOPHYSIOLOGY                 [3,120 words]
🔵 4. CLINICAL PRESENTATION           [Generating...]
   └─→ Subsection 4.1: Signs         [Complete ✓]
   └─→ Subsection 4.2: Neurological  [Streaming...█]

⏳ 5-12. [Additional sections]        [Queued]

Progress: ████████░░░░░░░ 42% | ETA: 4m 30s
```

### Real-Time Features

- **Incremental Streaming**: Read sections as they're created
- **Live Progress**: See exactly what stage is running
- **Cache Metrics**: Watch savings accumulate
- **Cost Tracking**: See real-time cost vs without cache

## Key Features to Try

### 1. Version Control & Rollback

1. Generate a chapter
2. Let it enrich with gaps
3. Go to chapter → "Versions"
4. Click "Compare v1.0 ⟷ v1.2"
5. See detailed diff
6. Click "Rollback to v1.0" if desired

### 2. Smart Gap Detection

1. Open any completed chapter
2. View "Detected Gaps" tab
3. See AI-identified missing content:
   - **High Priority**: Limited coverage areas
   - **Medium Priority**: Thin coverage topics
   - **Low Priority**: Optional enhancements
4. Click "Auto-Generate Section" to fill

### 3. Observability Dashboard

Watch live metrics:
- System health: 98%
- Cache hit rate: 87%
- Response time: 2.3s avg
- Active processes: Real-time
- Cost savings: Cumulative

### 4. Document Deep Integration

1. Generate a primary chapter
2. Upload a specialized document (institutional protocol, guidelines)
3. Watch deep analysis:
   - Knowledge extraction (85 units)
   - Semantic mapping (12 integration points)
   - Coherent weaving into chapter
4. New version created automatically

## Test Scenarios

### Scenario 1: Quick Chapter (3-5 minutes)
```
Topic: "Brain Tumor Classification"
Enable streaming: ✅
External research: ❌
Auto-fill gaps: ❌
Result: ~40,000 words, 50 citations, 8 sections
```

### Scenario 2: Comprehensive Chapter (7-10 minutes)
```
Topic: "Glioblastoma Multiforme"
Enable streaming: ✅
External research: ✅ (PubMed + Scholar)
Auto-fill gaps: ✅
Upload document: ✅ (institutional protocol)
Result: ~110,000 words, 155 citations, 12+ sections
```

### Scenario 3: Document Indexing (2-5 minutes)
```
Upload: Medical textbook PDF (500 pages)
Cache hit rate: 45% (if similar textbooks indexed before)
Result: Fully searchable, 670 sections, 240 embeddings
```

## Stopping the Application

```bash
docker-compose down
```

To stop and remove all data:
```bash
docker-compose down -v
```

## Troubleshooting

### Services not starting?
```bash
docker-compose logs
```

### Frontend not loading?
```bash
docker-compose restart frontend
```

### Database connection error?
```bash
docker-compose restart postgres
# Wait 10 seconds
docker-compose restart backend
```

### Need to reset everything?
```bash
docker-compose down -v
./start.sh
```

## Next Steps

1. **Read Full Documentation**: See [README.md](README.md)
2. **Explore API**: Visit http://localhost:8000/docs
3. **Check System Health**: Dashboard → System Health panel
4. **Generate Multiple Chapters**: Test different topics
5. **Upload Documents**: Build your knowledge base

## Architecture Diagram

```
┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│  Frontend   │
│ (You!)      │◀────│  (React)    │
└─────────────┘     └──────┬──────┘
                           │ HTTP + WebSocket
                    ┌──────▼──────┐
                    │   Backend   │
                    │  (FastAPI)  │
                    └──┬───┬───┬──┘
                       │   │   │
        ┌──────────────┘   │   └──────────────┐
        ▼                  ▼                   ▼
┌───────────────┐  ┌──────────────┐  ┌────────────┐
│  PostgreSQL   │  │    Redis     │  │  AI APIs   │
│  + pgvector   │  │  (Caching)   │  │ (Mock/Real)│
└───────────────┘  └──────────────┘  └────────────┘
```

## Support

- 📖 Full docs: [README.md](README.md)
- 🐛 Issues: Check logs with `docker-compose logs`
- 💬 Questions: See troubleshooting section

---

**Enjoy synthesizing medical knowledge!** 🎓✨
