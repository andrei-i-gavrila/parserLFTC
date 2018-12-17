import re
import sys

from pyscanner.codification import *
from pyscanner.pif import PIF


def is_separator(char):
    return char in separators


def is_keyword(token):
    return token in keywords


def is_identifier(token):
    return re.fullmatch(identifier_regex, token) is not None


def is_constant(token):
    return re.fullmatch(constant_regex, token) is not None


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception("File name required")

    pif = PIF()

    filename = sys.argv[1]
    with open(filename, "r") as source:
        sourcecode = map(lambda s: s + " ", source.readlines())
    failure = False
    for line_number, line in enumerate(sourcecode, 1):
        start_pos = 0
        i = 0
        while i < len(line):
            if line[i] == "'":
                i += 1
                while line[i] != "'":
                    i += 1
                i += 1
                pif.add_constant(line[start_pos:i])
                start_pos = i

            if not is_separator(line[i]):
                i += 1
                continue

            if line[i] in multi_char_separator and line[i:i + 2] in multi_char_separator[line[i]]:
                i += 2
            token = line[start_pos:i]

            try:
                if is_keyword(token):
                    pif.add(token)
                elif is_identifier(token):
                    pif.add_identifier(token)
                elif is_constant(token):
                    pif.add_constant(token)
                elif token not in {' ', '', '\n'}:
                    pif.add(token)
                # else:
                #     print ("something went wrong", token)

                if line[i] not in {' ', '', '\n'}:
                    pif.add(line[i])
            except LookupError as error:
                print("Error at line", line_number, "position", start_pos, "token", "'{}'".format(error.args[0]))
                failure = True

            i += 1
            start_pos = i
    if not failure:
        print(pif)
