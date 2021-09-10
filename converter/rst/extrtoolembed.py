import re
from converter.rst.model.assessment_data import AssessmentData


class ExtrToolEmbed(object):
    def __init__(self, source_string, exercises):
        self.str = source_string
        self._exercises = exercises
        self._assessments = list()
        self._extrtoolembed_re = re.compile(
            r"""^$\n^.*?\n-+\n\n?\.\. extrtoolembed:: '(?P<name>.*?)'\n( *:.*?: .*?\n)?(?=\S|$)""", flags=re.MULTILINE)

    def _extrtoolembed(self, matchobj):
        name = matchobj.group('name').lower()
        options = self._exercises.get(name.lower(), {})
        assessment_id = f'test-{name.lower()}'
        if options:
            assessment = AssessmentData(assessment_id, name, 'test', 20, options)
            self._assessments.append(assessment)
        return ''

    def convert(self):
        output = self.str
        output = self._extrtoolembed_re.sub(self._extrtoolembed, output)
        return output, self._assessments
