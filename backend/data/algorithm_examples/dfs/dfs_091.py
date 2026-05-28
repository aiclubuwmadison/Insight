def tree_sum_91(root):
    if root is None:
        return 0
    return root.val + tree_sum_91(root.left) + tree_sum_91(root.right)
