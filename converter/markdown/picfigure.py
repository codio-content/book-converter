import re

picfigure_re = re.compile(r"""\\picfigure{(?P<image>.*?)}{(?P<refs>.*?)}{(?P<content>.*?)}""",
                          flags=re.DOTALL + re.VERBOSE)

images = []


def make_block(matchobj):
    content = matchobj.group('content').strip()
    image = matchobj.group('image').strip()
    if image.lower().endswith('.pdf'):
        images.append(image)
        image = image.replace('.pdf', '.jpg')
    return "![{}]({})  \n{}".format(content, image, content)


def convert(input_str):
    images.clear()
    pdfs = filter(lambda img: img.endswith('.pdf'), images)
    return picfigure_re.sub(make_block, input_str), list(pdfs)
