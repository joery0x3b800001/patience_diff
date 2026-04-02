"""Move ID - unique identifier for moves in diffs."""


class MoveId:
    """A unique identifier for each move identified in the code."""
    
    def __init__(self, value: int = 0):
        """Initialize a MoveId with an integer value."""
        if not isinstance(value, int):
            raise TypeError(f"Expected int, got {type(value)}")
        self.value = value
    
    def __eq__(self, other):
        if not isinstance(other, MoveId):
            return False
        return self.value == other.value
    
    def __hash__(self):
        return hash(self.value)
    
    def __lt__(self, other):
        if not isinstance(other, MoveId):
            return NotImplemented
        return self.value < other.value
    
    def __le__(self, other):
        if not isinstance(other, MoveId):
            return NotImplemented
        return self.value <= other.value
    
    def __gt__(self, other):
        if not isinstance(other, MoveId):
            return NotImplemented
        return self.value > other.value
    
    def __ge__(self, other):
        if not isinstance(other, MoveId):
            return NotImplemented
        return self.value >= other.value
    
    def __repr__(self):
        return f"MoveId({self.value})"
    
    def __str__(self):
        return str(self.value)
    
    @staticmethod
    def zero():
        """Return the 0th move index."""
        return MoveId(0)
    
    def succ(self):
        """Get the next move index."""
        return MoveId(self.value + 1)
    
    def to_string(self):
        """Convert to string representation."""
        return str(self.value)
