import collections


class TypedList(collections.MutableSequence):

    def __init__(self, oktypes, items=[]):
        self.oktypes = oktypes
        self._list = list()
        self.extend(items)

    def __str__(self):
        return str(self._list)

    def __add__(self, other):
        L = self.__class__(self)
        if isinstance(other, list):
            L.extend(other)
        else:
            L.append(other)
        return L

    def __radd__(self, other):
        if isinstance(other, self.__item_type__):
            L = self.__class__([other])
            L.extend(self)
        elif isinstance(other, list):
            L = self.__class__(other)
            L.extend(self)
        return L

    def __iadd__(self, other):
        if isinstance(other, list):
            self.extend(other)
        else:
            self.append(other)
        return self

    def __len__(self): 
        return len(self._list)

    def __getitem__(self, i): 
        return self._list[i]

    def __delitem__(self, i): 
        del self._list[i]

    def __setitem__(self, i, v):
        # self.check(v)
        self._list[i] = v

    def check(self, v):
        if not isinstance(v, self.oktypes):
            raise TypeError('Invalid type')

    def insert(self, i, v):
        # self.check(v)
        self._list.insert(i, v)


class ElementList(TypedList):

    def __init__(self, oktypes=tuple(), items=list()):
        super().__init__(oktypes, items)

#     def __add__(self, other):
#         if isinstance(other, list):
#             l = ElementList([self])
#             l.extend(other)
#             return l
#         elif isinstance(other, __Element__):
#             return ElementList([self, other])
#         else:
#             raise TypeError("Wrong type of argument for addition in __Element__: " + str(type(other)))

#     def __radd__(self, other):
#         if isinstance(other, list) :
#             l = ElementList(other)
#             l.append(self)
#             return l
#         elif isinstance(other, __Element__):
#             return ElementList([other, self])
#         else:
#             raise TypeError("Wrong type of argument for addition in __Element__: " + str(type(other)))
