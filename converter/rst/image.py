import re
from collections import namedtuple

Figure = namedtuple('Figure', ['position', 'tag'])


class Image(object):
    def __init__(self, source_string, caret_token, chapter_num, subsection_num):
        self.str = source_string
        self._caret_token = caret_token
        self._chapter_num = chapter_num
        self._subsection_num = subsection_num
        self._figure_counter = 1
        self._figures = list()
        self._image_capt_with_tag_re = re.compile(
            r"""\.\. _(?P<tag>.*?):\n\s*\s\.\. odsafig:: (?P<path>.*?)\n(?P<options>(?:\s+:.*?:\s+.*\n)+)\n(?P<caption>( +.+\n)+)""")
        self._image_re = re.compile(r"""\.\. odsafig:: (?P<path>.*?)\n(?P<options>(?:\s+:.*?:\s+.*\n)+)""")
        self._image_capt_re = re.compile(r"""\.\. odsafig:: (?P<path>.*?)\n(?:.*?\n +(?P<caption>.*\n))""")

    def _image(self, matchobj):
        caret_token = self._caret_token
        image = matchobj.group('path')
        options = self._get_image_options(matchobj.group('options'))
        alt = options.get('alt')
        return f'![{alt}]({image}){caret_token}{caret_token}'

    def _image_capt(self, matchobj):
        caret_token = self._caret_token
        image = matchobj.group('path')
        caption = matchobj.group('caption')
        caption = caption.strip()
        return f'![{caption}]({image}){caret_token}{caption}{caret_token}{caret_token}'

    def _image_capt_with_tag(self, matchobj):
        self._figures.append(Figure(self._figure_counter, matchobj.group('tag')))
        caption = self._get_caption(matchobj.group('caption'))
        self._figure_counter += 1
        caret_token = self._caret_token
        image = matchobj.group('path')
        options = self._get_image_options(matchobj.group('options'))
        alt = options.get('alt')
        return f'![{alt}]({image}){caret_token}{caption}{caret_token}{caret_token}'

    def _set_figure_links_by_tag(self, output):
        for figure in self._figures:
            output = output.replace(f'Figure :num:`Figure #{figure.tag}`',
                                    f'Figure {self._chapter_num}.{self._subsection_num}.{figure.position}')
        return output

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

    def _get_caption(self, raw_caption):
        caption = raw_caption.replace('\n', ' ')
        caption = caption.strip()
        caption = re.sub(" +", " ", caption)
        return f'Figure {self._chapter_num}.{self._subsection_num}.{self._figure_counter}: {caption}'

    def convert(self):
        output = self.str
        output = self._image_capt_with_tag_re.sub(self._image_capt_with_tag, output)
        output = self._set_figure_links_by_tag(output)
        output = self._image_re.sub(self._image, output)
        output = self._image_capt_re.sub(self._image_capt, output)
        return output
