from typing import List

from models.Element import Element


class Production:
    def __init__(self, lhs: Element, rhs: List[Element], number=None):
        self.lhs = lhs
        self.rhs = tuple(rhs)
        self.number = number

    def __str__(self) -> str:
        return "[{}->{}]".format(str(self.lhs), ' '.join(map(str, self.rhs)))

    def __repr__(self):
        return str(self)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Production) and self.lhs == o.lhs and all(a == b for a, b in zip(self.rhs, o.rhs))

    def __hash__(self) -> int:
        return hash((self.lhs, self.rhs))
