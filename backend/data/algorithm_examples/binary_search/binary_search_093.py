def last_le_93(items, needle):
    lo, hi = 0, len(items)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if items[mid] < needle:
            lo = mid + 1
        else:
            hi = mid
    return lo
