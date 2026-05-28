from collections import deque
def min_edges_79(graph, source, target):
    queue = deque([(source, 0)])
    visited = {source}
    while queue:
        node, depth = queue.popleft()
        if node == target:
            return depth
        for nxt in graph[node]:
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, depth + 1))
    return -1
