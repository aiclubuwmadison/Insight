def tree_sum_23(root):
    if root is None:
        return 0
    return root.val + tree_sum_23(root.left) + tree_sum_23(root.right)
