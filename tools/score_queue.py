from collections import deque
# Cola simple para manejar puntuaciones o elementos en orden FIFO
class ScoreQueue:
    def __init__(self):
        self._q = deque()

    def enqueue(self, item):
        self._q.append(item)

    def dequeue(self):
        return self._q.popleft() if self._q else None

    def peek(self):
        return self._q[0] if self._q else None

    def is_empty(self):
        return len(self._q) == 0

    def size(self):
        return len(self._q)

    def to_list(self):
        return list(self._q)
