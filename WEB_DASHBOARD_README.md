# Z2 Web Dashboard

Web-based interface for the Z2 AI Knowledge Distillery Platform.

## Quick Start

### 1. Start the Backend Server

```bash
./run_web.sh
```

Or manually:
```bash
source venv/bin/activate
python -m uvicorn src.web.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Access the API

- **API Documentation**: http://localhost:8000/docs
- **API Base URL**: http://localhost:8000/api
- **WebSocket**: ws://localhost:8000/ws

## Architecture

```
┌─────────────────┐
│  React Frontend │  (TODO: Not yet implemented)
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP/REST + WebSocket
┌────────┴────────┐
│  FastAPI Backend│  ✅ COMPLETE
│  (Port 8000)    │
└────────┬────────┘
         │
┌────────┴────────┐
│  PostgreSQL     │  ✅ COMPLETE
│  (Port 5433)    │
└─────────────────┘
```

## Backend Features (Complete)

### ✅ REST API Endpoints
- `POST /api/jobs` - Submit YouTube URL for processing
- `GET /api/jobs` - List all jobs (with pagination)
- `GET /api/jobs/{uuid}` - Get job details
- `DELETE /api/jobs/{uuid}` - Cancel job
- `GET /api/stats` - Get platform statistics

### ✅ WebSocket Endpoints
- `WS /ws/jobs/status` - Real-time status updates (broadcast)
- `WS /ws/jobs/{uuid}/logs` - Real-time log streaming (per job)

### ✅ Pipeline Integration
- Async job queue (2 concurrent workers)
- Complete pipeline execution:
  1. Download video from YouTube
  2. Transcribe audio
  3. Translate to Chinese
  4. Burn subtitles
  5. Analyze content
  6. Publish to platforms (WeChat, Bilibili)
- Real-time status updates
- Live log streaming
- Job cancellation support

### ✅ Database Storage
- Job tracking and history
- Video metadata
- Processing logs
- File paths
- Content analysis
- Publishing status

## API Examples

### Create a Job
```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=uhJJgc-0iTQ"}'
```

Response:
```json
{
  "id": 1,
  "job_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "youtube_url": "https://www.youtube.com/watch?v=uhJJgc-0iTQ",
  "video_id": "uhJJgc-0iTQ",
  "status": "PENDING",
  "progress": 0,
  "created_at": "2025-11-27T22:30:00Z",
  "started_at": null,
  "completed_at": null,
  "error_message": null,
  "cancelled": false
}
```

### List Jobs
```bash
curl http://localhost:8000/api/jobs?limit=10&status=COMPLETED
```

### Get Job Details
```bash
curl http://localhost:8000/api/jobs/123e4567-e89b-12d3-a456-426614174000
```

### Get Statistics
```bash
curl http://localhost:8000/api/stats
```

Response:
```json
{
  "total_jobs": 25,
  "completed": 20,
  "failed": 2,
  "running": 1,
  "pending": 2,
  "cancelled": 0,
  "avg_duration_minutes": 15.5
}
```

### Cancel Job
```bash
curl -X DELETE http://localhost:8000/api/jobs/123e4567-e89b-12d3-a456-426614174000
```

## WebSocket Usage

### JavaScript Example

```javascript
// Connect to status updates
const statusWs = new WebSocket('ws://localhost:8000/ws/jobs/status');

statusWs.onopen = () => {
  console.log('Connected to status stream');
};

statusWs.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Status update:', data);
  // {
  //   job_uuid: "...",
  //   status: "TRANSCRIBING",
  //   progress: 25,
  //   stage: "transcribing",
  //   timestamp: "2025-11-27T22:35:00Z"
  // }
};

// Connect to job logs
const logsWs = new WebSocket(`ws://localhost:8000/ws/jobs/${jobUuid}/logs`);

logsWs.onmessage = (event) => {
  const log = JSON.parse(event.data);
  console.log(`[${log.level}] ${log.message}`);
};
```

## Job Status Flow

```
PENDING (0%)
    ↓
DOWNLOADING (10%) - Downloading video from YouTube
    ↓
TRANSCRIBING (25%) - Extracting/generating transcripts
    ↓
TRANSLATING (40%) - Translating to Chinese
    ↓
PROCESSING_VIDEO (60%) - Burning subtitles
    ↓
ANALYZING (75%) - Content analysis
    ↓
PUBLISHING (85%) - Publishing to platforms
    ↓
COMPLETED (100%) - All done!

At any point:
    → FAILED (on error)
    → CANCELLED (by user)
```

## Database Schema

### Tables
- `jobs` - Main job tracking
- `job_metadata` - Video information
- `job_logs` - Processing logs
- `job_files` - Generated files
- `job_analysis` - Content analysis results
- `job_publishing` - Platform publishing status

## Configuration

Edit `src/web/config.py` or create `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/z2_platform
API_PREFIX=/api
MAX_CONCURRENT_JOBS=2
CORS_ORIGINS=["http://localhost:3000"]
```

## Development

### Project Structure
```
src/web/
├── main.py              # FastAPI application
├── config.py            # Configuration
├── database.py          # Database connection
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic request/response schemas
├── api/
│   ├── jobs.py          # Job management endpoints
│   ├── stats.py         # Statistics endpoint
│   └── websocket.py     # WebSocket handlers
├── services/
│   ├── job_service.py   # Business logic
│   ├── job_queue.py     # Async job queue
│   ├── pipeline_runner.py  # Pipeline execution
│   └── websocket_manager.py  # WebSocket connections
└── utils/
    └── validators.py    # URL validation
```

### Dependencies
See `requirements-web.txt`

Key dependencies:
- FastAPI - Web framework
- Uvicorn - ASGI server
- SQLAlchemy - ORM
- PostgreSQL - Database
- WebSockets - Real-time communication
- Pydantic - Data validation

## Frontend (TODO)

The frontend React application is not yet implemented. See `documents/backlog/20251127-WebDashboard/02. Design.md` for the planned frontend architecture.

### Planned Features:
- Job submission form
- Real-time job status dashboard
- Job history table with filtering
- Job detail view
- Live log viewer
- Statistics panel

## Testing

### Manual API Testing
1. Start the server: `./run_web.sh`
2. Open http://localhost:8000/docs
3. Try the interactive API documentation

### Test Job Submission
```bash
# Submit a job
JOB_UUID=$(curl -s -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=uhJJgc-0iTQ"}' \
  | jq -r '.job_uuid')

echo "Job UUID: $JOB_UUID"

# Watch status
while true; do
  curl -s http://localhost:8000/api/jobs/$JOB_UUID | jq '.status, .progress'
  sleep 2
done
```

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running on port 5433
- Check `docker ps | grep postgres`
- Verify database exists: `docker exec -it zeeren-eap-scratch-postgres-1 psql -U postgres -l`

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements-web.txt`

### WebSocket Connection Failed
- Check CORS settings in `config.py`
- Ensure server is running with `--reload` flag

## Next Steps

1. ✅ Backend Complete
2. ⏳ Build React Frontend
3. ⏳ Test End-to-End
4. ⏳ Deploy to Production

See `documents/backlog/20251127-WebDashboard/00. Plan.md` for full implementation plan.
