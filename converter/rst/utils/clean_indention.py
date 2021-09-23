import re


def clean_indention(content):
    str_len = 0
    cut_content = []
    content = content.lstrip('\n').rstrip()
    content_list = content.split('\n')
    indent_match = re.search(r'^ *', content_list[0])
    if indent_match:
        str_len = len(indent_match.group(0))
    for ind, item in enumerate(content_list):
        cut_content.append(content_list[ind][str_len-1:])
    return '\n'.join(cut_content)
