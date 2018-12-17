import argparse
import os

from models import Element, Grammar, Production


def filename(path):
    """Checks that file exists but it does not open."""
    if not os.path.exists(path):
        raise argparse.ArgumentError
    return path


def sc_argparse():
    """Read and validate command-line arguments."""
    parser = argparse.ArgumentParser(description='Scanner program for mini-language')
    parser.add_argument('-g', '--grammar', dest='grammar', required=False, type=filename, help='Grammar',
                        metavar='FILE')
    parser.add_argument('-f', '--file', dest='code', required=False, type=filename, help='Source code',
                        metavar='FILE')
    parser.add_argument('-pif', '--pif', action='store_true')
    return parser.parse_args()


class Reader(object):
    def __init__(self, grammar_file, code_file):
        self.grammar_filename = grammar_file
        self.code_filename = code_file
        self.grammar_lines = []
        self.code_lines = []

    def read_code(self):
        self.code_lines = [line.rstrip('\n') for line in open(self.code_filename)]
        elements = []

        for line in self.code_lines:
            for e in line.split(' '):
                elements.append(Element(name=e, terminal=True))
        return elements

    def gen_code(self, code):
        elements = []
        for line in code:
            for e in line.split(' '):
                elements.append(Element(name=e, terminal=True))
        return elements

    def read_grammar(self):
        self.grammar_lines = [line.rstrip('\n') for line in open(self.grammar_filename)]
        starting_symbol = Element(name=self.grammar_lines[0], terminal=False)
        elements = []
        productions = []
        for terminal in self.grammar_lines[1].split(' '):
            elements.append(Element(name=terminal, terminal=True))
        for nonterminal in self.grammar_lines[2].split(' '):
            elements.append(Element(name=nonterminal, terminal=False))
        for production in self.grammar_lines[3:]:
            elems = production.split(' ')
            lhs = [lhselem for lhselem in elements if lhselem.name == elems[0]]
            rhs = []
            for rhsinput in elems[1:]:
                rhselem = [rhsele for rhsele in elements if rhsele.name == rhsinput]
                rhs.append(rhselem[0])
            prod = Production(lhs=lhs[0], rhs=rhs)
            productions.append(prod)

        return Grammar(starting_symbol=starting_symbol, productions=productions, elements=elements)
