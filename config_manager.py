import json
import os

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file='config.json'):
        """
        Initialize the ConfigManager
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                # Return default config if file doesn't exist
                return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            "input_folder_path": ""
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """
        Get a configuration value
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Set a configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        self.save_config()
    
    def get_input_folder_path(self):
        """
        Get the input folder path, ensuring it exists
        
        Returns:
            Valid folder path or None
        """
        folder_path = self.get('input_folder_path', '')
        if folder_path and os.path.isdir(folder_path):
            return folder_path
        return None
