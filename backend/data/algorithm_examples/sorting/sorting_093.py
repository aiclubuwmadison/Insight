def kth_largest_93(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
