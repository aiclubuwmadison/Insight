def kth_largest_33(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
