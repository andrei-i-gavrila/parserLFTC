class Element(object):
    def __init__(self, name, terminal, augmented=False, is_dot=False):
        self.name = name
        self.terminal = terminal
        self.augmented = augmented
        self.is_dot = is_dot

    def __str__(self):
        return '{}'.format(self.name)

    def __cmp__(self, other):
        if (self.name == other.name and self.terminal == other.terminal and self.augmented == other.augmented and
                self.is_dot == other.is_dot):
            return 0
        return -1


class Production(object):
    def __init__(self, rhs, lhs):
        self.rhs = rhs
        self.lhs = lhs

    def __str__(self):
        return "{} -> {}".format(self.lhs, "".join(self.rhs))

    def __cmp__(self, other):
        if self.lhs != other.lhs:
            return -1
        elif len(self.rhs) != len(other.rhs):
            return -1
        else:
            for a, b in zip(self.rhs, other.rhs):
                if a != b:
                    return -1
            return 0


class ProductionContainer(object):
    def __init__(self):
        self.productions = []

    def get_augmented(self):
        return [prod for prod in self.productions if prod.lhs.augmented]

    def add(self, production):
        if production not in self.productions:
            self.productions.append(production)


class Grammar(object):
    def __init__(self, starting_symbol, productions, elements):
        self.elements = elements
        self.productions = ProductionContainer()
        self.productions.productions = productions
        self.starting_symbol = starting_symbol
        self.augmented_starting = Element("S'", False, True)
        augmented_prod = Production(self.augmented_starting, [self.starting_symbol])
        self.productions.add(augmented_prod)


class Table(object):
    def __init__(self):
        self.entries = {}


class Action(object):
    def __init__(self, action, number):
        self.action = action
        self.number = number

    def __str__(self):
        return '{} - {}'.format(self.action, self.number)


class TableEntry(object):
    def __init__(self, action, goto):
        self.action = action
        self.goto = goto

    def __str__(self):
        return "{} {}".format(",".join(["{}: {}".format(k, v) for k, v in self.action.items()]), ",".join(["{}: {}".format(k, v) for k, v in self.goto.items()]))
