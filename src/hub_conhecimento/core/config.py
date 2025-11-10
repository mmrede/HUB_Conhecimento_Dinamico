"""
Configuration Manager
Gerenciador de Configuração

Handles loading and managing configuration from config.yaml and environment variables.
"""

import os
import yaml
from typing import Any, Dict, Optional


class ConfigManager:
    """Manages configuration for the Knowledge Hub."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._apply_env_overrides()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        # Database password
        if 'DB_PASSWORD' in os.environ:
            self.config['database']['password'] = os.environ['DB_PASSWORD']
        
        # Elasticsearch API key
        if 'ES_API_KEY' in os.environ:
            self.config['elasticsearch']['api_key'] = os.environ['ES_API_KEY']
        
        # API key
        if 'API_KEY' in os.environ:
            self.config['api']['api_key'] = os.environ['API_KEY']
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key in dot notation (e.g., 'database.host')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_database_url(self) -> str:
        """
        Get database connection URL.
        
        Returns:
            Database connection string
        """
        db = self.config['database']
        password = db.get('password', '')
        return f"postgresql://{db['user']}:{password}@{db['host']}:{db['port']}/{db['name']}"
    
    def get_elasticsearch_config(self) -> Dict[str, Any]:
        """
        Get Elasticsearch configuration.
        
        Returns:
            Elasticsearch configuration dictionary
        """
        return self.config['elasticsearch']
    
    def get_processing_config(self) -> Dict[str, Any]:
        """
        Get processing configuration.
        
        Returns:
            Processing configuration dictionary
        """
        return self.config['processing']


# Global configuration instance
_config_instance: Optional[ConfigManager] = None


def get_config(config_path: str = "config.yaml") -> ConfigManager:
    """
    Get or create global configuration instance.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        ConfigManager instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager(config_path)
    return _config_instance
