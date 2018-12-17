import argparse
import os


def filename(path):
    """Checks that file exists but it does not open."""
    if not os.path.exists(path):
        raise argparse.ArgumentError
    return path


def sc_argparse():
    """Read and validate command-line arguments."""
    parser = argparse.ArgumentParser(description='Scanner program for mini-language')
    parser.add_argument('-f', '--file', dest='filename', required=True, type=filename, help='Source code', metavar='FILE')
    parser.add_argument('-d', '--debug', action='store_true')
    return parser.parse_args()


def remove_whitespaces_and_last_char(text):
    """Removes whitespaces and removes last character from string."""
    return text[:-1].strip()
