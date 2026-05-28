def rob_26(nums):
    prev2 = 0
    prev1 = 0
    for value in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + value)
    return prev1
