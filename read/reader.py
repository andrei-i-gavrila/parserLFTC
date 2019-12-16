import string

from models.Element import Element
from models.Grammar import Grammar
from models.Production import Production


def read_grammar(filename: string) -> Grammar:
    with open(filename, "r") as file:
        starting_symbol = file.readline().strip()
        terminals = set(file.readline().strip().split(" "))

        terminal_elements = list(map(lambda t: Element(t, True), terminals))
        non_terminal_elements = []
        starting_symbol_element = Element(starting_symbol, False)

        productions = []
        for line in file.readlines():
            tokens = line.strip().split(" ")
            lhs = Element(tokens[0][:-1], False)
            non_terminal_elements.append(lhs)
            rhs = list(map(lambda e: Element(e, e in terminals), tokens[1:]))
            productions.append(Production(lhs, rhs))

        return Grammar(terminal_elements + non_terminal_elements, productions, starting_symbol_element)


def read_code(filename):
    pass