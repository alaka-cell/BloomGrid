class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BST:

    def __init__(self):
        self.root = None
        self.size = 0

    def insert(self, value):
        self.size += 1
        if self.root is None:
            self.root = TreeNode(value)
            return
        curr = self.root
        while True:
            if value == curr.value:
                self.size -= 1  # no duplicates
                return
            elif value < curr.value:
                if curr.left is None:
                    curr.left = TreeNode(value)
                    return
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = TreeNode(value)
                    return
                curr = curr.right

    def search(self, value):
        curr = self.root
        steps = 0
        while curr:
            steps += 1
            if value == curr.value:
                return True, steps
            curr = curr.left if value < curr.value else curr.right
        return False, steps

    def inorder(self):
        result = []

        def _walk(node):
            if node:
                _walk(node.left)
                result.append(node.value)
                _walk(node.right)

        _walk(self.root)
        return result

    def preorder(self):
        result = []

        def _walk(node):
            if node:
                result.append(node.value)
                _walk(node.left)
                _walk(node.right)

        _walk(self.root)
        return result


class CollisionGraph:

    def __init__(self):
        self.adjacency = {} 
    def add_node(self, item):
        self.adjacency.setdefault(item, set())

    def add_edge(self, item_a, item_b):
        self.add_node(item_a)
        self.add_node(item_b)
        self.adjacency[item_a].add(item_b)
        self.adjacency[item_b].add(item_a)

    def build_from_positions(self, item_positions: dict):
        items = list(item_positions.keys())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if item_positions[a] & item_positions[b]:  # shared bits
                    self.add_edge(a, b)

    def bfs(self, start):
        if start not in self.adjacency:
            return []
        visited = {start}
        queue = [start]
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in sorted(self.adjacency[node]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def dfs(self, start):
        visited = set()
        order = []

        def _walk(node):
            if node in visited:
                return
            visited.add(node)
            order.append(node)
            for neighbor in sorted(self.adjacency.get(node, [])):
                _walk(neighbor)

        _walk(start)
        return order

    def connected_clusters(self):
        seen = set()
        clusters = []
        for node in self.adjacency:
            if node not in seen:
                cluster = self.bfs(node)
                seen.update(cluster)
                clusters.append(cluster)
        return clusters


if __name__ == "__main__":
    bst = BST()
    for x in ["mango", "apple", "banana", "kiwi"]:
        bst.insert(x)
    print("Inorder (sorted):", bst.inorder())
    print("Search 'banana':", bst.search("banana"))

    g = CollisionGraph()
    g.build_from_positions({
        "alice": {3, 8, 15},
        "bob": {8, 22, 40},     
        "carol": {5, 9, 12},    
    })
    print("BFS from alice:", g.bfs("alice"))
    print("Clusters:", g.connected_clusters())
