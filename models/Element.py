class Element:
    def __init__(self, name, terminal, dot=False):
        self.name = name
        self.terminal = terminal
        self.dot = dot

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Element) and self.name == other.name and self.terminal == other.terminal and self.dot == other.dot

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self):
        return str(self)