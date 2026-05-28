def find_target_95(values, needle):
    def helper(lo, hi):
        if lo > hi:
            return -1
        mid = (lo + hi) // 2
        if values[mid] == needle:
            return mid
        if values[mid] > needle:
            return helper(lo, mid - 1)
        return helper(mid + 1, hi)
    return helper(0, len(values) - 1)
