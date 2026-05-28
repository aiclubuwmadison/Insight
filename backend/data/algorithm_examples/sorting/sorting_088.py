def kth_largest_88(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
