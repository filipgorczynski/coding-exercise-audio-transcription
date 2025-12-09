"""Tests for the interval_overlap function."""

import pytest

from services.transcription_service import interval_overlap


class TestIntervalOverlap:
    """Test the interval_overlap function with various edge cases."""

    @pytest.mark.parametrize(
        "segment_start,segment_end,turn_start,turn_end,expected",
        [
            # Perfect overlap - segment contained in turn
            (1.0, 3.0, 0.0, 5.0, 2.0),
            # Perfect overlap - turn contained in segment
            (0.0, 5.0, 1.0, 3.0, 2.0),
            # Partial overlap - segment starts before turn
            (0.0, 3.0, 2.0, 5.0, 1.0),
            # Partial overlap - segment starts after turn
            (2.0, 5.0, 0.0, 3.0, 1.0),
            # No overlap - segment ends before turn starts
            (0.0, 1.0, 2.0, 3.0, 0.0),
            # No overlap - segment starts after turn ends
            (2.0, 3.0, 0.0, 1.0, 0.0),
            # Edge case - exact boundary (segment end == turn start)
            (0.0, 2.0, 2.0, 4.0, 0.0),
            # Edge case - exact boundary (segment start == turn end)
            (2.0, 4.0, 0.0, 2.0, 0.0),
            # Edge case - identical intervals
            (1.0, 3.0, 1.0, 3.0, 2.0),
            # Edge case - single point overlap
            (1.0, 2.5, 2.0, 3.0, 0.5),
            # Edge case - zero-duration segment
            (2.0, 2.0, 1.0, 3.0, 0.0),
            # Edge case - zero-duration turn
            (1.0, 3.0, 2.0, 2.0, 0.0),
            # Floating point precision
            (1.23, 4.56, 2.34, 5.67, 2.22),
            # Small overlap (< min_overlap threshold)
            (1.0, 1.05, 1.04, 2.0, 0.01),
        ],
        ids=[
            "segment_contained_in_turn",
            "turn_contained_in_segment",
            "partial_overlap_segment_first",
            "partial_overlap_turn_first",
            "no_overlap_segment_before",
            "no_overlap_segment_after",
            "boundary_segment_end_turn_start",
            "boundary_segment_start_turn_end",
            "identical_intervals",
            "single_point_overlap",
            "zero_duration_segment",
            "zero_duration_turn",
            "floating_point_precision",
            "small_overlap",
        ],
    )
    def test_interval_overlap_scenarios(
        self, segment_start, segment_end, turn_start, turn_end, expected
    ):
        """Test interval overlap calculation for various scenarios."""
        result = interval_overlap(segment_start, segment_end, turn_start, turn_end)
        assert pytest.approx(result, abs=0.01) == expected

    def test_interval_overlap_always_non_negative(self):
        """Test that overlap is always >= 0 even with unusual inputs."""
        # This shouldn't happen in practice but test defensive behavior
        result1 = interval_overlap(-1.0, 1.0, 0.0, 2.0)
        assert result1 >= 0.0

        result2 = interval_overlap(5.0, 2.0, 0.0, 3.0)  # End before start
        assert result2 >= 0.0
