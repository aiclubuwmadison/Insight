def binary_search_31(items, target):
    def helper(lo, hi):
        if lo > hi:
            return -1
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] > target:
            return helper(lo, mid - 1)
        return helper(mid + 1, hi)
    return helper(0, len(items) - 1)
