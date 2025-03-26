"""
This module manages different regex engines and provides functionality to match patterns with a timeout.
"""

import multiprocessing
import signal
import time

from project import Config, log
from src.engine import CppRegex, JavaRegex, JavaScriptRegex, PythonRe, PythonRegex


class EngineManager:
    """
    Manages different regex engines and provides functionality to match patterns with a timeout.
    """

    def __init__(self):
        self.timeout = Config.regex_timeout
        self.engine = {}
        self._init_engine()

    def _init_engine(self):
        """Register all available engines."""
        python_re = PythonRe()
        python_regex = PythonRegex()
        java = JavaRegex()
        cpp = CppRegex()
        javascript = JavaScriptRegex()
        self.engine[python_re.name] = python_re
        self.engine[python_regex.name] = python_regex
        self.engine[cpp.name] = cpp
        self.engine[java.name] = java
        self.engine[javascript.name] = javascript

    def get_engine_list(self):
        """Get the list of available engines."""
        return list(self.engine.keys())

    def get_engine(self, engine_name):
        """Get the engine instance by its name."""
        return self.engine.get(engine_name, None)

    @staticmethod
    def _run_match_with_timeout(engine, pattern, text, flags, result_queue):
        """Helper function to run match in a separate process with a timeout."""
        matches, error = [], ""
        start_time = time.time()

        def signal_handler(signum, _):
            """Signal handler to gracefully exit."""
            log.info(f"Received signal {signum}, shutting down gracefully.")
            raise TimeoutError(f"Process for engine '{engine.name}' was terminated by signal")

        signal.signal(signal.SIGTERM, signal_handler)

        try:
            # Instantiate the engine inside the separate process
            if engine:
                matches, error = engine.match(pattern, text, flags)
            else:
                error = f"Engine {engine.name} not found"
        except TimeoutError as e:
            error = str(e)
            log.warning(error)
        except (ValueError, TypeError) as e:
            error = f"Exception in engine {engine.name}: {str(e)}"
            log.error(error)
        finally:
            execution_time = time.time() - start_time
            result_queue.put((matches, error, execution_time))

    def match(self, engine_name, pattern, text, flags=0):
        """Match the pattern with the text using the selected engine with a timeout."""
        time_start = time.time()
        result_queue = multiprocessing.Queue()
        engine = self.get_engine(engine_name)  # Queue for inter-process communication
        process = multiprocessing.Process(
            target=self._run_match_with_timeout,
            args=(engine, pattern, text, flags, result_queue),
            name=f"Engine-{engine_name}",
        )

        process.start()
        start_time = time.time()
        while process.is_alive() and (time.time() - start_time) < self.timeout:
            time.sleep(0.05)
        execution_time = time.time() - time_start

        if process.is_alive():
            log.warning(f"Process for engine '{engine_name}' timed out after {self.timeout} seconds")
            process.terminate()
            process.join(timeout=1)  # Wait for a short time to allow termination

            if process.is_alive():
                log.warning(f"Process for engine '{engine_name}' did not terminate, killing it")
                process.kill()
                process.join()

            return [], f"Timeout exceeded: {self.timeout} seconds", execution_time

        if not result_queue.empty():
            matches, error, _ = result_queue.get()
            return matches, error, execution_time

        log.error(f"Process for engine '{engine_name}' finished without returning a result")
        return [], "No result returned from engine", execution_time
