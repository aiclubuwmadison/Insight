def lower_bound_23(items, x):
    def helper(lo, hi):
        if lo > hi:
            return -1
        mid = (lo + hi) // 2
        if items[mid] == x:
            return mid
        if items[mid] > x:
            return helper(lo, mid - 1)
        return helper(mid + 1, hi)
    return helper(0, len(items) - 1)
