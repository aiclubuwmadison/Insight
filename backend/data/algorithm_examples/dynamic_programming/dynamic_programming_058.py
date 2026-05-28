def lcs_58(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for r in range(1, len(a) + 1):
        for c in range(1, len(b) + 1):
            if a[r - 1] == b[c - 1]:
                dp[r][c] = 1 + dp[r - 1][c - 1]
            else:
                dp[r][c] = max(dp[r - 1][c], dp[r][c - 1])
    return dp[-1][-1]
