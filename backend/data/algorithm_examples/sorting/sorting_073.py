def kth_largest_73(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
