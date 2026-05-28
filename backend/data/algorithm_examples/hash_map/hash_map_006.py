from collections import Counter
def most_common_6(words):
    counts = Counter(words)
    return counts.most_common(1)[0][0] if counts else None
