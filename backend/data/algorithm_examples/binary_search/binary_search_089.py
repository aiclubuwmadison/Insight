def binary_search_89(values, x):
    lo, hi = 0, len(values)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if values[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo
