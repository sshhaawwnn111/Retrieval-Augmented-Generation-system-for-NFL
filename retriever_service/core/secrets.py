"""
AWS Secrets Manager integration
"""
import json
import logging
import boto3
from botocore.exceptions import ClientError
from functools import lru_cache

logger = logging.getLogger(__name__)

class SecretsManager:
    """
    AWS Secrets Manager client for retrieving secrets
    """
    def __init__(self, region_name: str = "us-east-2"):
        self.client = boto3.client(
            service_name='secretsmanager',
            region_name=region_name
        )
    
    def get_secret(self, secret_name: str) -> dict:
        """
        Retrieve a secret from AWS Secrets Manager
        
        Args:
            secret_name: Name or ARN of the secret
            
        Returns:
            Dictionary containing the secret values
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            
            # Secrets can be stored as string or binary
            if 'SecretString' in response:
                secret = json.loads(response['SecretString'])
            else:
                secret = response['SecretBinary']
            
            logger.info(f"Successfully retrieved secret: {secret_name}")
            return secret
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                logger.error(f"Secret not found: {secret_name}")
            elif error_code == 'InvalidRequestException':
                logger.error(f"Invalid request for secret: {secret_name}")
            elif error_code == 'InvalidParameterException':
                logger.error(f"Invalid parameter for secret: {secret_name}")
            elif error_code == 'DecryptionFailure':
                logger.error(f"Decryption failed for secret: {secret_name}")
            elif error_code == 'InternalServiceError':
                logger.error(f"Internal service error retrieving secret: {secret_name}")
            else:
                logger.error(f"Error retrieving secret {secret_name}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving secret {secret_name}: {str(e)}")
            raise

@lru_cache(maxsize=10)
def get_database_credentials(secret_name: str, region: str = "us-east-2") -> dict:
    """
    Cached retrieval of database credentials from Secrets Manager
    
    Args:
        secret_name: Name of the secret containing DB credentials
        region: AWS region
        
    Returns:
        Dictionary with keys: username, password
        Note: RDS-managed secrets only contain username and password
    """
    sm = SecretsManager(region_name=region)
    return sm.get_secret(secret_name)