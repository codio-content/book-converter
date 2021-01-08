import re

MASK_IMAGE_TO_MD = '![{alt}]({image}){caret_token}{caption}{caret_token}{caret_token}\n'


class Image(object):
    def __init__(self, source_string, caret_token, tags):
        self.str = source_string
        self._caret_token = caret_token
        self._tags = tags
        self._image_re = re.compile(
            r"""(\.\.[ ]_(?P<tag>.*?):\n\s*)?\.\.[ ]odsafig::[ ](?P<path>.*?)\n(?P<options>(?:\s+:.*?:\s+.*\n)+)?[ ]*
                (\n(?P<caption>(?:[ ]+.+\n)+))?""", flags=re.VERBOSE)
        self._figure_re = re.compile(
            r"""(\.\.[ ]_(?P<tag>.*?):\n\s*)?\.\.[ ]figure::[ ](?P<path>.*?)\n(?P<options>(?:\s+:.*?:\s+.*\n)+)?[ ]*
                (\n(?P<caption>(?:[ ]+.+\n)+))?""", flags=re.VERBOSE)

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
        reference = ''
        tag = matchobj.group('tag') if matchobj.group('tag') is not None else False
        if tag and tag in self._tags:
            reference = self._tags[tag]
        output = self._set_caption(output, matchobj.group('caption'), reference)
        output = output.replace('{caret_token}', caret_token)
        return output

    def _set_caption(self, output, raw_caption, reference):
        caption = self._get_caption(raw_caption, reference) if raw_caption is not None else False
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
    def _get_caption(raw_caption, reference):
        caption = raw_caption.replace('\n', ' ')
        caption = caption.strip()
        caption = re.sub(" +", " ", caption)
        return f'**Figure {reference}:** *{caption}*'

    def convert(self):
        output = self.str
        output = self._image_re.sub(self._image, output)
        output = self._figure_re.sub(self._image, output)
        return output
