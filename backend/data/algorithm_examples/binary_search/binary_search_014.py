def binary_search_14(values, x):
    low = 0
    high = len(values) - 1
    ans = -1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] <= x:
            ans = middle
            low = middle + 1
        else:
            high = middle - 1
    return ans
