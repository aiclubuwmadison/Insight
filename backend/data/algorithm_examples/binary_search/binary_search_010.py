def lower_bound_10(nums, needle):
    low = 0
    high = len(nums) - 1
    ans = -1
    while low <= high:
        middle = (low + high) // 2
        if nums[middle] <= needle:
            ans = middle
            low = middle + 1
        else:
            high = middle - 1
    return ans
