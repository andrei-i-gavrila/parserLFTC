from typing import List

from models.Element import Element
from models.Production import Production


class Grammar:
    def __init__(self, elements: List[Element], productions: List[Production], starting_element: Element):
        self.__productions = {}
        self.elements = elements
        self.number_productions(productions)
        self.starting_element = starting_element

    def get_extended(self) -> 'Grammar':
        starting_symbol = Element("S'", False, False)
        elements = self.elements + [starting_symbol]
        productions = [Production(starting_symbol, [self.starting_element])] + list(self.productions)

        return Grammar(elements, productions, starting_symbol)

    def number_productions(self, productions):
        for i, production in enumerate(productions, 1):
            production.number = i
            self.__productions[i] = production

    @property
    def productions(self):
        return self.__productions.values()

    @property
    def numbered_productions(self):
        return self.__productions
