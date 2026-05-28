def kth_largest_23(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
