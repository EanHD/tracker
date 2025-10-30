"""Cross-platform path utilities for the Tracker application."""

import os
import platform
from pathlib import Path
from typing import Optional


class TrackerPaths:
    """Manages application paths across different platforms."""
    
    @staticmethod
    def get_system() -> str:
        """Get the current operating system."""
        return platform.system()
    
    @staticmethod
    def get_home_dir() -> Path:
        """Get the user's home directory."""
        return Path.home()
    
    @staticmethod
    def get_config_dir() -> Path:
        """
        Get the configuration directory based on platform conventions.
        
        Returns:
            - Windows: %APPDATA%/tracker
            - macOS: ~/Library/Application Support/tracker
            - Linux: ~/.config/tracker
        """
        system = TrackerPaths.get_system()
        
        if system == "Windows":
            # Use APPDATA on Windows
            app_data = os.environ.get('APPDATA')
            if app_data:
                config_dir = Path(app_data) / "tracker"
            else:
                config_dir = Path.home() / "AppData" / "Roaming" / "tracker"
        elif system == "Darwin":  # macOS
            config_dir = Path.home() / "Library" / "Application Support" / "tracker"
        else:  # Linux and other Unix-like systems
            # Follow XDG Base Directory Specification
            xdg_config = os.environ.get('XDG_CONFIG_HOME')
            if xdg_config:
                config_dir = Path(xdg_config) / "tracker"
            else:
                config_dir = Path.home() / ".config" / "tracker"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    @staticmethod
    def get_data_dir() -> Path:
        """
        Get the data directory based on platform conventions.
        
        Returns:
            - Windows: %LOCALAPPDATA%/tracker
            - macOS: ~/Library/Application Support/tracker
            - Linux: ~/.local/share/tracker
        """
        system = TrackerPaths.get_system()
        
        if system == "Windows":
            # Use LOCALAPPDATA on Windows
            local_app_data = os.environ.get('LOCALAPPDATA')
            if local_app_data:
                data_dir = Path(local_app_data) / "tracker"
            else:
                data_dir = Path.home() / "AppData" / "Local" / "tracker"
        elif system == "Darwin":  # macOS
            data_dir = Path.home() / "Library" / "Application Support" / "tracker"
        else:  # Linux and other Unix-like systems
            # Follow XDG Base Directory Specification
            xdg_data = os.environ.get('XDG_DATA_HOME')
            if xdg_data:
                data_dir = Path(xdg_data) / "tracker"
            else:
                data_dir = Path.home() / ".local" / "share" / "tracker"
        
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    @staticmethod
    def get_cache_dir() -> Path:
        """
        Get the cache directory based on platform conventions.
        
        Returns:
            - Windows: %TEMP%/tracker
            - macOS: ~/Library/Caches/tracker
            - Linux: ~/.cache/tracker
        """
        system = TrackerPaths.get_system()
        
        if system == "Windows":
            # Use TEMP on Windows
            temp_dir = os.environ.get('TEMP') or os.environ.get('TMP')
            if temp_dir:
                cache_dir = Path(temp_dir) / "tracker"
            else:
                cache_dir = Path.home() / "AppData" / "Local" / "Temp" / "tracker"
        elif system == "Darwin":  # macOS
            cache_dir = Path.home() / "Library" / "Caches" / "tracker"
        else:  # Linux and other Unix-like systems
            # Follow XDG Base Directory Specification
            xdg_cache = os.environ.get('XDG_CACHE_HOME')
            if xdg_cache:
                cache_dir = Path(xdg_cache) / "tracker"
            else:
                cache_dir = Path.home() / ".cache" / "tracker"
        
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    @staticmethod
    def get_log_dir() -> Path:
        """
        Get the log directory.
        
        Returns:
            Platform-specific log directory within the data directory.
        """
        log_dir = TrackerPaths.get_data_dir() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    @staticmethod
    def get_database_path(filename: str = "tracker.db") -> Path:
        """
        Get the database file path.
        
        Args:
            filename: Database filename (default: tracker.db)
            
        Returns:
            Full path to the database file.
        """
        return TrackerPaths.get_data_dir() / filename
    
    @staticmethod
    def get_env_file_path() -> Path:
        """
        Get the .env file path.
        
        Checks in order:
        1. Current working directory (for development)
        2. Config directory (for production)
        
        Returns:
            Path to the .env file.
        """
        # Check current directory first (for development)
        local_env = Path.cwd() / ".env"
        if local_env.exists():
            return local_env
        
        # Otherwise use config directory
        return TrackerPaths.get_config_dir() / ".env"
    
    @staticmethod
    def get_export_dir() -> Path:
        """
        Get the default export directory.
        
        Returns:
            User's Documents/Tracker directory.
        """
        system = TrackerPaths.get_system()
        
        if system == "Windows":
            # Try to get Documents folder from registry or use default
            documents = Path.home() / "Documents"
        elif system == "Darwin":  # macOS
            documents = Path.home() / "Documents"
        else:  # Linux
            # Check for XDG documents directory
            xdg_documents = os.environ.get('XDG_DOCUMENTS_DIR')
            if xdg_documents:
                documents = Path(xdg_documents)
            else:
                documents = Path.home() / "Documents"
        
        export_dir = documents / "Tracker"
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir
    
    @staticmethod
    def ensure_permissions(path: Path) -> None:
        """
        Ensure proper permissions for a file or directory.
        
        Args:
            path: Path to set permissions for.
        """
        system = TrackerPaths.get_system()
        
        if system != "Windows":
            # Set appropriate permissions on Unix-like systems
            import stat
            
            if path.is_dir():
                # Directory: rwx for owner, rx for group, nothing for others
                path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
            else:
                # File: rw for owner, r for group, nothing for others
                path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)
    
    @staticmethod
    def normalize_path(path: str) -> Path:
        """
        Normalize a path string to handle platform differences.
        
        Args:
            path: Path string to normalize.
            
        Returns:
            Normalized Path object.
        """
        # Expand user home directory
        path = os.path.expanduser(path)
        
        # Expand environment variables
        path = os.path.expandvars(path)
        
        # Convert to Path object and resolve
        return Path(path).resolve()
    
    @staticmethod
    def get_temp_file(prefix: str = "tracker_", suffix: str = ".tmp") -> Path:
        """
        Get a temporary file path.
        
        Args:
            prefix: File prefix.
            suffix: File suffix.
            
        Returns:
            Path to a temporary file.
        """
        import tempfile
        
        temp_dir = TrackerPaths.get_cache_dir()
        fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=temp_dir)
        os.close(fd)  # Close the file descriptor
        
        return Path(temp_path)


# Convenience functions
def get_config_dir() -> Path:
    """Get the configuration directory."""
    return TrackerPaths.get_config_dir()


def get_data_dir() -> Path:
    """Get the data directory."""
    return TrackerPaths.get_data_dir()


def get_database_path(filename: str = "tracker.db") -> Path:
    """Get the database file path."""
    return TrackerPaths.get_database_path(filename)


def get_log_dir() -> Path:
    """Get the log directory."""
    return TrackerPaths.get_log_dir()


def get_export_dir() -> Path:
    """Get the export directory."""
    return TrackerPaths.get_export_dir()
import os
import platform
from pathlib import Path
from typing import Optional


class TrackerPaths:
    """Manages application paths across different platforms."""
    
    @staticmethod
    def get_system() -> str:
        """Get the current operating system."""
        return platform.system()
    
    @staticmethod
    def get_home_dir() -> Path:
        """Get the user's home directory."""
        return Path.home()
    
    @staticmethod
    def get_config_dir() -> Path:
        """
        Get the configuration directory based on platform conventions.
        
        Returns:
            - Windows: %APPDATA%/tracker
            - macOS: ~/Library/Application Support/tracker
            - Linux: ~/.config/tracker
        """
        system = TrackerPaths.get_system()
        
        if system == "Windows":
            # Use APPDATA on Windows
            app_data = os.environ.get('APPDATA')
            if app_data:
                config_dir = Path(app_data) / "tracker"
            else:
                config_dir = Path.home() / "AppData" / "Roaming" / "tracker"
        elif system == "Darwin":  # macOS
            config_dir = Path.home() / "Library" / "Application Support" / "tracker"
        else:  # Linux and other Unix-like systems
            # Follow XDG Base Directory Specification
            xdg_config = os.environ.get('XDG_CONFIG_HOME')
            if xdg_config:
                config_dir = Path(xdg_config) / "tracker"
            else:
                config_dir = Path.home() / ".config" / "tracker"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    @staticmethod
    def get_data_dir() -> Path:
        """
        Get the data directory based on platform conventions.
        
        Returns:
            - Windows: %LOCALAPPDATA%/tracker
            - macOS: ~/Library/Application Support/tracker
            - Linux: ~/.local/share/tracker
        """
        system = TrackerPaths.get_system()
        
        if system == "Windows":
            # Use LOCALAPPDATA on Windows
            local_app_data = os.environ.get('LOCALAPPDATA')
            if local_app_data:
                data_dir = Path(local_app_data) / "tracker"
            else:
                data_dir = Path.home() / "AppData" / "Local" / "tracker"
        elif system == "Darwin":  # macOS
            data_dir = Path.home() / "Library" / "Application Support" / "tracker"
        else:  # Linux and other Unix-like systems
            # Follow XDG Base Directory Specification
            xdg_data = os.environ.get('XDG_DATA_HOME')
            if xdg_data:
                data_dir = Path(xdg_data) / "tracker"
            else:
                data_dir = Path.home() / ".local" / "share" / "tracker"
        
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    @staticmethod
    def get_cache_dir() -> Path:
        """
        Get the cache directory based on platform conventions.
        
        Returns:
            - Windows: %TEMP%/tracker
            - macOS: ~/Library/Caches/tracker
            - Linux: ~/.cache/tracker
        """
        system = TrackerPaths.get_system()
        
        if system == "Windows":
            # Use TEMP on Windows
            temp_dir = os.environ.get('TEMP') or os.environ.get('TMP')
            if temp_dir:
                cache_dir = Path(temp_dir) / "tracker"
            else:
                cache_dir = Path.home() / "AppData" / "Local" / "Temp" / "tracker"
        elif system == "Darwin":  # macOS
            cache_dir = Path.home() / "Library" / "Caches" / "tracker"
        else:  # Linux and other Unix-like systems
            # Follow XDG Base Directory Specification
            xdg_cache = os.environ.get('XDG_CACHE_HOME')
            if xdg_cache:
                cache_dir = Path(xdg_cache) / "tracker"
            else:
                cache_dir = Path.home() / ".cache" / "tracker"
        
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    @staticmethod
    def get_log_dir() -> Path:
        """
        Get the log directory.
        
        Returns:
            Platform-specific log directory within the data directory.
        """
        log_dir = TrackerPaths.get_data_dir() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    @staticmethod
    def get_database_path(filename: str = "tracker.db") -> Path:
        """
        Get the database file path.
        
        Args:
            filename: Database filename (default: tracker.db)
            
        Returns:
            Full path to the database file.
        """
        return TrackerPaths.get_data_dir() / filename
    
    @staticmethod
    def get_env_file_path() -> Path:
        """
        Get the .env file path.
        
        Checks in order:
        1. Current working directory (for development)
        2. Config directory (for production)
        
        Returns:
            Path to the .env file.
        """
        # Check current directory first (for development)
        local_env = Path.cwd() / ".env"
        if local_env.exists():
            return local_env
        
        # Otherwise use config directory
        return TrackerPaths.get_config_dir() / ".env"
    
    @staticmethod
    def get_export_dir() -> Path:
        """
        Get the default export directory.
        
        Returns:
            User's Documents/Tracker directory.
        """
        system = TrackerPaths.get_system()
        
        if system == "Windows":
            # Try to get Documents folder from registry or use default
            documents = Path.home() / "Documents"
        elif system == "Darwin":  # macOS
            documents = Path.home() / "Documents"
        else:  # Linux
            # Check for XDG documents directory
            xdg_documents = os.environ.get('XDG_DOCUMENTS_DIR')
            if xdg_documents:
                documents = Path(xdg_documents)
            else:
                documents = Path.home() / "Documents"
        
        export_dir = documents / "Tracker"
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir
    
    @staticmethod
    def ensure_permissions(path: Path) -> None:
        """
        Ensure proper permissions for a file or directory.
        
        Args:
            path: Path to set permissions for.
        """
        system = TrackerPaths.get_system()
        
        if system != "Windows":
            # Set appropriate permissions on Unix-like systems
            import stat
            
            if path.is_dir():
                # Directory: rwx for owner, rx for group, nothing for others
                path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
            else:
                # File: rw for owner, r for group, nothing for others
                path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)
    
    @staticmethod
    def normalize_path(path: str) -> Path:
        """
        Normalize a path string to handle platform differences.
        
        Args:
            path: Path string to normalize.
            
        Returns:
            Normalized Path object.
        """
        # Expand user home directory
        path = os.path.expanduser(path)
        
        # Expand environment variables
        path = os.path.expandvars(path)
        
        # Convert to Path object and resolve
        return Path(path).resolve()
    
    @staticmethod
    def get_temp_file(prefix: str = "tracker_", suffix: str = ".tmp") -> Path:
        """
        Get a temporary file path.
        
        Args:
            prefix: File prefix.
            suffix: File suffix.
            
        Returns:
            Path to a temporary file.
        """
        import tempfile
        
        temp_dir = TrackerPaths.get_cache_dir()
        fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=temp_dir)
        os.close(fd)  # Close the file descriptor
        
        return Path(temp_path)


# Convenience functions
def get_config_dir() -> Path:
    """Get the configuration directory."""
    return TrackerPaths.get_config_dir()


def get_data_dir() -> Path:
    """Get the data directory."""
    return TrackerPaths.get_data_dir()


def get_database_path(filename: str = "tracker.db") -> Path:
    """Get the database file path."""
    return TrackerPaths.get_database_path(filename)


def get_log_dir() -> Path:
    """Get the log directory."""
    return TrackerPaths.get_log_dir()


def get_export_dir() -> Path:
    """Get the export directory."""
    return TrackerPaths.get_export_dir()
