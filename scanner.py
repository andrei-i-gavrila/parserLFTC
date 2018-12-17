import collections
import logging
import pprint

import pyscanner.CONFIG as CONFIG
from pyscanner.scanner_exceptions import ScannerException
from pyscanner.utils import sc_argparse, remove_whitespaces_and_last_char


class PyScanner(object):
    def __init__(self, filename):
        self.filename = filename
        self.pif = []
        self.constant_st = collections.OrderedDict()
        self.identifier_st = collections.OrderedDict()
        self.errors = []

    def analyze(self, last_char, text_until_last_char, source_code, line_number, line_position):

        # We need to save the text length with whitespaces so we'll know the exact position of error in file
        true_text_length = text_until_last_char
        """
        Analyze source code part (the last read char(stop token) and the text read until that point).
        :param last_char: The last read character
        :param text_until_last_char: The text read until the last character
        :param source_code: The file containing the source code
        :param line_number: The current line number
        :param line_position: The current position in line
        :return: New substring
        """
        # Skip detecting tokens if the last char isn't a text separator or comparator
        if last_char in CONFIG.TEXT_SEPARATORS + CONFIG.COMPARATORS:
            # Trim text to get rid of whitespaces
            text_until_last_char = remove_whitespaces_and_last_char(text_until_last_char)
            end_token = last_char

            if last_char in CONFIG.COMPARATORS:
                # Perform lookahead
                lookahead = source_code.read(1)
                if lookahead in CONFIG.COMPARATORS:
                    end_token = last_char + lookahead
                else:
                    # Lookahead unsuccessful, set file cursor one position back
                    if source_code.tell() != 1:
                        source_code.seek(source_code.tell() - 1)

            # Skip if whitespace (since whitespaces were removed before, length is zero).
            if len(text_until_last_char) > 0:
                try:
                    self.detect_token(text_until_last_char)
                except ScannerException as e:
                    message = 'Line {0}, character {1}, {2}'.format(line_number,
                                                                    line_position - len(true_text_length), e.message)
                    self.errors.append(message)
            # Skip if whitespace
            if end_token not in CONFIG.SPACES:
                try:
                    self.detect_token(end_token)
                except ScannerException as e:
                    message = 'Line {0}, character {1}, {2}'.format(line_number, line_position, e.message)
                    self.errors.append(message)

            # Token identified (or exception was raised), so text until the last char has been processed
            # Return empty string (reset text read until last char)
            return ''
        else:
            # The last read character wasn't a text separator, so text read until then
            # must be set back
            return text_until_last_char

    def scan(self):
        """
        Scan source code.
        :return: None
        """
        substring = ''
        c = None
        line_number = 1
        line_position = 1
        with open(self.filename) as source_code:
            while True:
                old_char = c
                # Read one character from file
                c = source_code.read(1)

                line_position += 1
                if not c:
                    # EOF reached, check for newline, stop scanning
                    if old_char != CONFIG.NEWLINE:
                        self.errors.append('No newline at the end of file.')
                    break

                # Store the history (text until the last read character)
                # Easier to manage if separated
                substring += c
                # Analyze last char and text read until it
                substring = self.analyze(c, substring, source_code, line_number, line_position)
                if c == CONFIG.NEWLINE:
                    line_number += 1
                    line_position = 1

    def detect_token(self, token):
        """
        Identifies (classifies, validates) tokens.
        :param token: Token
        :return: None
        :raises: ScannerException
        """

        if token in CONFIG.RESERVED_WORDS:
            logging.debug('reserved word:{0}'.format(token))
            self.add_to_pif(code=CONFIG.CODIFICATION_MAP[token], index=-1)
            return

        elif CONFIG.match_constant(token):
            logging.debug('integer constant:{0}'.format(token))
            st_index = self.add_to_st(token=token, constant=True)
            self.add_to_pif(code=CONFIG.CODIFICATION_MAP['constant'], index=st_index)
            return

        elif token in CONFIG.SEPARATORS:
            logging.debug('separator:{0}'.format(token))
            self.add_to_pif(code=CONFIG.CODIFICATION_MAP[token], index=-1)
            return

        elif token in CONFIG.ARITHMETIC_OPERATORS:
            logging.debug('arithmetic operator:{0}'.format(token))
            self.add_to_pif(code=CONFIG.CODIFICATION_MAP[token], index=-1)
            return

        elif token in CONFIG.COMPARATORS:
            logging.debug('comparator:{0}'.format(token))
            self.add_to_pif(code=CONFIG.CODIFICATION_MAP[token], index=-1)
            return

        elif CONFIG.match_identifier(token):
            logging.debug('identifier:{0}'.format(token))
            st_index = self.add_to_st(token=token, constant=False)
            self.add_to_pif(code=CONFIG.CODIFICATION_MAP['identifier'], index=st_index)
            return

        # Token couldn't be identified, raise exception
        raise ScannerException('Syntax error: {0}'.format(token))

    def add_to_st(self, token, constant=True):
        """
        Add token to symbol table.
        :param token: Validated token
        :param constant: If true add to the constant symbol table
        :return: New index or old (if it was already present)
        """
        if constant:
            if token not in self.constant_st:
                self.constant_st[token] = len(self.constant_st)
                self.constant_st = collections.OrderedDict(sorted(self.constant_st.items()))

            return self.constant_st[token]
        else:
            if token not in self.identifier_st:
                self.identifier_st[token] = len(self.identifier_st)
                self.identifier_st = collections.OrderedDict(sorted(self.identifier_st.items()))
            return self.identifier_st[token]

    def add_to_pif(self, code, index):
        """
        Add a new record to the program internal form.
        :param code: The corresponding code from CONFIG.CODIFICATION_MAP
        :param index: Symbol table index
        :return: None
        """
        new_record = {'code': code, 'st_index': index}
        self.pif.append(new_record)


if __name__ == '__main__':

    # Set logging level
    if sc_argparse().debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    scanner = PyScanner(sc_argparse().filename)
    scanner.scan()

    # Print results (temporary code)
    if not scanner.errors:
        pprint.pprint('CONSTANT SYMBOL TABLE')
        pprint.pprint(scanner.constant_st)
        pprint.pprint('IDENTIFIER SYMBOL TABLE')
        pprint.pprint(scanner.identifier_st)
        pprint.pprint('PIF')
        pprint.pprint(scanner.pif, width=4)
    else:
        for error in scanner.errors:
            pprint.pprint(error, width=4)
