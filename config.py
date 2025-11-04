import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env', override=False)

class Config:
    """Configuration class that loads settings from environment variables"""
    
    def _get_env_var(self, var_name: str) -> str:
        """Get environment variable with proper error handling"""
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Environment variable {var_name} is required but not set")
        return value
    
    def __init__(self):
        # MONGO_HOST must be a full MongoDB connection string (mongodb:// or mongodb+srv://)
        self.mongo_host = self._get_env_var('MONGO_HOST')
        if not (self.mongo_host.startswith('mongodb://') or self.mongo_host.startswith('mongodb+srv://')):
            raise ValueError("MONGO_HOST must be a full MongoDB connection string (starting with mongodb:// or mongodb+srv://)")
        
        self.mongo_database = self._get_env_var('MONGO_DATABASE')
        self.mongo_collection_hardware = self._get_env_var('MONGO_COLLECTION_HARDWARE')
        self.mongo_collection_checkouts = self._get_env_var('MONGO_COLLECTION_CHECKOUTS')
        self.service_port = int(self._get_env_var('SERVICE_PORT'))
        self.environment = self._get_env_var('ENVIRONMENT')
    
    def get_mongodb_connection_string(self) -> str:
        """Return MongoDB connection string with TLS parameters if needed"""
        conn_str = self.mongo_host
        
        # Add tlsAllowInvalidCertificates to connection string if needed
        # This is more reliable than client parameter for mongodb+srv://
        import os
        allow_invalid_certs = os.getenv('MONGO_ALLOW_INVALID_CERTS', 'true').lower() == 'true'
        
        if allow_invalid_certs and 'mongodb+srv://' in conn_str:
            # Add tlsAllowInvalidCertificates to query parameters
            if '?' in conn_str:
                if 'tlsAllowInvalidCertificates' not in conn_str:
                    conn_str += '&tlsAllowInvalidCertificates=true'
            else:
                conn_str += '?tlsAllowInvalidCertificates=true'
        
        return conn_str
    
    def validate_config(self) -> bool:
        """Validate that required configuration is present"""
        return bool(self.mongo_host and self.mongo_database)

# Global config instance
config = Config()
