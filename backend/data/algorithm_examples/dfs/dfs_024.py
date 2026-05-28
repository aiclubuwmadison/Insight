def dfs_24(graph, start):
    visited = set()
    order = []
    def visit(node):
        if node in visited:
            return
        visited.add(node)
        order.append(node)
        for nxt in graph.get(node, []):
            visit(nxt)
    visit(start)
    return order
