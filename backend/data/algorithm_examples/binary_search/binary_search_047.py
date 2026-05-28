def search_47(items, needle):
    def helper(lo, hi):
        if lo > hi:
            return -1
        mid = (lo + hi) // 2
        if items[mid] == needle:
            return mid
        if items[mid] > needle:
            return helper(lo, mid - 1)
        return helper(mid + 1, hi)
    return helper(0, len(items) - 1)
