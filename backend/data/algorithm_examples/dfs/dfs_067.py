def tree_sum_67(root):
    if root is None:
        return 0
    return root.val + tree_sum_67(root.left) + tree_sum_67(root.right)
