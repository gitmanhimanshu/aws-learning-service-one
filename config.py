import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("service-1")

class Settings:
    SERVICE_NAME: str = "aws-learning-service-one"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")
    PORT: int = int(os.getenv("PORT", "8001"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Non-sensitive configuration (Safe to expose)
    APP_FEATURE_FLAG_ALPHA: bool = os.getenv("FEATURE_FLAG_ALPHA", "true").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    
    # Secrets management
    ENABLE_SECRETS_MANAGER: bool = os.getenv("ENABLE_SECRETS_MANAGER", "false").lower() == "true"
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    SECRET_NAME: str = os.getenv("SECRET_NAME", f"learning/{os.getenv('ENVIRONMENT', 'dev')}/service-1")
    
    # Internal secret values (loaded from AWS Secrets Manager or fallback local env)
    _cached_secrets: Dict[str, Any] = {}

    @classmethod
    def load_secrets(cls) -> Dict[str, Any]:
        """
        Loads secrets from AWS Secrets Manager if enabled, otherwise falls back to local env.
        Secrets are NEVER logged or exposed via endpoints.
        """
        if not cls.ENABLE_SECRETS_MANAGER:
            logger.info("Secrets Manager disabled. Using local environment variables.")
            return {
                "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///./dev.db"),
                "API_KEY": os.getenv("API_KEY", "dummy-local-key")
            }

        try:
            import boto3
            from botocore.exceptions import ClientError

            logger.info("Fetching secrets from AWS Secrets Manager: %s in %s", cls.SECRET_NAME, cls.AWS_REGION)
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=cls.AWS_REGION
            )
            response = client.get_secret_value(SecretId=cls.SECRET_NAME)
            
            if 'SecretString' in response:
                cls._cached_secrets = json.loads(response['SecretString'])
                logger.info("Successfully fetched and cached secrets from AWS Secrets Manager.")
            return cls._cached_secrets
        except Exception as e:
            logger.warning("Could not load secrets from AWS Secrets Manager: %s. Using local fallback.", str(e))
            return {
                "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///./dev.db"),
                "API_KEY": os.getenv("API_KEY", "dummy-local-key")
            }

settings = Settings()

