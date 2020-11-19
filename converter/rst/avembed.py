import re
import pathlib
from converter.rst.model.assessment_data import AssessmentData


class AvEmbed(object):
    def __init__(self, source_string, caret_token, open_dsa_cdn):
        self.str = source_string
        self._caret_token = caret_token
        self._open_dsa_cdn = open_dsa_cdn
        self._assessments = list()
        self._avembed_re = re.compile(
            r"""\s*\.\. avembed:: (?P<name>.*?) (?P<type>[a-z]{2}) *\n(?P<options>(\s+:.*?:\s+.*\n)+)?"""
        )

    def _avembed(self, matchobj):
        caret_token = self._caret_token
        file_name = matchobj.group('name')
        # todo: check different type
        av_type = matchobj.group('type')
        # todo: verify options
        # options = matchobj.group('options')
        name = pathlib.Path(file_name).stem

        # todo: future todos: upload and use cdn path

        assessment_id = f'custom-{name.lower()}'
        assessment = AssessmentData(assessment_id, name, 'custom', 1, {'question': 'Resolve the challenge above'})
        self._assessments.append(assessment)

        return f'{caret_token}<iframe id="{name}_iframe" src="{self._open_dsa_cdn}/{file_name}' \
               f'?selfLoggingEnabled=false&localMode=true&JXOP-debug=true&JOP-lang=en&JXOP-code=java' \
               f'&scoringServerEnabled=false&threshold=5&amp;points=1.0&required=True" ' \
               f'class="embeddedExercise" width="950" height="800" data-showhide="show" scrolling="yes" ' \
               f'style="position: relative; top: 0px;">Your browser does not support iframes.</iframe>' \
               f'{caret_token}{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}{caret_token}'

    def convert(self):
        output = self.str
        output = self._avembed_re.sub(self._avembed, output)
        return output, self._assessments
