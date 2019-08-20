def match_block(chars, output, repl_func):
    pos = output.find(chars)
    while pos != -1:
        level = 0
        for index in range(pos + len(chars), len(output), 1):
            ch = output[index]
            if ch == '}':
                if level == 0:
                    output = output[0:pos] + repl_func(output[pos+len(chars):index]) + output[index + 1:]
                    break
                else:
                    level += 1
            elif ch == '{':
                level -= 1
        pos = output.find(chars)
    return output
