import os
import re

# Define language constants
NEWLINE = os.linesep
RESERVED_WORDS = ['if', 'int', 'bool', 'when', 'else', 'Arr', 'while', 'input', 'output']
TEXT_SEPARATORS = ['<', '>', '(', ')', '{', '}', ' ', NEWLINE, ']', '[', ',', '->']
COMPARATORS = ['=', '==', '>', '>=', '<', '<=']
ARITHMETIC_OPERATORS = ['+', '-', '/', '*']
SEPARATORS = ['(', ')', '{', '}', '[', ']', ',']
SPACES = [' ', NEWLINE]
CODIFICATION_MAP = {
    'identifier': 0,
    'constant': 1,
    'Arr': 3,
    'int': 4,
    'bool': 5,
    'input': 6,
    'output': 7,
    'while': 8,
    'when': 9,
    'else': 10,
    '+': 11,
    '*': 12,
    '/': 13,
    '[': 14,
    ']': 15,
    '-': 16,
    '<': 17,
    '>': 18,
    '=': 19,
    '==': 20,
    '->': 21,
    '{': 22,
    '}': 23,
    ',': 24
}


def match_identifier(text):
    """
    Match indentifier.
    :param text: Search text
    :return: True/False
    """
    return re.search(r"^[a-zA-Z][a-zA-Z0-9]{0,7}$", text)


def match_constant(text):
    """
    Match an integer.
    :param text: Search text
    :return: True/False
    """
    return re.search(r'[+-]?[1-9][0-9]*|0|false|true|\'[^\']?\'', text)
