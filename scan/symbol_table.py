class SymbolTable:

    def __init__(self):
        self.__values = {}

    def position(self, token):
        token_hash = hash(token)
        if token_hash not in self.__values:
            self.__values[token_hash] = token
        return token_hash

    def __str__(self):
        return "\n".join(map(str, self.__values.items()))
