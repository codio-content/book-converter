def match_elements(text, n_matches):
    level = 0
    offset = 0
    found_matches = 0
    founds = []
    last_index = 0
    for index in range(0, len(text), 1):
        ch = text[index]
        last_index = index
        if ch == '}':
            level -= 1
            if level == 0:
                start_position = text.find("{", offset) + 1
                offset += start_position
                founds.append(text[start_position:index])
                found_matches += 1
                if found_matches == n_matches:
                    break
        elif ch == '{':
            level += 1
    return founds, last_index
