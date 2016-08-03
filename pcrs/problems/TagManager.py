import re

def parseCodeIntoFiles(code):
    '''Parses this submission into corresponding files

    The file tag format is [file <fileName>][/file]
    Returns:
        A list of name-code file dictionaries.
    '''
    files = []

    startTagRegex = re.compile('[\t ]*\[file ([A-Za-z0-9_\.]+)\][\t ]*\n')
    endTagRegex = re.compile('\n[\t ]*\[\/file\][\t ]*');

    startMatch = startTagRegex.search(code)
    while startMatch:
        endMatch = endTagRegex.search(code)
        files.append({
            'name': startMatch.group(1),
            'code': code[startMatch.end():endMatch.start()],
        })
        code = code[endMatch.end():]
        startMatch = startTagRegex.search(code)
    return files or [{
        # If there were no file tags
        'name': 'Code.java', # There should be a fallback for an empty file name
        'code': code,
    }]

