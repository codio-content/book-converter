import re


class Del_icons_description(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str

        output = re.sub(r"\s*We also use.*?look them up.\s*", "", output)
        output = re.sub(r"\\tablefigure{ch_intro/tables/icons_table}{.*?}{.*?}", "", output)

        return output
