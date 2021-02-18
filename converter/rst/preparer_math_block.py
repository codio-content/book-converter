class PreparerMathBlock(object):
    def __init__(self, source_array, math_block_separator_token):
        self._array = source_array
        self._math_block_separator_token = math_block_separator_token
        self._is_started_block = False
        self._indent = None
        self._last_position_separator = None
        self._separator = False

    def _prepare_math_block(self, line, number_line):
        if len(line) == 0 and self._separator is True:
            self._array[self._last_position_separator] = ""
            self._is_started_block = False
            self._indent = None
            self._last_position_separator = None
            self._separator = False
            return
        if len(line) == 0:
            self._separator = True
            if self._indent is None:
                return
            else:
                self._array[number_line] = f'{self._math_block_separator_token}'
                self._last_position_separator = number_line
        else:
            self._separator = False
            current_indent = len(line) - len(line.lstrip())
            if self._indent is None:
                self._indent = current_indent
            if current_indent == self._indent:
                return
            else:
                self._is_started_block = False
                self._indent = None
                if self._last_position_separator is not None:
                    self._array[self._last_position_separator] = ""

    def prepare(self):
        for i in range(len(self._array)):
            line = self._array[i]
            _is_started_block = ".. math::" in line
            if _is_started_block:
                self._is_started_block = _is_started_block
                continue
            if self._is_started_block:
                self._prepare_math_block(line, i)
        return self._array
