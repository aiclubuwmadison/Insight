def kth_largest_38(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
