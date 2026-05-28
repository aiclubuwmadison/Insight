def find_target_28(values, x):
    left = 0
    right = len(values) - 1
    while left <= right:
        mid = (left + right) // 2
        if values[mid] == x:
            return mid
        if values[mid] < x:
            left = mid + 1
        else:
            right = mid - 1
    return -1
