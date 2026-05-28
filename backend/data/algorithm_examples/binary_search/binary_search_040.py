def binary_search_40(items, needle):
    left = 0
    right = len(items) - 1
    while left <= right:
        mid = (left + right) // 2
        if items[mid] == needle:
            return mid
        if items[mid] < needle:
            left = mid + 1
        else:
            right = mid - 1
    return -1
