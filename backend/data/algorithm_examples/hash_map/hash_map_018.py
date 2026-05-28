def first_unique_18(s):
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    for j, ch in enumerate(s):
        if freq[ch] == 1:
            return j
    return -1
