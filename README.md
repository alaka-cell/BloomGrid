# BloomGuard — Duplicate/Membership Detection System

A Bloom filter–based duplicate detection system, built from scratch with
supporting data structures across four phases. No external DSA libraries —
only Python's standard `hashlib`, `math`, `time`.

## How to run

```bash
python3 main.py
```

This runs the full pipeline: streams items through a Queue, checks them
against the Bloom filter + BST, logs everything to a LinkedList, tracks
operations on a Stack, builds a collision Graph, benchmarks 4 search
strategies, and runs the Phase 4 greedy allocator.

You can also run any module standalone to see just that phase:
```bash
python3 linear_ds.py         # Phase 1
python3 hierarchical_ds.py   # Phase 2
python3 search_sort.py       # Phase 3
python3 greedy_allocator.py  # Phase 4
python3 bloom_filter.py      # Core Bloom filter
```

## File structure

| File | Phase | What it does |
|---|---|---|
| `linear_ds.py` | Phase 1 | LinkedList (item log), Stack (op trace/undo), Queue (input buffer) |
| `bloom_filter.py` | Core | BloomFilter + CountingBloomFilter (supports deletion) |
| `hierarchical_ds.py` | Phase 2 | BST (exact verifier), CollisionGraph (BFS/DFS over shared bit positions) |
| `search_sort.py` | Phase 3 | Linear search, binary search, merge sort, 4-way benchmark |
| `greedy_allocator.py` | Phase 4 | Greedy bit-budget allocation across multiple filters |
| `main.py` | Integration | Wires all phases into one streaming pipeline + demo |

## How each requirement is satisfied

- **Linked list + basic ops**: `LinkedList` in `linear_ds.py` — append, delete, search, traverse.
- **Stack/Queue via linked list**: both built directly on the `Node` class, not Python lists.
- **Stack for execution trace**: every `bloom.add()` call is pushed with its bit positions, so you can print/undo the operation history.
- **Binary tree + traversal**: `BST` class with inorder/preorder in `hierarchical_ds.py`.
- **BST for efficient access**: doubles as the "ground truth" — used to measure the Bloom filter's real false-positive rate during the demo.
- **Graph + traversal**: `CollisionGraph` connects items sharing bit positions; BFS/DFS find clusters prone to false positives.
- **Linear & binary search**: both implemented from scratch in `search_sort.py`, benchmarked against BST and Bloom filter.
- **Sorting**: merge sort implemented from scratch, used as a prerequisite for binary search.
- **Performance comparison**: `benchmark_membership_check()` runs the same query 4 ways and reports steps + microseconds.
- **Greedy algorithm**: `greedy_allocator.py` distributes a fixed bit budget across multiple filters by marginal false-positive-rate improvement.
- **Integration + demo**: `main.py` streams 650 items (mix of unique + duplicates) through the full pipeline and prints a report at each stage.

## Web frontend

A Flask dashboard sits on top of the same modules — it doesn't reimplement
anything, it just calls into `system.py`, which wraps all four phases in
one stateful class the API can drive.

### Run it

```bash
pip install flask
python3 app.py
```

Then open **http://localhost:5000**.

### What's on the dashboard

- **Hero bit-array grid** — the actual Bloom filter bit array, live. Cells
  light up teal as items get added. This is the real internal state, not a
  mock-up (sampled down to a fixed grid if `m` is large).
- **Feed an item / seed 50 random / reset** — drives `add_item()`, which
  runs the same Bloom-check → BST-verify → log → stack-trace flow as the
  CLI demo.
- **Activity feed** — tags each item `added`, `duplicate`, or
  `false positive` in real time.
- **Operation trace & BST inorder** — Phase 1's stack, Phase 2's BST,
  rendered live.
- **Collision graph** — Phase 2's graph, laid out in a simple circular SVG
  (no charting library needed) with edges between items sharing a bit.
- **Search & sort benchmark** — button that runs Phase 3's four-way
  comparison on a random logged item and shows steps + microseconds.
- **Greedy allocator** — button that runs Phase 4's allocation across three
  hypothetical filter categories and renders it as bars.

### Architecture

```
app.py            Flask routes (thin — just request/response glue)
system.py         BloomGuardSystem: stateful wrapper around all 4 phases
templates/index.html   Dashboard markup
static/style.css       Console/dashboard styling
static/app.js          Fetch calls + canvas/SVG rendering, no frameworks
```

The frontend is plain HTML/CSS/vanilla JS (fetch + canvas + SVG) — no
build step, no npm install, so it's simple to demo from a single
`python3 app.py`. State lives in one in-memory `BloomGuardSystem`
instance on the server, which is fine for a single-demo-session project;
note it isn't safe for concurrent multi-user access as written.

## Extending it

- Swap `greedy_allocator.py` for a DP (knapsack-style) version and compare whether greedy matches optimal.
- Use `CountingBloomFilter` in `bloom_filter.py` to support real deletions (already implemented, just swap the import in `main.py`).
- Add `matplotlib` to plot false-positive rate vs. fill ratio as more items are added.
