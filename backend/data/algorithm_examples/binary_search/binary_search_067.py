def find_target_67(arr, x):
    def helper(lo, hi):
        if lo > hi:
            return -1
        mid = (lo + hi) // 2
        if arr[mid] == x:
            return mid
        if arr[mid] > x:
            return helper(lo, mid - 1)
        return helper(mid + 1, hi)
    return helper(0, len(arr) - 1)
