import re

from converter.markdown.text_as_paragraph import TextAsParagraph


class Exercise(TextAsParagraph):
    def __init__(self, latex_str, exercise_num, chapter_num, remove_exercise, caret_token):
        super().__init__(latex_str, caret_token)

        self._exercise_counter = 0
        self._exercise_counter_offset = exercise_num
        self._chapter_num = chapter_num
        self._remove_exercise = remove_exercise

        self._exercise_re = re.compile(r"""\\begin{exercise}(.*?)\n
                                    (?P<block_contents>.*?)
                                    \\end{exercise}""",
                                       flags=re.DOTALL + re.VERBOSE)

    def _exercise_block(self, matchobj):
        block_contents = matchobj.group('block_contents')

        self._exercise_counter += 1
        prefix = "**Exercise {}.{}:**{caret_token}".format(
            self._chapter_num, self._exercise_counter + self._exercise_counter_offset, caret_token=self._caret_token
        )
        if self._remove_exercise:
            prefix = ""

        block_contents = self.to_paragraph(block_contents)

        return prefix + block_contents

    def convert(self):
        output = self.str

        output = self._exercise_re.sub(self._exercise_block, output)

        return output
