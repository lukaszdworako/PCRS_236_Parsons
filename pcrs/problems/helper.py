def remove_tag(tag_open, tag_close, source_code):
    '''Remove a tag and all it's contents from the given code.
    '''
    source_code = source_code.split('\n')
    source_code_output = []
    tag_count = 0
    for line in source_code:
        if line.find(tag_open) > -1:
            tag_count += 1
            continue
        elif line.find(tag_close) > -1:
            tag_count -= 1
            continue
        if tag_count == 0:
            source_code_output.append(line)
    return "\n".join(source_code_output)

