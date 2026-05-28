def binary_search_78(arr, target):
    low = 0
    high = len(arr) - 1
    ans = -1
    while low <= high:
        middle = (low + high) // 2
        if arr[middle] <= target:
            ans = middle
            low = middle + 1
        else:
            high = middle - 1
    return ans
