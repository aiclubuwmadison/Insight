def find_target_6(values, needle):
    low = 0
    high = len(values) - 1
    ans = -1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] <= needle:
            ans = middle
            low = middle + 1
        else:
            high = middle - 1
    return ans
