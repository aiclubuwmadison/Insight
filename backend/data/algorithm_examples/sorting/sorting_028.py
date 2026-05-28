def kth_largest_28(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
