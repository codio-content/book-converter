import re
import uuid


class RemoveComments(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str

        comment_token = str(uuid.uuid4())
        output = re.sub("%(.*?)?$", comment_token, output, flags=re.MULTILINE)
        cleaned = list(filter(lambda line: line.strip() != comment_token, output.split('\n')))
        output = '\n'.join(cleaned)
        output = re.sub(comment_token, "", output, flags=re.MULTILINE)

        return output
