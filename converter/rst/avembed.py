import re
import pathlib
from converter.rst.model.assessment_data import AssessmentData
from converter.rst.utils import css_property


class AvEmbed(object):
    def __init__(self, source_string, caret_token, open_dsa_cdn, workspace_dir):
        self.str = source_string
        self._caret_token = caret_token
        self._open_dsa_cdn = open_dsa_cdn
        self._workspace_dir = workspace_dir
        self._assessments = list()
        self._avembed_re = re.compile(
            r"""[ ]*\.\.[ ]avembed::[ ](?P<name>.*?)[ ](?P<type>[a-z]{2}[ \t]*)[ ]*\n(?P<options>(\s+:.*?:\s+.*\n)+)?"""
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

        source_css_files = [file_name.replace('.html', '.css')]
        iframe_height = css_property.get_property_by_css(source_css_files, 'container', 'height', self._workspace_dir)
        if iframe_height is None:
            iframe_height = css_property.get_property_by_html(file_name, 'height', self._workspace_dir)
        iframe_height = 800 if iframe_height is None else re.sub(r'\d+', self._increase_size, iframe_height)
        iframe_width = css_property.get_property_by_css(source_css_files, 'container', 'width', self._workspace_dir)
        if iframe_width is None:
            iframe_width = css_property.get_property_by_html(file_name, 'width', self._workspace_dir)
        iframe_width = 950 if iframe_width is None else re.sub(r'\d+', self._increase_size, iframe_width)

        return f'\n{caret_token}<iframe id="{name}_iframe" src="{self._open_dsa_cdn}/{file_name}' \
               f'?selfLoggingEnabled=false&localMode=true&JXOP-debug=true&JOP-lang=en&JXOP-code=java' \
               f'&scoringServerEnabled=false&threshold=5&amp;points=1.0&required=True" ' \
               f'class="embeddedExercise" width="{iframe_width}" height="{iframe_height}"' \
               f' data-showhide="show" scrolling="no" ' \
               f'style="position: relative; top: 0px; border: none;">Your browser does not support iframes.</iframe>' \
               f'{caret_token}{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}{caret_token}\n'

    @staticmethod
    def _increase_size(match_obj):
        return str(int(match_obj.group(0)) + 50)

    def convert(self):
        output = self.str
        output = self._avembed_re.sub(self._avembed, output)
        return output, self._assessments
