import threading
import queue
from typing import Callable, Any, Optional, Tuple

from Services.ErrorHandler import ErrorHandler


class ThreadingService:
    """Handles background task execution and result management.

    This service wraps Python's ``threading.Thread`` and a ``queue.Queue``
    to provide a simple interface for running background tasks and
    collecting their results. When an ``ErrorHandler`` is provided, any
    exceptions raised in the background task are logged centrally before
    being surfaced to callers via the result queue.
    """

    def __init__(self, error_handler: Optional[ErrorHandler] = None) -> None:
        """Create a new threading service.

        Args:
            error_handler: Optional error handler used to log exceptions
                raised by background tasks.
        """
        self.result_queue: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self.current_thread: Optional[threading.Thread] = None
        self._error_handler = error_handler

    def execute_async(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> "queue.Queue[Tuple[str, Any]]":
        """Execute a task asynchronously and return the result queue.

        The queue will contain exactly one tuple of the form
        ``("success", result)`` or ``("error", error_message)``.
        """
        self.result_queue = queue.Queue()

        def wrapper() -> None:
            try:
                result = task(*args, **kwargs)
                self.result_queue.put(("success", result))
            except Exception as error:  # pragma: no cover - defensive logging
                if self._error_handler is not None:
                    context = getattr(task, "__name__", "background_task")
                    self._error_handler.log_error(error, context=context)
                self.result_queue.put(("error", str(error)))

        self.current_thread = threading.Thread(target=wrapper)
        self.current_thread.daemon = True
        self.current_thread.start()

        return self.result_queue

    def is_task_complete(self) -> bool:
        """Return ``True`` if the current task has completed."""
        return not self.result_queue.empty()

    def get_result(self) -> Tuple[str, Any]:
        """Get the result from the queue (blocking)."""
        return self.result_queue.get()

    def try_get_result(self) -> Optional[Tuple[str, Any]]:
        """Try to get result without blocking.

        Returns ``None`` if no result is currently available.
        """
        if not self.result_queue.empty():
            return self.result_queue.get()
        return None
