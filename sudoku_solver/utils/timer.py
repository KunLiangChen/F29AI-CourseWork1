# utils/timer.py
import time
from functools import wraps

class Timer:
    """Context manager for timing code blocks."""
    def __init__(self, name="Operation"):
        self.name = name
        self.start_time = None
        self.elapsed = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.elapsed = time.time() - self.start_time
        print(f"[TIMER] {self.name}: {self.elapsed:.4f}s")

def timeit(func):
    """Function decorator for timing a single function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"[TIMER] {func.__name__} executed in {end - start:.4f}s")
        return result
    return wrapper
