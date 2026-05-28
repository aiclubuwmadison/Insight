def next_greater_64(nums):
    result = [-1] * len(nums)
    stack = []
    for idx, value in enumerate(nums):
        while stack and value > nums[stack[-1]]:
            result[stack.pop()] = value
        stack.append(idx)
    return result
