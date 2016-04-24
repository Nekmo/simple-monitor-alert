

class InvalidScriptLineBase:
    def __init__(self, line, script_path):
        self.line = line
        self.script_path = script_path

    def __repr__(self):
        return '<InvalidScriptLine "{}" in file "{}">'.format(self.line, self.script_path)

    def __str__(self):
        return self.__repr__()


class InvalidScriptLineError(InvalidScriptLineBase, SyntaxError):
    pass


class InvalidScriptLineWarning(InvalidScriptLineBase, SyntaxWarning):
    def __repr__(self):
        return '{}'.format(self.line)


class InvalidScriptLineLogging(InvalidScriptLineBase):
    pass