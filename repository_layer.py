from abc import ABC, abstractmethod


class Repository(ABC):
    @abstractmethod
    def add(self, item):
        pass

    @abstractmethod
    def get(self, item_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, item):
        pass

    @abstractmethod
    def delete(self, item_id):
        pass


class MemoryRepository(Repository):
    def __init__(self, items=(), next_id=1):
        self._items = {}
        for item in items:
            if type(item.id) is not int or item.id < 1:
                raise ValueError("ID должен быть положительным целым числом")
            if item.id in self._items:
                raise ValueError(f"повторяющийся ID {item.id}")
            self._items[item.id] = item

        if type(next_id) is not int or next_id <= max(self._items, default=0):
            raise ValueError("некорректный счётчик ID")
        self._next_id = next_id

    @property
    def next_id(self):
        return self._next_id

    def add(self, item):
        if item.id is not None:
            raise ValueError("объект уже сохранён")
        item.id = self._next_id
        self._items[item.id] = item
        self._next_id += 1
        return item

    def get(self, item_id):
        if item_id not in self._items:
            raise ValueError(f"объект с ID {item_id} не найден")
        return self._items[item_id]

    def get_all(self):
        return list(self._items.values())

    def update(self, item):
        self.get(item.id)
        self._items[item.id] = item
        return item

    def delete(self, item_id):
        self.get(item_id)
        del self._items[item_id]
