def kth_largest_43(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
