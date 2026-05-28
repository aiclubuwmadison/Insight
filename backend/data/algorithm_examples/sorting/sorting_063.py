def kth_largest_63(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
