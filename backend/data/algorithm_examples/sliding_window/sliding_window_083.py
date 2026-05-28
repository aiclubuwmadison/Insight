def count_windows_83(nums, k, limit):
    total = 0
    count = 0
    left = 0
    for right, value in enumerate(nums):
        total += value
        if right - left + 1 > k:
            total -= nums[left]
            left += 1
        if right - left + 1 == k and total <= limit:
            count += 1
    return count
