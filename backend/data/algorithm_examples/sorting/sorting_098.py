def kth_largest_98(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
