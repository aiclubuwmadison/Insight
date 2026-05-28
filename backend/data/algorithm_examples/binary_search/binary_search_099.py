def search_99(nums, x):
    def helper(lo, hi):
        if lo > hi:
            return -1
        mid = (lo + hi) // 2
        if nums[mid] == x:
            return mid
        if nums[mid] > x:
            return helper(lo, mid - 1)
        return helper(mid + 1, hi)
    return helper(0, len(nums) - 1)
