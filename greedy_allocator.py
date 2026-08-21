import math


class FilterProfile:

    def __init__(self, name, expected_items, cost_weight=1.0):
        self.name = name
        self.n = expected_items          
        self.cost_weight = cost_weight   
        self.bits_allocated = 0

    def fp_rate(self):
        if self.bits_allocated == 0 or self.n == 0:
            return 1.0
        k = max(1, round((self.bits_allocated / self.n) * math.log(2)))
        return (1 - math.exp(-k * self.n / self.bits_allocated)) ** k

    def marginal_gain(self, extra_bits):
        current = self.fp_rate()
        self.bits_allocated += extra_bits
        improved = self.fp_rate()
        self.bits_allocated -= extra_bits
        return (current - improved) * self.cost_weight


def greedy_allocate(profiles, total_bit_budget, chunk_size=1000):
    remaining = total_bit_budget
    floor = chunk_size
    for p in profiles:
        p.bits_allocated = floor
        remaining -= floor

    while remaining >= chunk_size:
        best = max(profiles, key=lambda p: p.marginal_gain(chunk_size))
        best.bits_allocated += chunk_size
        remaining -= chunk_size

    return {p.name: p.bits_allocated for p in profiles}


def report(profiles):
    print(f"{'Filter':<12}{'Bits':<10}{'Items':<8}{'FP Rate':<10}")
    print("-" * 40)
    for p in profiles:
        print(f"{p.name:<12}{p.bits_allocated:<10}{p.n:<8}{p.fp_rate():.5f}")


if __name__ == "__main__":
    profiles = [
        FilterProfile("usernames", expected_items=5000, cost_weight=1.0),
        FilterProfile("emails", expected_items=2000, cost_weight=2.0),   
        FilterProfile("urls", expected_items=20000, cost_weight=0.5),
    ]

    allocation = greedy_allocate(profiles, total_bit_budget=200_000, chunk_size=2000)
    print("Allocation:", allocation)
    report(profiles)
