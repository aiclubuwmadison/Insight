def tree_sum_55(root):
    if root is None:
        return 0
    return root.val + tree_sum_55(root.left) + tree_sum_55(root.right)
