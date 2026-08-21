import time


def linear_search(arr, target):
    steps = 0
    for i, val in enumerate(arr):
        steps += 1
        if val == target:
            return i, steps
    return -1, steps


def binary_search(sorted_arr, target):
    lo, hi, steps = 0, len(sorted_arr) - 1, 0
    while lo <= hi:
        steps += 1
        mid = (lo + hi) // 2
        if sorted_arr[mid] == target:
            return mid, steps
        elif sorted_arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, steps


def merge_sort(arr):
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left, right):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def benchmark_membership_check(log_list, bst, bloom, target, timing=True):
    results = {}

    t0 = time.perf_counter()
    found, steps = linear_search(log_list, target)
    results["linked_list_linear_search"] = {
        "found": found != -1, "steps": steps,
        "time_us": round((time.perf_counter() - t0) * 1e6, 2),
    }

    t0 = time.perf_counter()
    sorted_log = merge_sort(log_list)
    idx, steps = binary_search(sorted_log, target)
    results["sorted_array_binary_search"] = {
        "found": idx != -1, "steps": steps,
        "time_us": round((time.perf_counter() - t0) * 1e6, 2),
    }

    t0 = time.perf_counter()
    found, steps = bst.search(target)
    results["bst_search"] = {
        "found": found, "steps": steps,
        "time_us": round((time.perf_counter() - t0) * 1e6, 2),
    }

    t0 = time.perf_counter()
    found = bloom.might_contain(target)
    results["bloom_filter_check"] = {
        "found": found, "steps": bloom.k,  
        "time_us": round((time.perf_counter() - t0) * 1e6, 2),
    }

    return results


def print_comparison_table(results):
    print(f"{'Method':<30}{'Found':<8}{'Steps':<8}{'Time (µs)':<12}")
    print("-" * 58)
    for method, r in results.items():
        print(f"{method:<30}{str(r['found']):<8}{r['steps']:<8}{r['time_us']:<12}")


if __name__ == "__main__":
    from bloom_filter import BloomFilter
    from hierarchical_ds import BST

    names = ["mango", "apple", "banana", "kiwi", "grape", "peach"]

    bst = BST()
    bloom = BloomFilter(n_items=100, false_positive_rate=0.01)
    for n in names:
        bst.insert(n)
        bloom.add(n)

    results = benchmark_membership_check(names, bst, bloom, "banana")
    print_comparison_table(results)
