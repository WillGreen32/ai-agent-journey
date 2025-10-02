# counter_demo.py

class Counter:
    """
    Counter with:
      - instance state: name, count
      - class state: total_counters, total_increments (across all instances)
      - static validation to keep inputs clean
    """
    # ---- class attributes (shared by all instances)
    total_counters = 0
    total_increments = 0

    def __init__(self, name: str, initial: int = 0):
        # validate once on creation
        if not self.validate_number(initial):
            raise ValueError("initial must be a non-negative integer")
        self.name = name            # instance attribute
        self.count = initial        # instance attribute
        # increment class-level tracker
        Counter.total_counters += 1

    # ---- instance method (affects only THIS object)
    def increment(self, step: int = 1) -> int:
        if not self.validate_number(step):
            raise ValueError("step must be a non-negative integer")
        self.count += step
        Counter.total_increments += step
        return self.count

    def decrement(self, step: int = 1) -> int:
        if not self.validate_number(step):
            raise ValueError("step must be a non-negative integer")
        # keep non-negative invariant
        if self.count - step < 0:
            raise ValueError("cannot decrement below 0")
        self.count -= step
        # we don't add to total_increments here (that metric is “ups” only)
        return self.count

    def reset(self) -> None:
        # decide: should class totals change? No — we treat them as historical.
        self.count = 0

    # ---- class methods (operate on the CLASS, not a specific instance)
    @classmethod
    def get_stats(cls) -> dict:
        """Snapshot of class-wide stats."""
        return {
            "total_counters": cls.total_counters,
            "total_increments": cls.total_increments,
            "avg_increments_per_counter": (
                cls.total_increments / cls.total_counters if cls.total_counters else 0
            ),
        }

    @classmethod
    def zero_all_metrics(cls) -> None:
        """Reset class-wide metrics (rarely used; for tests/demos)."""
        cls.total_counters = 0
        cls.total_increments = 0

    # ---- static methods (utility; no self/cls)
    @staticmethod
    def validate_number(n) -> bool:
        """Accepts non-negative integers only."""
        return isinstance(n, int) and n >= 0

    # ---- nice-to-haves
    def __repr__(self) -> str:
        return f"Counter(name='{self.name}', count={self.count})"


if __name__ == "__main__":
    # quick demo
    Counter.zero_all_metrics()  # start clean for reproducible out
if __name__ == "__main__":
    # Reset class metrics for a clean run
    Counter.zero_all_metrics()

    # --- Test 1: Instance method (object-specific state) ---
    a = Counter("Alice")
    b = Counter("Bob", 2)

    print("Test 1 — Instance Methods")
    print("a.increment():", a.increment())          # Alice → 1
    print("b.increment():", b.increment())          # Bob → 3
    print("a.count (should be 1):", a.count)
    print("b.count (should be 3):", b.count)
    print()

    # --- Test 2: Class method (shared state across ALL objects) ---
    print("Test 2 — Class Methods")
    print("Total counters created:", Counter.get_stats()["total_counters"])      # 2
    print("Total increments across all:", Counter.get_stats()["total_increments"])  # 2
    print()

    # --- Test 3: Static method (independent helper) ---
    print("Test 3 — Static Methods")
    print("Validate 5:", Counter.validate_number(5))     # True
    print("Validate -1:", Counter.validate_number(-1))   # False
    print("Validate 'x':", Counter.validate_number("x")) # False
    print()

    # --- Test 4: Prove independence vs sharing ---
    print("Test 4 — Independence vs Sharing")
    c = Counter("Charlie")
    print("Charlie's count (before):", c.count)          # 0
    c.increment(4)
    print("Charlie's count (after increment):", c.count) # 4
    print("Class-wide stats after Charlie joined:", Counter.get_stats())
