# Algorithm Examples Dataset

This folder contains 1,000 labeled Python examples for Insight's local AST-based algorithm classifier.

Labels:
- binary_search
- bfs
- dfs
- dynamic_programming
- hash_map
- sliding_window
- sorting
- stack
- two_pointers
- unknown

Each label has 100 `.py` examples. The folder name is the training label.

Train from the backend directory with:

```bash
python -m app.models.train_from_folders
```

This dataset is generated/curated to match Insight's exact labels. Public datasets such as LeetCode/Kaggle solution dumps and IBM Project CodeNet are useful sources for future expansion, but they usually label by problem or metadata rather than directly by algorithm pattern.
