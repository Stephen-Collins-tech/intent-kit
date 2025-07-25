"""
Tests for performance utilities.
"""

import pytest
import time
from unittest.mock import patch
from intent_kit.utils.perf_util import PerfUtil


class TestPerfUtil:
    """Test cases for PerfUtil class."""

    def test_init_default(self):
        """Test PerfUtil initialization with default parameters."""
        perf = PerfUtil()
        assert perf.label == "PerfUtil"
        assert perf.auto_print is True
        assert perf._start is None
        assert perf._end is None
        assert perf.elapsed is None

    def test_init_custom(self):
        """Test PerfUtil initialization with custom parameters."""
        perf = PerfUtil("custom_label", auto_print=False)
        assert perf.label == "custom_label"
        assert perf.auto_print is False
        assert perf._start is None
        assert perf._end is None
        assert perf.elapsed is None

    def test_start(self):
        """Test start method."""
        perf = PerfUtil("test")
        perf.start()
        assert perf._start is not None
        assert perf._end is None
        assert perf.elapsed is None

    def test_start_resets_previous_timing(self):
        """Test that start resets previous timing."""
        perf = PerfUtil("test")
        perf.start()
        time.sleep(0.001)  # Small delay
        perf.stop()
        first_elapsed = perf.elapsed

        perf.start()
        assert perf._start is not None
        assert perf._end is None
        assert perf.elapsed is None
        assert first_elapsed is not None

    def test_stop_before_start_raises_error(self):
        """Test that stop before start raises RuntimeError."""
        perf = PerfUtil("test")
        with pytest.raises(
            RuntimeError, match="start\\(\\) must be called before stop\\(\\)"
        ):
            perf.stop()

    def test_stop_returns_elapsed_time(self):
        """Test that stop returns elapsed time."""
        perf = PerfUtil("test")
        perf.start()
        time.sleep(0.001)  # Small delay
        elapsed = perf.stop()
        assert isinstance(elapsed, float)
        assert elapsed > 0
        assert elapsed == perf.elapsed

    def test_stop_idempotent(self):
        """Test that stop is idempotent."""
        perf = PerfUtil("test")
        perf.start()
        time.sleep(0.001)  # Small delay
        first_elapsed = perf.stop()
        second_elapsed = perf.stop()
        assert first_elapsed == second_elapsed
        assert perf.elapsed == first_elapsed

    def test_format_not_stopped(self):
        """Test format when timer is not stopped."""
        perf = PerfUtil("test")
        result = perf.format()
        assert result == "test: timer not stopped yet."

    def test_format_stopped(self):
        """Test format when timer is stopped."""
        perf = PerfUtil("test")
        perf.start()
        time.sleep(0.001)  # Small delay
        perf.stop()
        result = perf.format()
        assert "test:" in result
        assert "seconds elapsed" in result
        assert "0.00" in result or "0.001" in result

    def test_get_not_stopped(self):
        """Test get when timer is not stopped."""
        perf = PerfUtil("test")
        assert perf.get() is None

    def test_get_stopped(self):
        """Test get when timer is stopped."""
        perf = PerfUtil("test")
        perf.start()
        time.sleep(0.001)  # Small delay
        perf.stop()
        elapsed = perf.get()
        assert isinstance(elapsed, float)
        assert elapsed > 0

    def test_context_manager(self):
        """Test PerfUtil as context manager."""
        with PerfUtil("context_test") as perf:
            time.sleep(0.001)  # Small delay
            assert perf._start is not None
            assert perf._end is None

        # After context exit, timer should be stopped
        assert perf._end is not None
        assert perf.elapsed is not None
        assert perf.elapsed > 0

    def test_context_manager_auto_print(self):
        """Test PerfUtil context manager with auto_print."""
        with patch("builtins.print") as mock_print:
            with PerfUtil("auto_print_test", auto_print=True):
                time.sleep(0.001)  # Small delay

            # Should have called print once
            assert mock_print.call_count == 1
            call_args = mock_print.call_args[0][0]
            assert "auto_print_test:" in call_args
            assert "seconds elapsed" in call_args

    def test_context_manager_no_auto_print(self):
        """Test PerfUtil context manager without auto_print."""
        with patch("builtins.print") as mock_print:
            with PerfUtil("no_auto_print_test", auto_print=False):
                time.sleep(0.001)  # Small delay

            # Should not have called print
            mock_print.assert_not_called()

    def test_context_manager_exception(self):
        """Test PerfUtil context manager with exception."""
        with pytest.raises(ValueError):
            with PerfUtil("exception_test") as perf:
                time.sleep(0.001)  # Small delay
                raise ValueError("test exception")

        # Timer should still be stopped even with exception
        assert perf._end is not None
        assert perf.elapsed is not None

    @staticmethod
    def test_report_table_empty():
        """Test report_table with empty timings."""
        with patch("builtins.print") as mock_print:
            PerfUtil.report_table([])
            assert (
                mock_print.call_count == 3
            )  # "Timing Summary:", header, and separator

    @staticmethod
    def test_report_table_with_data():
        """Test report_table with timing data."""
        timings = [("task1", 1.234), ("task2", 0.567)]
        with patch("builtins.print") as mock_print:
            PerfUtil.report_table(timings)
            calls = mock_print.call_args_list

            # Should have header, separator, and data rows
            assert len(calls) >= 4
            assert "task1" in str(calls)
            assert "task2" in str(calls)
            assert "1.234" in str(calls)
            assert "0.567" in str(calls)

    @staticmethod
    def test_report_table_with_label():
        """Test report_table with custom label."""
        timings = [("task1", 1.234)]
        with patch("builtins.print") as mock_print:
            PerfUtil.report_table(timings, "Custom Label")
            calls = mock_print.call_args_list

            # Should have label, header, separator, and data
            assert len(calls) >= 4
            assert "Custom Label" in str(calls[0])

    @staticmethod
    def test_collect_context_manager():
        """Test collect static method as context manager."""
        timings = []
        with patch("builtins.print"):
            with PerfUtil.collect("collect_test", timings, auto_print=False):
                time.sleep(0.001)  # Small delay

            # Should have added timing to list
            assert len(timings) == 1
            assert timings[0][0] == "collect_test"
            assert isinstance(timings[0][1], float)
            assert timings[0][1] > 0

    @staticmethod
    def test_collect_with_auto_print():
        """Test collect with auto_print enabled."""
        timings = []
        with patch("builtins.print") as mock_print:
            with PerfUtil.collect("collect_test", timings, auto_print=True):
                time.sleep(0.001)  # Small delay

            # Collector doesn't auto-print, it only collects timings
            # The auto_print parameter is passed to the inner PerfUtil but not used by collector
            assert mock_print.call_count == 0
            assert len(timings) == 1

    @staticmethod
    def test_collect_exception():
        """Test collect with exception."""
        timings = []
        with pytest.raises(ValueError):
            with PerfUtil.collect("collect_test", timings):
                time.sleep(0.001)  # Small delay
                raise ValueError("test exception")

        # Should still have added timing to list
        assert len(timings) == 1
        assert timings[0][0] == "collect_test"
        assert isinstance(timings[0][1], float)

    def test_manual_timing_workflow(self):
        """Test complete manual timing workflow."""
        perf = PerfUtil("manual_test", auto_print=False)

        # Start timing
        perf.start()
        time.sleep(0.001)  # Small delay

        # Stop timing
        elapsed = perf.stop()

        # Verify results
        assert isinstance(elapsed, float)
        assert elapsed > 0
        assert perf.elapsed == elapsed
        assert perf.get() == elapsed

        # Format should work
        formatted = perf.format()
        assert "manual_test:" in formatted
        assert "seconds elapsed" in formatted

    def test_multiple_starts_and_stops(self):
        """Test multiple start/stop cycles."""
        perf = PerfUtil("multi_test")

        # First cycle
        perf.start()
        time.sleep(0.001)
        first_elapsed = perf.stop()

        # Second cycle
        perf.start()
        time.sleep(0.002)
        second_elapsed = perf.stop()

        # Verify both timings are valid
        assert isinstance(first_elapsed, float)
        assert isinstance(second_elapsed, float)
        assert first_elapsed > 0
        assert second_elapsed > 0
        assert second_elapsed > first_elapsed

    def test_very_short_timing(self):
        """Test timing for very short operations."""
        perf = PerfUtil("short_test")
        perf.start()
        perf.stop()

        # Even very short operations should have some elapsed time
        assert perf.elapsed is not None
        assert perf.elapsed >= 0
        assert isinstance(perf.elapsed, float)

    def test_label_with_special_characters(self):
        """Test PerfUtil with labels containing special characters."""
        perf = PerfUtil("test-label_with_underscores: 123")
        perf.start()
        perf.stop()

        formatted = perf.format()
        assert "test-label_with_underscores: 123:" in formatted

    def test_zero_duration_timing(self):
        """Test timing when start and stop are called immediately."""
        perf = PerfUtil("zero_test")
        perf.start()
        perf.stop()

        # Should have very small but non-zero elapsed time
        assert perf.elapsed is not None
        assert perf.elapsed >= 0
        assert isinstance(perf.elapsed, float)
