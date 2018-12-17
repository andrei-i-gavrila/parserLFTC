codification = {
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

separators = {' ', '+', '*', '/', '[', ']', '-', '{', '}', '=', ',', '<', '>', '\n'}
multi_char_separator = {
    '=': {'=='},
    '-': {'->'},
}

keywords = {'Arr', 'int', 'bool', 'input', 'output', 'while', 'when', 'else'}
identifier_regex = r'[a-zA-Z][a-zA-Z0-9]{0,7}'
constant_regex = r'[+-]?[1-9][0-9]*|0|false|true|\'[^\']?\''
