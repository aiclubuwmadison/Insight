def tree_sum_39(root):
    if root is None:
        return 0
    return root.val + tree_sum_39(root.left) + tree_sum_39(root.right)
