# CLAUDE.md
必ず日本語で返答してください。
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Database Migrations (Alembic)
```bash
# Generate new migration
alembic revision --autogenerate -m "migration description"

# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Rollback one migration
alembic downgrade -1
```

### Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run production server (Render deployment)
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Testing
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/repository/test_auth_postgres_repository.py

# Run tests with coverage
pytest --cov=app

# Run tests and generate HTML coverage report
pytest --cov=app --cov-report=html
```

## Architecture Overview

This is a FastAPI application implementing Domain-Driven Design (DDD) for an English learning platform called "EIGOAT".

### Core Architecture Layers
- **Domain** (`app/domain/`): Business entities, value objects, and repository interfaces
- **Services** (`app/services/`): Application logic and orchestration
- **Repository** (`app/repository/`): Data access implementations (PostgreSQL)
- **Endpoint** (`app/endpoint/`): REST API controllers
- **Schema** (`app/schema/`): SQLAlchemy ORM models

### Business Domains
- **Auth**: JWT authentication, email verification, user management
- **Practice**: AI-powered English conversation practice with OpenAI
- **Dashboard**: Learning analytics and progress tracking
- **Email**: Verification codes and notifications via Resend

### Key Technologies
- **FastAPI**: Async web framework with automatic OpenAPI docs
- **SQLAlchemy**: Async ORM with PostgreSQL via asyncpg
- **LangChain/LangGraph**: AI orchestration for conversation generation
- **OpenAI**: GPT models for English practice conversations
- **Alembic**: Database schema migrations
- **JWT**: Token-based authentication with bcrypt password hashing

### Repository Pattern
The codebase follows clean architecture with abstract repository interfaces in the domain layer and concrete PostgreSQL implementations in the repository layer. Dependencies are injected via FastAPI's dependency system.

### Database Schema
- Users with email verification workflow
- English conversation practice sessions and messages
- Test scoring for both conversations and individual messages
- Learning history tracking for user analytics

### Security
- JWT access/refresh tokens with proper validation
- Email verification with time-limited codes
- CORS, HTTPS redirect, and trusted host middleware
- bcrypt password hashing

### Deployment
Configured for Render.com cloud deployment with automatic builds from requirements.txt.