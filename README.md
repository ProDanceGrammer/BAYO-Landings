# Lead Management System

> **Technical Assignment Submission** - Backend system for receiving and processing leads from landing pages

A microservices-based lead management system built with Python 3.11+, FastAPI, PostgreSQL, Redis, and Docker. This project demonstrates implementation of a production-ready backend with proper architecture, testing, and documentation.

## Assignment Status

✅ **All Requirements Implemented**
- Two independent FastAPI microservices (landings + core)
- JWT authentication with affiliate validation
- Redis-based queue communication
- Background worker with 10-minute deduplication
- Analytics API with date/offer grouping
- Full test coverage (16/16 tests passing)
- Comprehensive Swagger documentation
- Docker Compose orchestration

**Submission Date:** 27 April 2026

## Requirements Compliance

This implementation fulfills all technical assignment requirements:

### Required Stack ✅
- **Python 3.11+** - Using Python 3.11.15
- **FastAPI** - Both services built with FastAPI
- **PostgreSQL** - Database with required tables (leads, offers, affiliates)
- **SQLAlchemy 2** - Using async SQLAlchemy with asyncpg driver
- **Alembic** - Database migrations implemented
- **Redis** - Message queue for service communication
- **JWT** - Bearer token authentication

### Required Tables ✅
- **leads** - Stores all lead data with created_at timestamp
- **offers** - Fields: id (int), name (string)
- **affiliates** - Fields: id (int), name (string)

### Service 1: Landings ✅
- **POST /lead** - Accepts leads with full validation
- Validates all fields including ISO 3166-1 alpha-2 country codes
- Verifies affiliate_id matches JWT token
- Queues accepted leads to Redis
- Returns 200 on success

### Service 2: Core ✅
- **Background Worker** - Processes leads from Redis queue
- **Deduplication** - 10-minute window using Redis (name+phone+offer_id+affiliate_id)
- **GET /leads** - Analytics with date_from, date_to, group parameters
- Supports grouping by date or offer
- Returns counts and lead lists per group

### Additional Features ✅
- **Swagger Documentation** - Interactive API docs at /docs endpoints
- **Unit Tests** - 16 tests covering routes, services, validation, deduplication
- **Docker Compose** - One-command deployment
- **Structured Logging** - Clear separation of client vs system errors

## Technical Decisions

### Architecture Choices

**Shared Services Module**
- Created `shared/` directory for common code (models, schemas, config, auth)
- Follows DRY principle - authentication logic shared between services
- Reduces code duplication and ensures consistency

**Async Throughout**
- Full async/await implementation for better performance
- AsyncPG for PostgreSQL, async Redis client
- Non-blocking I/O for all database and cache operations

**Country Validation**
- Used `pycountry` library for ISO 3166-1 alpha-2 validation
- Provides official country code validation
- Better than manual list maintenance

**Deduplication Strategy**
- Redis SET with 10-minute TTL
- Hash key: MD5(name+phone+offer_id+affiliate_id)
- Prevents duplicate processing without database queries

**Testing Approach**
- Integration tests with FastAPI TestClient
- Database fixtures with test isolation
- Dependency injection for mocking Redis/DB in tests

## Quick Evaluation Guide

For reviewers to quickly assess this implementation:

### 1. Start the System (2 minutes)
```bash
docker-compose up -d
docker-compose exec landings alembic upgrade head
docker-compose exec landings python seed_data.py
```

### 2. Test via Swagger UI (3 minutes)
1. Open http://localhost:8001/docs
2. Click "Authorize" and paste token from seed_data.py output
3. Try POST /lead with sample data
4. Open http://localhost:8002/docs and test GET /leads

### 3. Run Tests (1 minute)
```bash
docker-compose exec landings pytest tests/ -v
```

### 4. Review Code Structure
- `shared/` - Common models, schemas, authentication
- `landings/` - Lead acceptance service
- `core/` - Lead processing and analytics
- `tests/` - Unit and integration tests

## Architecture

The system uses two independent microservices:

- **Landings Service** (Port 8001): Fast lead acceptance and queuing
- **Core Service** (Port 8002): Lead processing, deduplication, and analytics
- **Core Worker**: Background worker for processing leads from Redis queue

### Key Features

- JWT-based authentication tied to affiliate identities
- Real-time lead acceptance without blocking
- Background processing with 10-minute deduplication window
- Analytics API for tracking affiliate performance
- ISO 3166-1 alpha-2 country code validation using pycountry
- Structured logging with clear separation of client vs system errors

## Technology Stack

- **Python 3.11+**
- **FastAPI** - Modern async web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy 2** (asyncpg) - Async ORM
- **Alembic** - Database migrations
- **Redis** - Message queue and deduplication cache
- **JWT** - Token-based authentication
- **pycountry** - ISO country code validation
- **Docker & Docker Compose** - Containerization

## Project Structure

```
BAYO-Landings/
├── shared/              # Shared components (models, schemas, config, services)
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── config.py        # Configuration
│   ├── database.py      # Database connection
│   └── services/        # Shared services (authentication)
├── landings/            # Landings service (lead acceptance)
│   ├── api/             # API routes
│   ├── services/        # Business logic (validation, queue)
│   ├── dependencies.py  # FastAPI dependencies
│   └── main.py          # Application entry point
├── core/                # Core service (processing & analytics)
│   ├── api/             # API routes
│   ├── services/        # Business logic (lead processor, analytics)
│   ├── dependencies.py  # FastAPI dependencies
│   ├── worker.py        # Background worker
│   └── main.py          # Application entry point
├── alembic/             # Database migrations
├── tests/               # Unit and integration tests
├── docker-compose.yml   # Service orchestration
├── Dockerfile           # Container image
├── requirements.txt     # Python dependencies
├── seed_data.py         # Database seeding script
└── README.md            # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed

### Launch Application

```bash
# 1. Clone repository
git clone <repository-url>
cd BAYO-Landings

# 2. Start all services
docker-compose up -d

# 3. Run database migrations
docker-compose exec landings alembic upgrade head

# 4. Seed test data (creates affiliates, offers, and JWT tokens)
docker-compose exec landings python seed_data.py

# 5. Access Swagger UI
# Landings: http://localhost:8001/docs
# Core: http://localhost:8002/docs
```

**Note:** Copy one of the JWT tokens from step 4 output to use in Swagger UI authentication.

### Testing with curl (Optional)

```bash
# Use token from seed_data.py output
curl -X POST http://localhost:8001/lead \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MX0.ifC4ERv66NSpC5cVjvQipTCjNHDyUuto4ZBY39myOso" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone": "+380123456789",
    "country": "UA",
    "offer_id": 1,
    "affiliate_id": 1
  }'

# Get analytics by date
curl -X GET "http://localhost:8002/leads?date_from=2026-04-01&date_to=2026-04-30&group=date" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MX0.ifC4ERv66NSpC5cVjvQipTCjNHDyUuto4ZBY39myOso"

# Get analytics by offer
curl -X GET "http://localhost:8002/leads?date_from=2026-04-01&date_to=2026-04-30&group=offer" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MX0.ifC4ERv66NSpC5cVjvQipTCjNHDyUuto4ZBY39myOso"
```

### Managing the Application

```bash
# Stop all services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

## API Documentation

Once services are running, access interactive API documentation:

- **Landings Service**: http://localhost:8001/docs
- **Core Service**: http://localhost:8002/docs

**Authentication in Swagger UI:**
1. Click the **"Authorize"** button (lock icon) at the top right
2. Enter your JWT token (without "Bearer" prefix)
3. Click "Authorize" then "Close"
4. Now you can make authenticated requests

## Environment Variables

The application uses default configuration suitable for development and testing. All services are configured via `docker-compose.yml`:

```env
DATABASE_URL=postgresql+asyncpg://leads_user:leads_pass@postgres:5432/leads_db
REDIS_URL=redis://redis:6379/0
JWT_SECRET=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
```

No additional `.env` file configuration is required for evaluation.

## Development

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up local PostgreSQL and Redis, then update .env

# Run migrations
alembic upgrade head

# Run services
uvicorn landings.main:app --reload --port 8001
uvicorn core.main:app --reload --port 8002
python -m core.worker
```

### Running Tests

```bash
# Run all tests
docker-compose exec landings pytest tests/ -v

# Run specific test file
docker-compose exec landings pytest tests/test_landings/test_routes.py -v

# Run with coverage
docker-compose exec landings pytest tests/ --cov=. --cov-report=html

# Run tests in quiet mode
docker-compose exec landings pytest tests/ -q
```

**Test Coverage:**
- 16 unit and integration tests
- 100% pass rate
- Tests cover: API routes, service logic, authentication, validation, deduplication

## Design Principles

- **Single Responsibility**: Each service class has one clear purpose
- **Loose Coupling**: Services communicate via Redis, not direct calls
- **DRY Principle**: Shared authentication logic in `shared/services/`
- **Dependency Injection**: Services receive dependencies via FastAPI
- **Async Throughout**: Full async/await for better performance

## Key Implementation Details

### Authentication
- JWT tokens contain `{"id": affiliate_id}`
- Token validation checks affiliate exists in database
- Affiliate ID in token must match affiliate_id in request data

### Lead Deduplication
- Redis SET with 10-minute TTL
- Hash key: MD5(name+phone+offer_id+affiliate_id)
- Prevents duplicate submissions within time window

### Country Code Validation
- Uses `pycountry` library for ISO 3166-1 alpha-2 validation
- Example: `"UA"` → Valid (Ukraine), `"XX"` → Invalid

## Troubleshooting

**Services won't start:**
```bash
docker-compose logs
docker-compose restart
```

**Database connection errors:**
```bash
docker-compose ps postgres
```

**Worker not processing leads:**
```bash
docker-compose logs core-worker
docker-compose exec redis redis-cli
> LLEN leads:queue
```

**Authentication errors:**
- Verify JWT_SECRET matches in .env
- Check affiliate exists in database
- Ensure token format is `Bearer <token>`
