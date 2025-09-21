from src.slot import Slot

def test_slot_transitions():
    s = Slot(index=0, level=1, fuel="ICE")
    assert s.is_vacant
    # Occupy
    s.occupy(object())
    assert not s.is_vacant
    # Double-occupy should fail
    try:
        s.occupy(object())
        assert False, "expected ValueError on occupying an occupied slot"
    except ValueError:
        pass
    # Free
    s.free()
    assert s.is_vacant
    # Double-free should fail
    try:
        s.free()
        assert False, "expected ValueError on freeing a vacant slot"
    except ValueError:
        pass
