import pytest  # type: ignore

from src.slot import Slot


def test_slot_transitions():
    s = Slot(index=0, level=1, fuel="ICE")
    assert s.is_vacant
    s.occupy(object())
    assert not s.is_vacant
    with pytest.raises(ValueError):
        s.occupy(object())
    s.free()
    assert s.is_vacant
    with pytest.raises(ValueError):
        s.free()
