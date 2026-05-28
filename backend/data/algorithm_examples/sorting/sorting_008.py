def kth_largest_8(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
