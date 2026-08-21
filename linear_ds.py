class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, data):
        node = Node(data)
        if not self.head:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def delete(self, value):
        prev, curr = None, self.head
        while curr:
            if curr.data == value:
                if prev:
                    prev.next = curr.next
                else:
                    self.head = curr.next
                if curr == self.tail:
                    self.tail = prev
                self.size -= 1
                return True
            prev, curr = curr, curr.next
        return False

    def search(self, value):
        curr = self.head
        steps = 0
        while curr:
            steps += 1
            if curr.data == value:
                return True, steps
            curr = curr.next
        return False, steps

    def to_list(self):
        out, curr = [], self.head
        while curr:
            out.append(curr.data)
            curr = curr.next
        return out

    def __len__(self):
        return self.size

    def __iter__(self):
        curr = self.head
        while curr:
            yield curr.data
            curr = curr.next


class Stack:

    def __init__(self):
        self._top = None
        self._count = 0

    def push(self, data):
        node = Node(data)
        node.next = self._top
        self._top = node
        self._count += 1

    def pop(self):
        if self._top is None:
            raise IndexError("pop from empty stack")
        node = self._top
        self._top = node.next
        self._count -= 1
        return node.data

    def peek(self):
        return self._top.data if self._top else None

    def is_empty(self):
        return self._top is None

    def __len__(self):
        return self._count

    def trace(self):
        out, node = [], self._top
        while node:
            out.append(node.data)
            node = node.next
        return out


class Queue:

    def __init__(self):
        self._list = LinkedList()

    def enqueue(self, data):
        self._list.append(data)

    def dequeue(self):
        if not self._list.head:
            raise IndexError("dequeue from empty queue")
        node = self._list.head
        self._list.head = node.next
        if self._list.head is None:
            self._list.tail = None
        self._list.size -= 1
        return node.data

    def is_empty(self):
        return self._list.head is None

    def __len__(self):
        return self._list.size


if __name__ == "__main__":
    ll = LinkedList()
    for x in ["alice", "bob", "carol"]:
        ll.append(x)
    print("Log:", ll.to_list())
    print("Search 'bob':", ll.search("bob"))

    s = Stack()
    s.push(("ADD", "alice"))
    s.push(("ADD", "bob"))
    print("Stack trace:", s.trace())
    print("Popped:", s.pop())

    q = Queue()
    q.enqueue("item1")
    q.enqueue("item2")
    print("Dequeued:", q.dequeue())
