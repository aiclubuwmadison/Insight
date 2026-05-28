def last_le_82(arr, needle):
    low = 0
    high = len(arr) - 1
    ans = -1
    while low <= high:
        middle = (low + high) // 2
        if arr[middle] <= needle:
            ans = middle
            low = middle + 1
        else:
            high = middle - 1
    return ans
