def has_path_26(graph, src, dst):
    stack = [src]
    seen = set()
    while stack:
        node = stack.pop()
        if node == dst:
            return True
        if node in seen:
            continue
        seen.add(node)
        for nxt in graph.get(node, []):
            stack.append(nxt)
    return False
