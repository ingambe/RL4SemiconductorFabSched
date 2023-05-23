class EventQueue:
    def __init__(self):
        self.event_array = []

    @property
    def first(self):
        return self.event_array[0]

    @property
    def empty(self):
        return len(self.event_array) == 0

    def pop_first(self):
        return self.event_array.pop(0)

    def push(self, item):
        self.event_array.append(item)

    def ordered_insert(self, item):
        if len(self.event_array) == 0 or item.timestamp < self.event_array[0].timestamp:
            self.event_array.insert(0, item)
        elif item.timestamp > self.event_array[-1].timestamp:
            self.event_array.append(item)
        else:
            lo = 0
            hi = len(self.event_array)
            while lo < hi:
                mid = (lo + hi) // 2
                if item.timestamp < self.event_array[mid].timestamp:
                    hi = mid
                else:
                    lo = mid + 1
            self.event_array.insert(lo, item)

    def remove(self, remove):
        self.event_array.remove(remove)

    def __len__(self):
        return len(self.event_array)


class LNode:
    def __init__(self, value, nx):
        self.value = value
        self.next: LNode = nx


class LinkedList:
    def __init__(self):
        self.f = None

    @property
    def first(self):
        return self.f.value

    @property
    def empty(self):
        return self.f is None

    def pop_first(self):
        val = self.f.value
        self.f = self.f.next
        return val

    def ordered_insert(self, item):
        for i, ev in enumerate(self.arr):
            if item.timestamp < ev.timestamp:
                ins = True
                break
        if ins:
            self.arr.insert(i, item)
        else:
            self.push(item)
        pass

    def remove(self, item):
        if item == self.f.value:
            return self.pop_first()
        else:
            pointer = self.f
            while pointer is not None:
                if pointer.next.value == item.value:
                    item = pointer.next.item
                    pointer.next = pointer.next.next
                    return item
            raise ValueError('not found')
