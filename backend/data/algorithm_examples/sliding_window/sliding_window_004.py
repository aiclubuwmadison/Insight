from collections import defaultdict
def longest_replacement_4(s, k):
    counts = defaultdict(int)
    left = 0
    best = 0
    max_count = 0
    for right, ch in enumerate(s):
        counts[ch] += 1
        max_count = max(max_count, counts[ch])
        while right - left + 1 - max_count > k:
            counts[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
