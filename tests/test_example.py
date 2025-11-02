import pytest

def test_add_positive_numbers():
    """Tests addition with positive numbers."""
    assert 2+3 == 5

def test_add_negative_numbers():
    """Tests addition with negative numbers."""
    assert -2-3 == -5

def test_subtract_basic():
    """Tests basic subtraction."""
    assert 10-4 == 5