import threading
import queue
from typing import Callable, Any


class ThreadingService:
    """Handles background task execution and result management"""
    
    def __init__(self):
        self.result_queue = queue.Queue()
        self.current_thread = None
    
    def execute_async(self, task: Callable, *args, **kwargs) -> queue.Queue:
        """Execute a task asynchronously and return the result queue"""
        self.result_queue = queue.Queue()
        
        def wrapper():
            try:
                result = task(*args, **kwargs)
                self.result_queue.put(('success', result))
            except Exception as e:
                self.result_queue.put(('error', str(e)))
        
        self.current_thread = threading.Thread(target=wrapper)
        self.current_thread.daemon = True
        self.current_thread.start()
        
        return self.result_queue
    
    def is_task_complete(self) -> bool:
        """Check if the current task has completed"""
        return not self.result_queue.empty()
    
    def get_result(self) -> tuple:
        """Get the result from the queue (blocking)"""
        return self.result_queue.get()
    
    def try_get_result(self) -> tuple | None:
        """Try to get result without blocking"""
        if not self.result_queue.empty():
            return self.result_queue.get()
        return None
