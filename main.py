import time
import logging
import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from config import settings

# Structured logging setup
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] service=%(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ"
)
logger = logging.getLogger(settings.SERVICE_NAME)

app = FastAPI(
    title="AWS Learning - Service One (Information Service)",
    version=settings.VERSION,
    description="Microservice 1: Exposes service information and safe configs."
)

@app.middleware("http")
async def structured_log_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    
    # Structured log format required by the specification:
    # INFO service=service-1 environment=dev path=/health status=200 duration_ms=1.2
    logger.info(
        "environment=%s method=%s path=%s status=%d duration_ms=%.2f client=%s",
        settings.ENVIRONMENT,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request.client.host if request.client else "unknown"
    )
    return response

def get_welcome_data():
    return {
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT,
        "message": "Welcome to AWS Learning Information Service",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

def get_health_data():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

def get_info_data():
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running"
    }

def get_config_data():
    # Only expose NON-SENSITIVE configurations.
    # Never expose API keys, database passwords, or secret tokens!
    return {
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT,
        "safe_config": {
            "feature_flag_alpha": settings.APP_FEATURE_FLAG_ALPHA,
            "cache_ttl_seconds": settings.CACHE_TTL_SECONDS,
            "aws_region": settings.AWS_REGION,
            "secrets_manager_enabled": settings.ENABLE_SECRETS_MANAGER,
            "secret_name": settings.SECRET_NAME if settings.ENABLE_SECRETS_MANAGER else "none"
        }
    }

# Standard endpoints
@app.get("/")
def read_root():
    return get_welcome_data()

@app.get("/health")
def read_health():
    return get_health_data()

@app.get("/info")
def read_info():
    return get_info_data()

@app.get("/config")
def read_config():
    return get_config_data()

# ALB path-based routing compatibility endpoints (/service1/*)
# ALB forwards the full request path without rewrite unless explicitly configured.
@app.get("/service1")
@app.get("/service1/")
def read_root_prefixed():
    return get_welcome_data()

@app.get("/service1/health")
def read_health_prefixed():
    return get_health_data()

@app.get("/service1/info")
def read_info_prefixed():
    return get_info_data()

@app.get("/service1/config")
def read_config_prefixed():
    return get_config_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)

