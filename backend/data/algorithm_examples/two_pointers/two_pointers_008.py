def remove_target_8(nums, target):
    write = 0
    for read in range(len(nums)):
        if nums[read] != target:
            nums[write] = nums[read]
            write += 1
    return write
