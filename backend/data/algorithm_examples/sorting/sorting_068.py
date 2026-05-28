def kth_largest_68(nums, k):
    nums = sorted(nums, reverse=True)
    return nums[k - 1]
