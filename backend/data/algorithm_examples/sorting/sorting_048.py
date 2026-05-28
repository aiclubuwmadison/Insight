def kth_largest_48(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
