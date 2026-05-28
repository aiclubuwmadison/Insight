def tree_sum_43(root):
    if root is None:
        return 0
    return root.val + tree_sum_43(root.left) + tree_sum_43(root.right)
