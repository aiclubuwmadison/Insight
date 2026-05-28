def first_ge_55(arr, needle):
    def helper(lo, hi):
        if lo > hi:
            return -1
        mid = (lo + hi) // 2
        if arr[mid] == needle:
            return mid
        if arr[mid] > needle:
            return helper(lo, mid - 1)
        return helper(mid + 1, hi)
    return helper(0, len(arr) - 1)
