def match_block(chars, output, repl_func):
    pos = output.find(chars)
    while pos != -1:
        level = 0 if '{' in chars else 1
        for index in range(pos + len(chars), len(output), 1):
            ch = output[index]
            prev_char = output[index - 1]
            if ch == '}' and prev_char != '\\':
                if level == 0:
                    start_position = pos+len(chars) if '{' in chars else output.find("{", pos) + 1
                    output = output[0:pos] + repl_func(output[start_position:index]) + output[index + 1:]
                    break
                else:
                    level += 1
            elif ch == '{' and prev_char != '\\':
                level -= 1
        pos = output.find(chars)
    return output
