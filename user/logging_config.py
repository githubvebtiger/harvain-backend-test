"""
Logging configuration for startup sync
"""
import logging
import sys

def setup_sync_logging():
    """Setup logging for startup sync operations"""
    
    # Create logger for startup sync
    sync_logger = logging.getLogger('user.startup_sync')
    sync_logger.setLevel(logging.INFO)
    
    # Create console handler if not already exists
    if not sync_logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        sync_logger.addHandler(console_handler)
        
        # Prevent propagation to avoid duplicate logs
        sync_logger.propagate = False
    
    return sync_logger