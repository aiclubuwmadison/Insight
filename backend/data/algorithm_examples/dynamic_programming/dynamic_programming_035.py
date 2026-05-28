def climb_stairs_35(n):
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 2
    for k in range(3, n + 1):
        dp[k] = dp[k - 1] + dp[k - 2]
    return dp[n]
