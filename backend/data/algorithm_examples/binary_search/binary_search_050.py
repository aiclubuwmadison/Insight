def search_50(items, target):
    low = 0
    high = len(items) - 1
    ans = -1
    while low <= high:
        middle = (low + high) // 2
        if items[middle] <= target:
            ans = middle
            low = middle + 1
        else:
            high = middle - 1
    return ans
