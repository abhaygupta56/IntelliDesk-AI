"""
Logging utility for IntelliDesk AI
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from config import Config

class Logger:
    """Custom logger for the application"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name="IntelliDesk"):
        """Get or create a logger instance"""
        
        if name in cls._loggers:
            return cls._loggers[name]
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Console Handler (INFO and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        
        # File Handler (DEBUG and above)
        file_handler = logging.FileHandler(
            Config.LOG_FILE,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        # Error File Handler (ERROR and above)
        error_handler = logging.FileHandler(
            Config.ERROR_LOG_FILE,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        
        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        
        cls._loggers[name] = logger
        return logger

# Convenience functions
def info(message):
    Logger.get_logger().info(message)

def debug(message):
    Logger.get_logger().debug(message)

def warning(message):
    Logger.get_logger().warning(message)

def error(message):
    Logger.get_logger().error(message)

def critical(message):
    Logger.get_logger().critical(message)