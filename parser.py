from parse.functions import pretty_print, construct_table, evaluate
from read import reader
from scan.scanner import get_pif

if __name__ == '__main__':
    grammar = reader.read_grammar('grammars/grammar2')
    grammar = grammar.get_extended()
    table, states = construct_table(grammar)
    pretty_print(grammar, states, table)
    pif = get_pif("code/code")
    print(pif)
    output = evaluate(grammar, table, ['a', 'b', 'c', 'd'])
    for production in output[::-1]:
        print(production)