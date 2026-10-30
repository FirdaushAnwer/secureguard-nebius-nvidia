import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import average, total

def test_average_normal():
    assert average([2, 4, 6]) == 4.0

def test_average_empty():
    assert average([]) == 0.0  # fails due to bug — agent must fix this

def test_total():
    assert total([1, 2, 3]) == 6
