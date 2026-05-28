def first_ge_44(arr, needle):
    left = 0
    right = len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == needle:
            return mid
        if arr[mid] < needle:
            left = mid + 1
        else:
            right = mid - 1
    return -1
