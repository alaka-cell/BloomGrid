import random
import string

from linear_ds import LinkedList, Stack, Queue
from bloom_filter import BloomFilter
from hierarchical_ds import BST, CollisionGraph
from search_sort import benchmark_membership_check, print_comparison_table, merge_sort
from greedy_allocator import FilterProfile, greedy_allocate, report as greedy_report


def random_username(length=8):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def run_demo(n_unique=500, n_duplicates=150):
    print("=" * 60)
    print("BLOOMGUARD DEMO — Duplicate/Membership Detection System")
    print("=" * 60)

    # ---- Setup structures ----
    log = LinkedList()
    ops_trace = Stack()
    incoming = Queue()
    bloom = BloomFilter(n_items=n_unique, false_positive_rate=0.02)
    bst = BST()
    item_positions = {}  # for the collision graph later

    # ---- Build a stream: unique items + deliberate duplicates ----
    unique_items = [random_username() for _ in range(n_unique)]
    stream = unique_items + random.choices(unique_items, k=n_duplicates)
    random.shuffle(stream)
    for item in stream:
        incoming.enqueue(item)

    print(f"\nStreaming {len(stream)} items ({n_unique} unique, "
          f"{n_duplicates} deliberate duplicates)...\n")

    # ---- Process the stream ----
    false_positives = 0
    true_new = 0
    duplicates_caught = 0

    while not incoming.is_empty():
        item = incoming.dequeue()

        probably_seen = bloom.might_contain(item)
        actually_seen, _ = bst.search(item)

        if probably_seen and not actually_seen:
            false_positives += 1  

        if actually_seen:
            duplicates_caught += 1
        else:
            true_new += 1
            positions = bloom.add(item)
            bst.insert(item)
            log.append(item)
            ops_trace.push(("ADD", item, positions))
            item_positions[item] = set(positions)

    print(f"New items added: {true_new}")
    print(f"Duplicates correctly caught: {duplicates_caught}")
    print(f"False positives (Bloom said seen, wasn't really): {false_positives}")
    print(f"\nBloom filter stats: {bloom.stats()}")
    print(f"\nLast 3 operations on stack (most recent first):")
    for op in ops_trace.trace()[:3]:
        print("  ", op[0], op[1])

    print("\n--- Collision Graph (Phase 2) ---")
    graph = CollisionGraph()
    graph.build_from_positions(item_positions)
    clusters = graph.connected_clusters()
    multi_item_clusters = [c for c in clusters if len(c) > 1]
    print(f"Total items in graph: {len(item_positions)}")
    print(f"Clusters with bit-sharing (FP risk groups): {len(multi_item_clusters)}")
    if multi_item_clusters:
        print("  Example cluster:", multi_item_clusters[0][:5])

    print("\n--- Search & Sort Benchmark (Phase 3) ---")
    sample_target = log.to_list()[len(log) // 2]  # pick a real item
    results = benchmark_membership_check(log.to_list(), bst, bloom, sample_target)
    print_comparison_table(results)

    print("\n--- Greedy Bit Allocation (Phase 4) ---")
    profiles = [
        FilterProfile("usernames", expected_items=n_unique, cost_weight=1.0),
        FilterProfile("emails", expected_items=n_unique // 3, cost_weight=2.0),
        FilterProfile("urls", expected_items=n_unique * 4, cost_weight=0.5),
    ]
    greedy_allocate(profiles, total_bit_budget=300_000, chunk_size=2000)
    greedy_report(profiles)

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
