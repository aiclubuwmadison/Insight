"""
Train Insight's local algorithm classifier.

This script intentionally starts with a small built-in DSA dataset so the full
Tree-sitter -> feature extraction -> scikit-learn -> saved model path works
without external files. Replace or extend TRAINING_EXAMPLES as the project grows.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from app.core.ast_features import FEATURE_KEYS, extract_ast_features
from app.core.parser import parse_code

MODEL_PATH = Path(__file__).with_name("algorithm_classifier.pkl")

TRAINING_EXAMPLES = [
    (
        "binary_search",
        "python",
        """
def search(nums, target):
    l, r = 0, len(nums) - 1
    while l <= r:
        mid = (l + r) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            l = mid + 1
        else:
            r = mid - 1
    return -1
""",
    ),
    (
        "binary_search",
        "javascript",
        """
function search(nums, target) {
  let left = 0, right = nums.length - 1;
  while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    if (nums[mid] === target) return mid;
    if (nums[mid] < target) left = mid + 1;
    else right = mid - 1;
  }
  return -1;
}
""",
    ),
    (
        "two_pointers",
        "python",
        """
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return [left, right]
        if total < target:
            left += 1
        else:
            right -= 1
    return []
""",
    ),
    (
        "two_pointers",
        "java",
        """
int[] twoSum(int[] nums, int target) {
    int left = 0, right = nums.length - 1;
    while (left < right) {
        int sum = nums[left] + nums[right];
        if (sum == target) return new int[]{left, right};
        if (sum < target) left++;
        else right--;
    }
    return new int[]{};
}
""",
    ),
    (
        "sliding_window",
        "python",
        """
def max_sum(nums, k):
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i-k]
        best = max(best, window)
    return best
""",
    ),
    (
        "sliding_window",
        "javascript",
        """
function maxSum(nums, k) {
  let window = 0;
  for (let i = 0; i < k; i++) window += nums[i];
  let best = window;
  for (let i = k; i < nums.length; i++) {
    window += nums[i] - nums[i-k];
    best = Math.max(best, window);
  }
  return best;
}
""",
    ),
    (
        "stack",
        "python",
        """
def is_valid(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for ch in s:
        if ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        else:
            stack.append(ch)
    return not stack
""",
    ),
    (
        "stack",
        "typescript",
        """
function isValid(s: string): boolean {
  const stack: string[] = [];
  const pairs: Record<string,string> = {')':'(', ']':'[', '}':'{'};
  for (const ch of s) {
    if (ch in pairs) {
      if (!stack.length || stack[stack.length-1] !== pairs[ch]) return false;
      stack.pop();
    } else stack.push(ch);
  }
  return stack.length === 0;
}
""",
    ),
    (
        "dfs",
        "python",
        """
def dfs(graph, node, seen):
    if node in seen:
        return
    seen.add(node)
    for nei in graph[node]:
        dfs(graph, nei, seen)
""",
    ),
    (
        "dfs",
        "javascript",
        """
function dfs(graph, node, seen) {
  if (seen.has(node)) return;
  seen.add(node);
  for (const next of graph[node]) dfs(graph, next, seen);
}
""",
    ),
    (
        "bfs",
        "python",
        """
from collections import deque

def bfs(graph, start):
    q = deque([start])
    seen = {start}
    while q:
        node = q.popleft()
        for nei in graph[node]:
            if nei not in seen:
                seen.add(nei)
                q.append(nei)
    return seen
""",
    ),
    (
        "bfs",
        "java",
        """
void bfs(Map<Integer, List<Integer>> graph, int start) {
    Queue<Integer> q = new LinkedList<>();
    Set<Integer> seen = new HashSet<>();
    q.add(start);
    seen.add(start);
    while (!q.isEmpty()) {
        int node = q.remove();
        for (int next : graph.get(node)) {
            if (!seen.contains(next)) {
                seen.add(next);
                q.add(next);
            }
        }
    }
}
""",
    ),
    (
        "dynamic_programming",
        "python",
        """
def climb_stairs(n):
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[1], dp[2] = 1, 2
    for i in range(3, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
""",
    ),
    (
        "dynamic_programming",
        "javascript",
        """
function fib(n) {
  const dp = new Array(n + 1).fill(0);
  dp[1] = 1;
  for (let i = 2; i <= n; i++) dp[i] = dp[i - 1] + dp[i - 2];
  return dp[n];
}
""",
    ),
    (
        "sorting",
        "python",
        """
def sort_nums(nums):
    nums.sort()
    return nums
""",
    ),
    (
        "sorting",
        "javascript",
        """
function sortNums(nums) {
  return nums.sort((a, b) => a - b);
}
""",
    ),
    (
        "hash_map",
        "python",
        """
def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target-n], i]
        seen[n] = i
    return []
""",
    ),
    (
        "hash_map",
        "java",
        """
int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> seen = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int need = target - nums[i];
        if (seen.containsKey(need)) return new int[]{seen.get(need), i};
        seen.put(nums[i], i);
    }
    return new int[]{};
}
""",
    ),
    (
        "unknown",
        "python",
        """
def greet(name):
    message = "hello " + name
    print(message)
""",
    ),
    (
        "unknown",
        "javascript",
        """
async function fetchUser(id) {
  const res = await fetch(`/api/users/${id}`);
  return await res.json();
}
""",
    ),
]


def build_training_frame() -> pd.DataFrame:
    rows = []
    for label, language, code in TRAINING_EXAMPLES:
        tree = parse_code(code, language)
        features = extract_ast_features(tree.root_node, code)
        features["label"] = label
        rows.append(features)
    return pd.DataFrame(rows)


def train() -> None:
    df = build_training_frame()

    feature_columns = [col for col in df.columns if col != "label"]

    X = df[feature_columns]
    y = df["label"]

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
    )

    model.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "model": model,
        "feature_columns": feature_columns,
    }

    joblib.dump(payload, MODEL_PATH)

    print(f"Trained algorithm classifier on {len(df)} examples")
    print(f"Classes: {sorted(y.unique())}")
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    train()
