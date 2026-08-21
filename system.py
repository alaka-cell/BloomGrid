import random
import string

from linear_ds import LinkedList, Stack, Queue
from bloom_filter import BloomFilter
from hierarchical_ds import BST, CollisionGraph
from search_sort import benchmark_membership_check
from greedy_allocator import FilterProfile, greedy_allocate


def random_username(length=8):
    return "".join(random.choices(string.ascii_lowercase, k=length))


class BloomGuardSystem:
    def __init__(self, n_items=500, fp_rate=0.02):
        self.n_items = n_items
        self.fp_rate = fp_rate
        self.reset()

    def reset(self, n_items=None, fp_rate=None):
        self.n_items = n_items or self.n_items
        self.fp_rate = fp_rate or self.fp_rate
        self.log = LinkedList()
        self.ops_trace = Stack()
        self.bloom = BloomFilter(n_items=self.n_items, false_positive_rate=self.fp_rate)
        self.bst = BST()
        self.item_positions = {}
        self.false_positives = 0
        self.duplicates_caught = 0
        self.recent_events = [] 


    def add_item(self, item: str):
        item = item.strip()
        if not item:
            return {"error": "empty item"}

        probably_seen = self.bloom.might_contain(item)
        actually_seen, _ = self.bst.search(item)

        event = {"item": item}

        if actually_seen:
            self.duplicates_caught += 1
            event.update(status="duplicate", is_new=False, was_false_positive=False)
        else:
            if probably_seen:
                self.false_positives += 1
                event["was_false_positive"] = True
            else:
                event["was_false_positive"] = False
            positions = self.bloom.add(item)
            self.bst.insert(item)
            self.log.append(item)
            self.ops_trace.push(("ADD", item, positions))
            self.item_positions[item] = set(positions)
            event.update(status="added", is_new=True, positions=positions)

        self.recent_events.insert(0, event)
        self.recent_events = self.recent_events[:25]
        return event

    def seed_random(self, count=50, duplicate_ratio=0.25):
        added = 0
        for _ in range(count):
            if self.log.size > 0 and random.random() < duplicate_ratio:
                item = random.choice(self.log.to_list())
            else:
                item = random_username()
            self.add_item(item)
            added += 1
        return {"seeded": added}


    def stats(self):
        s = self.bloom.stats()
        s.update(
            duplicates_caught=self.duplicates_caught,
            false_positives=self.false_positives,
            log_size=self.log.size,
        )
        return s

    def bit_array_preview(self, max_bits=400):
        arr = self.bloom.bit_array
        m = len(arr)
        if m <= max_bits:
            return {"bits": arr, "sampled": False, "actual_size": m}
        bucket_size = m / max_bits
        buckets = []
        for i in range(max_bits):
            lo = int(i * bucket_size)
            hi = int((i + 1) * bucket_size) or lo + 1
            buckets.append(1 if any(arr[lo:hi]) else 0)
        return {"bits": buckets, "sampled": True, "actual_size": m}

    def log_items(self):
        return self.log.to_list()

    def recent(self):
        return self.recent_events

    def stack_trace(self, limit=10):
        return [{"op": t[0], "item": t[1]} for t in self.ops_trace.trace()[:limit]]


    def collision_graph(self, max_nodes=60):
        graph = CollisionGraph()
        graph.build_from_positions(self.item_positions)
        clusters = graph.connected_clusters()

        nodes, edges = [], []
        seen_edges = set()
        node_count = 0
        for item in graph.adjacency:
            if node_count >= max_nodes:
                break
            nodes.append(item)
            node_count += 1
        node_set = set(nodes)
        for a in nodes:
            for b in graph.adjacency[a]:
                if b in node_set:
                    edge = tuple(sorted((a, b)))
                    if edge not in seen_edges:
                        seen_edges.add(edge)
                        edges.append({"source": edge[0], "target": edge[1]})

        return {
            "nodes": [{"id": n} for n in nodes],
            "edges": edges,
            "total_items": len(self.item_positions),
            "cluster_count": len([c for c in clusters if len(c) > 1]),
        }

    def bst_traversal(self):
        return self.bst.inorder()


    def run_benchmark(self, target=None):
        items = self.log.to_list()
        if not items:
            return {"error": "no items yet"}
        target = target or random.choice(items)
        results = benchmark_membership_check(items, self.bst, self.bloom, target)
        return {"target": target, "results": results}


    def run_greedy(self, total_budget=300_000, chunk_size=2000):
        n = max(1, self.log.size)
        profiles = [
            FilterProfile("usernames", expected_items=n, cost_weight=1.0),
            FilterProfile("emails", expected_items=max(1, n // 3), cost_weight=2.0),
            FilterProfile("urls", expected_items=n * 4, cost_weight=0.5),
        ]
        greedy_allocate(profiles, total_bit_budget=total_budget, chunk_size=chunk_size)
        return [
            {
                "name": p.name,
                "bits": p.bits_allocated,
                "items": p.n,
                "fp_rate": round(p.fp_rate(), 6),
            }
            for p in profiles
        ]
