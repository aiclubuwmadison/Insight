def last_le_97(nums, x):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo
