def kth_largest_3(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
