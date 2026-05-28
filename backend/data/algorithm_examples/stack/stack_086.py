def daily_temperatures_86(temps):
    ans = [0] * len(temps)
    stack = []
    for idx, temp in enumerate(temps):
        while stack and temp > stack[-1][1]:
            prev_idx, _ = stack.pop()
            ans[prev_idx] = idx - prev_idx
        stack.append((idx, temp))
    return ans
