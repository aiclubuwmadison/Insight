def kth_largest_53(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
