import logging
import traceback
from typing import Optional, Callable, Any


class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, log_file: str = "game.log"):
        self.logger = self._setup_logger(log_file)
    
    def _setup_logger(self, log_file: str) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger("MurderMysteryGame")
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_error(self, error: Exception, context: str = ""):
        """Log an error with context"""
        error_msg = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(error_msg)
        self.logger.debug(traceback.format_exc())
    
    def log_info(self, message: str):
        """Log an info message"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log a warning message"""
        self.logger.warning(message)
    
    def handle_error(self, error: Exception, context: str = "", 
                    fallback: Optional[Callable] = None) -> Optional[Any]:
        """Handle an error with optional fallback"""
        self.log_error(error, context)
        
        if fallback:
            try:
                return fallback()
            except Exception as fallback_error:
                self.log_error(fallback_error, "Fallback failed")
        
        return None
    
    def safe_execute(self, func: Callable, *args, fallback: Optional[Callable] = None, 
                    context: str = "", **kwargs) -> Optional[Any]:
        """Execute a function safely with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return self.handle_error(e, context, fallback)
