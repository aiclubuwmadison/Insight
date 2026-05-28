def search_73(arr, needle):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < needle:
            lo = mid + 1
        else:
            hi = mid
    return lo
