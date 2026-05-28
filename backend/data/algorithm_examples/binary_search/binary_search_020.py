def last_le_20(items, x):
    left = 0
    right = len(items) - 1
    while left <= right:
        mid = (left + right) // 2
        if items[mid] == x:
            return mid
        if items[mid] < x:
            left = mid + 1
        else:
            right = mid - 1
    return -1
