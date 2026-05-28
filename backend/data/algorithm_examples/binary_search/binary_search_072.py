def find_target_72(nums, x):
    left = 0
    right = len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == x:
            return mid
        if nums[mid] < x:
            left = mid + 1
        else:
            right = mid - 1
    return -1
