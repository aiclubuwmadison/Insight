from functools import lru_cache
def fib_94(n):
    @lru_cache(None)
    def solve(k):
        if k < 2:
            return k
        return solve(k - 1) + solve(k - 2)
    return solve(n)
