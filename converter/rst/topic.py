import re


class Topic(object):
    def __init__(self, source_string, caret_token, chapter_num, subsection_num, figure_counter):
        self.str = source_string
        self._caret_token = caret_token
        self._chapter_num = chapter_num
        self._subsection_num = subsection_num
        self._figure_counter = figure_counter
        self._topic_re = re.compile(
            r"""^\.{2} topic::? +(?P<type>.*?)\n\n*(?P<content>(?:\s+[^\n]+\n*)*)""", flags=re.MULTILINE)

    def _topic(self, matchobj):
        caret_token = self._caret_token
        topic_type = matchobj.group('type')
        content = matchobj.group('content')
        content = re.sub(r"\n +", "\n ", content)
        self._figure_counter += 1
        return f'<div style="padding: 20px; border: 1px; border-style: solid; border-color: silver;">' \
               f'{caret_token}{caret_token}**{topic_type} {self._chapter_num}.{self._subsection_num}.' \
               f'{self._figure_counter}**<br/>' \
               f'{caret_token}{caret_token}{content}\n\n</div><br/>{caret_token}{caret_token}'

    def convert(self):
        output = self.str
        output = self._topic_re.sub(self._topic, output)
        return output, self._figure_counter
