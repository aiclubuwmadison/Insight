def merge_sorted_39(a, b):
    i1 = 0
    i2 = 0
    out = []
    while i1 < len(a) and i2 < len(b):
        if a[i1] <= b[i2]:
            out.append(a[i1])
            i1 += 1
        else:
            out.append(b[i2])
            i2 += 1
    out.extend(a[i1:])
    out.extend(b[i2:])
    return out
