import time
from typing import List, Tuple, Optional, ContextManager


class PerfUtil:
    """
    Utility for measuring elapsed time of code blocks or operations.
    Supports context manager usage and manual start/stop.

    Example (manual):
        p = PerfUtil("my task", auto_print=False)
        p.start()
        ... # code to time
        p.stop()
        print(p.format())

    Example (context manager):
        with PerfUtil("my task") as p:
            ... # code to time

    Example (collection):
        timings = []
        with PerfUtil.collect("label", timings):
            ... # code to time
        PerfUtil.report_table(timings)
    """

    def __init__(self, label=None, auto_print=True):
        self.label = label or "PerfUtil"
        self.auto_print = auto_print
        self._start = None
        self._end = None
        self.elapsed = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        if self.auto_print:
            print(self.format())

    def start(self):
        """
        Start or restart the timer. Resets any previous timing.
        """
        self._start = time.perf_counter()
        self._end = None
        self.elapsed = None

    def stop(self):
        """
        Stop the timer and record the elapsed time. Idempotent: calling multiple times returns the same result.
        Returns the elapsed time in seconds.
        """
        if self._start is None:
            raise RuntimeError("PerfUtil: start() must be called before stop().")
        if self.elapsed is not None:
            return self.elapsed
        self._end = time.perf_counter()
        self.elapsed = self._end - self._start
        return self.elapsed

    def format(self):
        if self.elapsed is None:
            return f"{self.label}: timer not stopped yet."
        return f"{self.label}: {self.elapsed:.3f} seconds elapsed"

    def get(self):
        """Return the elapsed time in seconds, or None if not stopped."""
        return self.elapsed

    @staticmethod
    def report_table(timings: List[Tuple[str, float]], label: Optional[str] = None):
        """
        Print a formatted table of timings. Each entry is (label, elapsed).
        """
        if label:
            print(f"\n{label}")
        print("\nTiming Summary:")
        print(f"  {'Label':<40} | {'Elapsed (sec)':>12}")
        print("  " + "-" * 57)
        for lbl, elapsed in timings:
            print(f"  {lbl[:40]:<40} | {elapsed:12.4f}")

    @staticmethod
    def collect(
        label: str, timings: List[Tuple[str, float]], auto_print: bool = False
    ) -> ContextManager["PerfUtil"]:
        """
        Context manager that yields a PerfUtil and appends (label, elapsed) to timings on exit.
        """

        class _Collector:
            def __init__(self, label, timings, auto_print):
                self.perf = PerfUtil(label, auto_print=auto_print)
                self.timings = timings
                self.label = label

            def __enter__(self):
                self.perf.start()
                return self.perf

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.perf.stop()
                self.timings.append((self.label, self.perf.get()))

        return _Collector(label, timings, auto_print)
