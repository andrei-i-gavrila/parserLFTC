from copy import deepcopy

from models import Action, Element, Production, Table, TableEntry
from pyscanner import CONFIG
from reader import Reader, sc_argparse
from scanner import PyScanner


def pretty_print(work_stack, input_stack, output_band):
    print('{:70s} {:70s} {:70s}'.format(work_stack, input_stack, output_band))


def stringify_list(input_list, comma=False):
    ret = ''
    counter = 0
    for element in input_list:
        if not comma or counter == 0:
            ret += str(element)
        else:
            ret += ', ' + str(element)
        counter += 1
    return ret


class Parser(object):
    def __init__(self, grammar, input_buffer):
        self.grammar = grammar
        self.input_buffer = input_buffer
        self.states = []
        self.table = Table()

    def add_dot(self, production):
        p = deepcopy(production)
        for idx, val in enumerate(p.rhs):
            if val.is_dot and idx == len(p.rhs) - 1:
                return []
            elif val.is_dot:
                p.rhs.insert(idx + 1, p.rhs.pop(idx))
                return p
        p.rhs.insert(0, Element('.', True, is_dot=True))

        return p

    def generate_additional_state_elements(self, production):
        additionals = []
        for idx, val in enumerate(production.rhs):
            if val.is_dot and idx == len(production.rhs) - 1:
                return []
            elif val.is_dot:
                nextelem = production.rhs[idx + 1]
                if not nextelem.terminal:
                    for p in self.grammar.productions.productions:
                        if p.lhs.name == nextelem.name:
                            additionals.append(self.add_dot(p))
        return additionals

    def goto(self, production):
        """Gets a production and returns a new state."""
        state = []
        new_dotted = self.add_dot(production)
        if not new_dotted:
            pass
        else:
            state.append(new_dotted)
            for gen in self.generate_additional_state_elements(new_dotted):
                state.append(gen)
            return state
        return []

    def get_element_before_dot(self, production):
        for idx, val in enumerate(production.rhs):
            if val.is_dot:
                return production.rhs[idx - 1]

    def prepare_table_entry(self):
        action = {}
        goto = {}
        for element in self.grammar.elements:
            if element.terminal:
                action[element.name] = None
            else:
                goto[element.name] = None
        action['$'] = None

        return TableEntry(action=action, goto=goto)

    def genearate_states(self):
        initial = self.grammar.productions.get_augmented()[0]
        dotted_initial = self.add_dot(initial)
        state = [dotted_initial]
        for e in self.generate_additional_state_elements(production=dotted_initial):
            state.append(e)
        self.states.append(state)
        index = 0
        # generate states
        while index < len(self.states):
            if index not in self.table.entries:
                self.table.entries[index] = self.prepare_table_entry()
            toadd = []
            transitions = []
            for pr in self.states[index]:
                goto = self.goto(pr)
                if len(goto) > 0:
                    element_to_add = self.get_element_before_dot(goto[0])
                    transitions.append((element_to_add, goto))
                    if goto not in toadd:
                        if goto not in self.states:
                            toadd.append(goto)

            for gt in toadd:
                self.states.append(gt)

            for t in transitions:
                idx = self.states.index(t[1])
                if idx not in self.table.entries:
                    self.table.entries[idx] = self.prepare_table_entry()
                if t[1][0].rhs[-1].is_dot:
                    p = Production(lhs=t[1][0].lhs, rhs=t[1][0].rhs[:-1])

                    if p == initial:
                        self.table.entries[idx].action['$'] = Action(action='accept', number=None)
                    else:

                        for y in self.table.entries[idx].action:
                            self.table.entries[idx].action[y] = Action(action='reduce',
                                                                       number=str(self.grammar.productions.productions.index(p) + 1))

                if t[0].terminal:
                    self.table.entries[index].action[t[0].name] = Action(action='shift',
                                                                         number=str(self.states.index(t[1])))

                else:
                    self.table.entries[index].goto[t[0].name] = Action(action='goto',
                                                                       number=str(self.states.index(t[1])))

            index += 1

        for i, state in enumerate(self.states):
            print(str(i) + ": " + ",".join(map(str, state)))

        for k, v in self.table.entries.items():
            print(str(k) + ": " + str(v))

    def evaluate(self):
        input_buffer_index = 0
        self.input_buffer.append(Element(name='$', terminal=False))
        pointer = self.input_buffer[input_buffer_index]
        stack = [0]
        output_data = []
        pretty_print(work_stack=stack,
                     input_stack=stringify_list(self.input_buffer[input_buffer_index:]),
                     output_band=stringify_list(output_data))
        while True:
            currentstate = stack[-1]
            action = self.table.entries[int(currentstate)].action[pointer.name]
            if not action:
                print('Errors found in source code.')
                break
            elif action.action == 'shift':
                stack.append(pointer.name)
                stack.append(int(action.number))
                input_buffer_index += 1
                pretty_print(work_stack=stack,
                             input_stack=stringify_list(self.input_buffer[input_buffer_index:]),
                             output_band=stringify_list(output_data, comma=True))

            elif action.action == 'accept':

                if input_buffer_index != (len(self.input_buffer) - 1):
                    print
                    'Errors found in source code.'
                else:
                    print
                    'The source code is correct.'
                break
            elif action.action == 'reduce':
                production = self.grammar.productions.productions[int(action.number) - 1]
                popcount = 2 * len(production.rhs)
                del stack[-popcount:]
                currentstate = stack[-1]
                stack.append(production.lhs.name)
                goto = self.table.entries[currentstate].goto[stack[-1]]
                output_data.insert(0, production)
                stack.append(goto.number)
                pretty_print(work_stack=stack,
                             input_stack=stringify_list(self.input_buffer[input_buffer_index:]),
                             output_band=stringify_list(output_data, comma=True))
            if pointer.name != '$':
                pointer = self.input_buffer[input_buffer_index]


def pif2sc(pif, codification_map):
    sc = []
    for pifelement in pif:
        if pifelement['code'] == 0:
            sc.append('identifier')
        elif pifelement['code'] == 1:
            sc.append('constant')
        else:
            for symbol, value in codification_map.items():
                if value == pifelement['code']:
                    sc.append(symbol)
    return sc


if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    pretty_print("Work Stack", "Input Stack", "Output Band")
    reader = Reader(sc_argparse().grammar, sc_argparse().code)
    if not sc_argparse().pif:
        grammar = reader.read_grammar()
        input_buffer = reader.read_code()
        parser = Parser(grammar=grammar, input_buffer=input_buffer)
        parser.genearate_states()
        parser.evaluate()
    else:
        scanner = PyScanner(filename=sc_argparse().code)
        scanner.scan()
        input_buffer = pif2sc(pif=scanner.pif, codification_map=CONFIG.CODIFICATION_MAP)
        grammar = reader.read_grammar()
        parser = Parser(grammar=grammar, input_buffer=reader.gen_code(code=input_buffer))
        parser.genearate_states()
        parser.evaluate()
