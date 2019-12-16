from typing import List, Optional, Dict, Tuple

from models.Element import Element
from models.Grammar import Grammar
from models.LR0Table import LR0Table
from models.Production import Production


def get_element_after_dot(production: Production) -> Optional[Element]:
    for i, element in enumerate(production.rhs):
        if element.dot and i + 1 != len(production.rhs):
            return production.rhs[i + 1]
    return None


def add_dot(production: Production) -> Production:
    return Production(production.lhs, [Element('.', True, True), *production.rhs], production.number)


def get_productions_of(grammar: Grammar, element: Element):
    return tuple(list(filter(lambda production: production.lhs == element, grammar.productions)))


def closure(grammar: Grammar, productions: Tuple[Production]) -> Tuple[Production]:
    result = set(productions)
    done = False
    while not done:
        done = True
        for production in result.copy():
            element_after_dot = get_element_after_dot(production)
            if element_after_dot is None:
                continue
            productions_of_element = get_productions_of(grammar, element_after_dot)
            for dotted_production in map(add_dot, productions_of_element):
                if dotted_production not in result:
                    done = False
                    result.add(dotted_production)
    return tuple(result)


def advance_dot(production: Production, dot_index: int) -> Production:
    rhs = production.rhs[:dot_index] + (production.rhs[dot_index + 1], production.rhs[dot_index]) + production.rhs[dot_index + 2:]
    return Production(production.lhs, rhs, production.number)


def goto(grammar: Grammar, productions: Tuple[Production], element: Element) -> Tuple[Production]:
    result = []
    for production in productions:
        dot_index = 0
        while dot_index < len(production.rhs) and not production.rhs[dot_index].dot:
            dot_index += 1
        if dot_index + 1 >= len(production.rhs):
            continue

        if production.rhs[dot_index + 1] != element:
            continue

        result.append(advance_dot(production, dot_index))

    return closure(grammar, tuple(result))


def canonical_collection(grammar: Grammar) -> Dict[int, Tuple[Production]]:
    dotted = add_dot(get_productions_of(grammar, grammar.starting_element)[0])
    s0 = closure(grammar, (dotted,))
    collection = {0: s0}
    states_set = {s0}
    done = False
    while not done:
        done = True
        for state in collection.copy().values():
            for element in grammar.elements:
                goto_result = goto(grammar, state, element)
                if goto_result and goto_result not in states_set:
                    collection[len(collection)] = goto_result
                    states_set.add(goto_result)
                    done = False

    return collection


def construct_table(grammar: Grammar):
    actions = {}
    gotos = {}
    states = canonical_collection(grammar)

    for i, state in states.items():
        shiftable = can_shift(state)
        reduceable_productions = get_reduce_productions(state)
        if shiftable and reduceable_productions:
            if len(reduceable_productions) != 1 or reduceable_productions[0].lhs != grammar.starting_element:
                # raise Exception('Shift reduce conflict', i, state, states)
                actions[i] = ('err sr',)
                continue
        if len(reduceable_productions) > 1:
            # raise Exception('Reduce reduce conflict')
            actions[i] = ('err rr',)
            continue

        if shiftable:
            actions[i] = ('shift',)
            for element in grammar.elements:
                goto_result = goto(grammar, state, element)
                if goto_result:
                    gotos[(i, element.name)] = [i for i, state in states.items() if state == goto_result][0]

        elif len(reduceable_productions) == 1:
            if reduceable_productions[0].lhs == grammar.starting_element:
                actions[i] = ('acc',)
            else:
                actions[i] = ('reduce', reduceable_productions[0].number)
        else:
            actions[i] = ('error',)
    return LR0Table(actions, gotos), states


def get_reduce_productions(state) -> List[Production]:
    return [production for production in state if get_element_after_dot(production) is None]


def can_shift(state):
    for production in state:
        if get_element_after_dot(production) is not None:
            return True
    return False


def pretty_print(grammar, states, table):
    def print_line(*values):
        print(*map(lambda v: "{:25s}".format(str(v)), values))

    print("Productions")
    for production in grammar.productions:
        print("{:2s}: {}".format(str(production.number), production))

    print("States")
    for i, state in states.items():
        print("{:2s}: {}".format(str(i), ", ".join(map(str, state))))

    print("Table")
    print_line("state", "action", *map(lambda e: e.name, grammar.elements))
    for i, state in states.items():
        print_line(i, table.actions[i], *map(lambda e: table.gotos[(i, e.name)] if (i, e.name) in table.gotos else '', grammar.elements))


def evaluate(grammar, table, code):
    state = 0
    alpha = [('$', 0)]
    beta = ['$'] + code[::-1]
    phi = []

    end = False

    while not end:
        if table.actions[state][0] == 'shift':
            token = beta.pop()
            state = table.gotos[(state, token)]
            alpha.append((token, state))
        elif table.actions[state][0] == 'reduce':
            production = grammar.numbered_productions[table.actions[state][1]]
            for element in production.rhs[::-1]:
                last = alpha.pop()
                if element.name != last[0]:
                    raise Exception("wrong")
            state = table.gotos[(alpha[-1][1], production.lhs.name)]
            alpha.append((production.lhs.name, state))
            phi.append(production)
        elif table.actions[state][0] == 'acc':
            end = True
            phi.append('success')
        else:
            phi.append("error")
            end = True

    return phi
