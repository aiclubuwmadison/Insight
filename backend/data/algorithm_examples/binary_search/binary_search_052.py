def binary_search_52(values, needle):
    left = 0
    right = len(values) - 1
    while left <= right:
        mid = (left + right) // 2
        if values[mid] == needle:
            return mid
        if values[mid] < needle:
            left = mid + 1
        else:
            right = mid - 1
    return -1
