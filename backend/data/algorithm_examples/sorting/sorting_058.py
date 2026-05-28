def kth_largest_58(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
