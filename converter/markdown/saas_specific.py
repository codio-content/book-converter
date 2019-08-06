import re


def convert(input_str):
    output = re.sub(r"\\protect", "", input_str)
    output = re.sub(r"\\ig{}", "Instructors' Manual", output)
    output = re.sub(r"\\js{}", "JavaScript", output)
    output = re.sub(r"\\slash{}", "/", output)
    return output
