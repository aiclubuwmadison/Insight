def search_8(nums, needle):
    left = 0
    right = len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == needle:
            return mid
        if nums[mid] < needle:
            left = mid + 1
        else:
            right = mid - 1
    return -1
