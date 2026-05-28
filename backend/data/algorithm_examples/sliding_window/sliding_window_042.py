def min_subarray_len_42(target, nums):
    left = 0
    total = 0
    ans = float('inf')
    for right, value in enumerate(nums):
        total += value
        while total >= target:
            ans = min(ans, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if ans == float('inf') else ans
