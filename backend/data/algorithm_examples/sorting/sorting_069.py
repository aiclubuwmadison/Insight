def insertion_sort_69(nums):
    arr = nums[:]
    for pos in range(1, len(arr)):
        current = arr[pos]
        j = pos - 1
        while j >= 0 and arr[j] > current:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = current
    return arr
