# AWS Learning - Service One (Information Service)

Lightweight FastAPI microservice designed for manual deployment on AWS EC2 behind an Application Load Balancer (ALB).

## Features
- Endpoints:
  - `GET /` & `GET /service1`: Welcome message.
  - `GET /health` & `GET /service1/health`: Health check (used by ALB Target Group).
  - `GET /info` & `GET /service1/info`: Service metadata, version, and active environment.
  - `GET /config` & `GET /service1/config`: Safe, non-sensitive configuration values.
- Structured logging with JSON/ISO timestamps.
- Zero secrets hardcoded. Optional integration with AWS Secrets Manager via IAM role.

## Local Setup (Without Docker)

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run service:**
   ```bash
   python main.py
   # Or using uvicorn directly:
   uvicorn main:app --host 0.0.0.0 --port 8001
   ```

4. **Verify:**
   - Health check: `http://localhost:8001/health`
   - Config: `http://localhost:8001/config`

## Sample Responses

### `GET /health`
```json
{
  "status": "healthy",
  "service": "aws-learning-service-one",
  "environment": "dev",
  "timestamp": "2026-10-23T08:00:00Z"
}
```

### `GET /config`
```json
{
  "service": "aws-learning-service-one",
  "environment": "dev",
  "safe_config": {
    "feature_flag_alpha": true,
    "cache_ttl_seconds": 300,
    "aws_region": "us-east-1",
    "secrets_manager_enabled": false,
    "secret_name": "none"
  }
}
```

