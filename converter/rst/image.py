import re

MASK_IMAGE_TO_MD = '![{alt}]({image}){caret_token}{caption}{caret_token}{caret_token}\n'


class Image(object):
    def __init__(self, source_string, caret_token, open_dsa_cdn):
        self.str = source_string
        self._caret_token = caret_token
        self._open_dsa_cdn = open_dsa_cdn
        self._odsafig_re = re.compile(
            r"""(\.\.[ ]_(?P<tag>.*?):\n\s*)?\.\.[ ]odsafig::[ ]:figure_number:(?P<figure_number>[0-9.]*):[ ]
                (?P<path>.*?)\n(?P<options>(?:\s+:.*?:\s+.*\n)+)?[ ]*
                (\n(?![ ]+\.\.)(?P<caption>(?:[ ]+.+\n)+))?""", flags=re.VERBOSE)

        self._figure_re = re.compile(
            r"""(\.\.[ ]_(?P<tag>.*?):\n\s*)?\.\.[ ]figure::[ ]:figure_number:(?P<figure_number>[0-9.]*):[ ]
                (?P<path>.*?)\n(?P<options>(?:\s+:.*?:\s+.*\n)+)?[ ]*
                (\n(?![ ]+\.\.)(?P<caption>(?:[ ]+.+\n)+))?""", flags=re.VERBOSE)

        self._image_re = re.compile(r"""^( *\.\.\simage:: ?(?P<path>.*?)?\n)(?P<options>.*?)\n(?=\S|\s+\n)""",
                                    flags=re.MULTILINE + re.DOTALL)

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

    def _figure(self, matchobj):
        caret_token = self._caret_token
        image_path = matchobj.group('path')
        # TODO cdn
        # image_path = f'{self._open_dsa_cdn}/{image_path}'
        output = MASK_IMAGE_TO_MD.replace('{image}', image_path)
        output = self._set_alt(output, matchobj.group('options'))
        figure_number = matchobj.group('figure_number') if matchobj.group('figure_number') is not None else ''
        output = self._set_caption(output, matchobj.group('caption'), figure_number)
        output = output.replace('{caret_token}', caret_token)
        return output

    def _set_caption(self, output, raw_caption, figure_number):
        caption = self._get_caption(raw_caption, figure_number) if raw_caption is not None else False
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

    @staticmethod
    def _get_caption(raw_caption, figure_number):
        caption = raw_caption.replace('\n', ' ')
        caption = caption.strip()
        caption = re.sub(" +", " ", caption)
        return f'**Figure {figure_number}:** *{caption}*'

    def _image(self, matchobj):
        options = {}
        caret_token = self._caret_token
        image_path = matchobj.group('path')
        options_group = matchobj.group('options')
        option_re = re.compile(':([^:]+): (.+)')
        for line in options_group.split('\n'):
            opt_match = option_re.match(line.strip())
            if option_re.match(line.strip()):
                options[opt_match[1]] = opt_match[2]
        width = options.get('width', '')
        alt = options.get('alt', '')

        return f'{caret_token}<img src="{image_path}" alt="{alt}" style="width:{width};">{caret_token}\n'

    def convert(self):
        output = self.str
        output = self._image_re.sub(self._image, output)
        output = self._odsafig_re.sub(self._figure, output)
        output = self._figure_re.sub(self._figure, output)
        return output
