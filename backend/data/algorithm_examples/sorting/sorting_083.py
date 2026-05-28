def kth_largest_83(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
