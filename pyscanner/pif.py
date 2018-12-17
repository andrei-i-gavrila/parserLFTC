from pyscanner.codification import codification
from pyscanner.symbol_table import SymbolTable


class PIF:

    def __init__(self):
        self.__identifiers_table = SymbolTable()
        self.__constants_table = SymbolTable()
        self.__elements = []

    def add_constant(self, token):
        self.__elements.append((codification["constant"], token, self.__constants_table.position(token)))

    def add_identifier(self, token):
        self.__elements.append((codification["identifier"], token, self.__identifiers_table.position(token)))

    def add(self, token):
        if token not in codification:
            raise LookupError(token)
        self.__elements.append((codification[token], token, -1))

    def __str__(self):
        return "PIF:\n" + "\n".join(map(str, self.__elements)) + "\nSymbols:\n" + str(self.__identifiers_table) + "\nConstants\n" + str(self.__constants_table)

    @property
    def symbol_table(self):
        return self.__identifiers_table

    @property
    def constant_table(self):
        return self.__constants_table
