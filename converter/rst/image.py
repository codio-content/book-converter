import re
from collections import namedtuple

MASK_IMAGE_TO_MD = '![{alt}]({image}){caret_token}{caption}{caret_token}{caret_token}'
Figure = namedtuple('Figure', ['position', 'tag'])


class Image(object):
    def __init__(self, source_string, caret_token, chapter_num, subsection_num):
        self.str = source_string
        self._caret_token = caret_token
        self._chapter_num = chapter_num
        self._subsection_num = subsection_num
        self._figure_counter = 1
        self._figures = list()
        self._image_re = re.compile(
            r"""(\.\. _(?P<tag>.*?):\n\s*)?\.\. odsafig:: (?P<path>.*?)\n(?P<options>(?:\s+:.*?:\s+.*\n)+)? *(\n(?P<caption>( +.+\n)+))?""")

    @staticmethod
    def _get_image_options(raw_options):
        options_dict = {}
        option_re = re.compile('[\t ]+:([^:]+): (.+)')
        options = raw_options.split('\n')
        for opt in options:
            match = option_re.match(opt)
            if match:
                options_dict[match[1]] = match[2]
        return options_dict

    def _image(self, matchobj):
        caret_token = self._caret_token
        image = matchobj.group('path')
        output = MASK_IMAGE_TO_MD.replace('{image}', image)
        output = self._set_alt(output, matchobj.group('options'))
        output = self._set_caption(output, matchobj.group('caption'))
        output = output.replace('{caret_token}', caret_token)

        tag = matchobj.group('tag') if matchobj.group('tag') is not None else False
        if tag:
            self._figures.append(Figure(self._figure_counter, matchobj.group('tag')))
        self._figure_counter += 1

        return output

    def _set_figure_links_by_tag(self, output):
        for figure in self._figures:
            output = output.replace(f'Figure :num:`Figure #{figure.tag}`',
                                    f'Figure {self._chapter_num}.{self._subsection_num}.{figure.position}')
        return output

    def _set_caption(self, output, raw_caption):
        caption = self._get_caption(raw_caption) if raw_caption is not None else False
        if caption:
            output = output.replace('{alt}', caption)
            output = output.replace('{caption}', '{caret_token}' + caption)
        else:
            output = output.replace('{caret_token}{caption}', '')
        return output

    def _set_alt(self, output, raw_options):
        options = self._get_image_options(raw_options) if raw_options is not None else False
        alt = options.get('alt') if options else False
        if alt:
            output = output.replace('{alt}', alt)
        return output

    def _get_caption(self, raw_caption):
        caption = raw_caption.replace('\n', ' ')
        caption = caption.strip()
        caption = re.sub(" +", " ", caption)
        return f'**Figure {self._chapter_num}.{self._subsection_num}.{self._figure_counter}:** *{caption}*'

    def convert(self):
        output = self.str
        output = self._image_re.sub(self._image, output)
        return output
