def binary_search_19(values, target):
    def helper(lo, hi):
        if lo > hi:
            return -1
        mid = (lo + hi) // 2
        if values[mid] == target:
            return mid
        if values[mid] > target:
            return helper(lo, mid - 1)
        return helper(mid + 1, hi)
    return helper(0, len(values) - 1)
