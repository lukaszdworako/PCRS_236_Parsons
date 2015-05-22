import logging
import pdb
# --------------------------------------------------------------- #
#        Supporting functions - cg_stacktrace constructor         #
# --------------------------------------------------------------- #


def hash_string(key):
    """Build a hash SHA1 from a key"""
    import hashlib
    hash_object = hashlib.sha1(key)
    return hash_object.hexdigest()


def get_current_date():
    """Return current date in milliseconds"""
    import datetime
    date_time = datetime.datetime.now() - datetime.datetime(1970, 1, 1)
    return str(date_time.total_seconds())


# --------------------------------------------------------------- #
#             Supporting functions - build_stacktrace             #
# --------------------------------------------------------------- #

def add_break_line_after_token(user_script, tokens):
    """Add \n scape sequence at the end of every ;."""
    logger = logging.getLogger('activity.logging')
    index = 0
    line_count = 1
    extra_scape_sequence_list = []
    while index < len(user_script):
        if user_script[index] == '\n':
            line_count += 1
        if (user_script[index] in tokens) and (index+1 != len(user_script)) and (user_script[index+1] != '\n'):
            user_script = insert_substring_in_string(user_script, '\n', index+1)
            extra_scape_sequence_list.append(line_count)
            line_count -= 1
        index += 1
    return extra_scape_sequence_list, user_script


def remove_string_constant(line):
    """Remove double quotes and what is inside it"""
    return remove_from_string_token_range(find_string_constants(line), line)

def remove_all_comments(user_script):
    """Remove all comments from the code"""
    while '/*' in user_script and '*/' in user_script:
        comment_start = user_script.index('/*')
        comment_end = user_script.index('*/', comment_start)
        user_script = user_script[:comment_start] + user_script[comment_end+1:]

    while '//' in user_script:
        comment_start = user_script.index('//')
        comment_end = user_script.index('\n', comment_start)
        user_script = user_script[:comment_start] + user_script[comment_end+1:]

    return user_script


def find_string_constants(line):
    """Find double quote strings in a line"""
    double_quotes = (list((find_all_occurrences(line, "\""))))
    invalid_double_quotes = (list((find_all_occurrences(line, "\\\""))))

    for invalid_double_quote in invalid_double_quotes:
        invalid_double_quote += 1  # jump the \ character
        if invalid_double_quote in double_quotes:
            double_quotes.remove(invalid_double_quote)

    return double_quotes


def remove_bracket_value_range(line, open, close):
    """Remove brackets and what is inside it"""
    brackets_open = (list((find_all_occurrences(line, open))))
    brackets_close = (list((find_all_occurrences(line, close))))
    brackets_close = brackets_close[::-1]

    brackets = []
    brackets_num = len(brackets_open)
    index = 0
    while index < brackets_num:
        if len(brackets) > 0 and \
           brackets[index-1] < brackets_open[index] and \
           brackets[index] > brackets_close[index]:
            index += 1
            continue
        brackets.append(brackets_open[index])
        brackets.append(brackets_close[index])
        index += 1

    return remove_from_string_token_range(brackets, line)


def remove_from_string_token_range(token_list, line):
    """Remove substring from string using a token pattern"""
    # Consider only quote pairs (open and a close quote)
    size_readjust = 0
    while len(token_list) > 0 and len(token_list) % 2 == 0:
        token_list[0] = token_list[0] - size_readjust
        token_list[1] = token_list[1] - size_readjust
        quote_start = token_list[0]
        quote_end = token_list[1]
        line = line[:quote_start] + line[quote_end+1:]
        token_list.remove(quote_start)
        token_list.remove(quote_end)
        size_readjust += quote_end - quote_start + 1
    return line


def find_all_occurrences(string, sub):
    """Find all occurrences of a token in a string."""
    start = 0
    while True:
        start = string.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)  # use start += 1 to find overlapping matches


def insert_substring_in_string(original, new, pos):
    """Inserts new inside original at pos."""
    return original[:pos] + new + original[pos:]


def get_return_variable(line):
    """Get return attributes"""
    expression_begin = line.find("return") + len('return')
    expression_end = line.find(";")
    return "".join(line[expression_begin: expression_end].split())


def search_dictionary(list, lookup):
    """Search value in a dictionary"""
    lookup = lookup.strip()
    best_key = ""
    for dict in list:
        for key, value in dict.items():
            if key in lookup and \
               lookup.index(key) == 0 and\
               len(best_key) < len(key):
                best_key = key
    return best_key


def get_variables_details_func_signature(line, line_number):
    """Get full details on variables located in function signature"""

    #pdb.set_trace()
    attributes = get_variables_inside_brackets(line)
    logger = logging.getLogger('activity.logging')
    attributes = attributes.strip()
    attributes_list = attributes.split(',')
    attributes_dic = []
    for attribute in attributes_list:
        logger.info("ATTRIBUTE IS "+attribute)
        attribute = attribute.strip()
        # ignore void or functions with no args
        if ('void' != attribute) and (attribute != ""):
            attribute = attribute.split(' ')
            attribute = remove_values_from_list(attribute, '')
            attributes_dic.append(
                {line_number: [{attribute[0]: ''.join(attribute[1:len(attribute)])}
                , 'outside_bracket', {'malloc': False}]})

    return attributes_dic


def get_variables_inside_brackets(line):
    """Get attributes inside brackets"""
    brack_start = line.index('(') + 1
    brack_end = line.index(')')
    return line[brack_start:brack_end]


def remove_values_from_list(list, val):
    """Remove a specific value from a list"""
    return [value for value in list if value != val]


def format_function_name(line, declaration_type):
    """Format function name"""
    line_formatted = line.replace(declaration_type, "", 1)
    line_formatted = line_formatted.replace("{", "")
    line_formatted = line_formatted.strip()
    return line_formatted


def get_variables_details(line, declaration_type):
    """Get variables details, both local and global definition"""
    attributes = line.strip()
    attributes = attributes[attributes.find(declaration_type):]
    attributes = attributes.replace(";", "")
    # Treat value range declared with a list
    attributes = remove_bracket_value_range(attributes, "{", "}")
    if '=' in attributes and '(' in attributes and ')' in attributes:
        attributes = remove_bracket_value_range(attributes, "=", ")")
    attributes_list = attributes.split(',')
    attributes_ret = []
    # In case of comma separate attributes
    for attribute in attributes_list:
        attribute = attribute.strip()
        attribute = attribute.replace(declaration_type, '')
        attribute = attribute.split(' ')
        attribute = remove_values_from_list(attribute, '')
        attributes_ret.append((declaration_type, attribute[0]))

    return attributes_ret


def is_function_prototype(line):
    """Verify if line contains a prototype declaration"""
    if '(' in line and ')' in line and "=" not in line and ';' in line:
        return True
    return False


def is_function_call(line):
    """Verify if line contains a function call"""
    if '(' in line and ')' in line and ';' in line:
        return True
    return False


def is_language_statement(line):
    """Verify if line contains a language statement (if, else, for)"""
    if '(' in line and ')' in line and ';' not in line:
        return True
    return False


def get_function_call(line, current_line):
    """Get function call details"""
    function_call = "".join(line.split()).replace(";", "")
    function_list = [{current_line: function_call[0: function_call.find('(')]}]
    if function_call.count("(") > 1:
        inner_functions = function_call[function_call.find('(')+1:function_call.rfind(')')]
        inner_functions = inner_functions.split(',')
        inner_functions = remove_values_from_list(inner_functions, '')
        for inner_function in inner_functions:
            function_list.extend(get_function_call(inner_function, current_line))
    return function_list


def get_variable_location_inside_function(function_brackets):
    """Check if variable is inside bracket inside a function"""
    variable_location = "outside_bracket"
    if len(function_brackets) % 2 != 0:
        variable_location = "inside_bracket"

    return variable_location

# --------------------------------------------------------------- #
#          Supporting functions - change_code_for_debbug          #
# --------------------------------------------------------------- #


def get_global_printf_list(stacktrace, line, key, primitive_types):
    """Get all printf statements for global variables"""
    print_list = []
    # Process global variables accessible by function
    for res in stacktrace:
        if res['declaration'] == 'variable' and res['scope'] == 'global':
            output_symbol = get_printf_symbol(res['type'], primitive_types)
            print_list.append(get_printf_string(line, key, output_symbol, res['name'], res['type'], res['malloc'],
                                                res['line_begin'], res['line_end']))

    return print_list


def get_local_printf_list(stacktrace, line, func_name, print_list, hash_key, primitive_types):
    """Get all printf statements for local variables"""
    # Process function local variables
    for res in stacktrace:
        if func_name == res['name']:
            for var_line in res['variables']:
                if line in var_line:
                    for key, value in var_line.items():
                        if 'return' in value:
                            for return_str, var_detail in value.items():
                                if 'return_str' in return_str:
                                    for type, var_name in var_detail.items():
                                        output_symbol = get_printf_symbol(type, primitive_types)
                                        print_list.append({'return': get_printf_string(line, hash_key, output_symbol,
                                                                                       var_name, type, value['malloc'],
                                                                                       res['line_begin'], res['line_end'])})
                        else:
                            for type, var_name in value[0].items():
                                output_symbol = get_printf_symbol(type, primitive_types)
                                print_list.append(get_printf_string(line, hash_key, output_symbol, var_name, type,
                                                                    value[2]['malloc'], res['line_begin'], res['line_end']))
            break
    return print_list


def get_printf_symbol(type, primitive_types):
    """Get printf symbol (such as %d, %c) from a C type"""
    output_symbol = ""
    for primitive_type in primitive_types:
        if type in primitive_type:
            output_symbol = primitive_type[type]
            break
        else:
            output_symbol = "%d"  # print decimal as default
    return output_symbol


def get_printf_string(line, hex_dig, output_symbol, var_name, type, malloc, line_begin, line_end):
    """Build a single printf statement"""

    printf = ""
    var_address = "&" + var_name

    # Process for pointers
    if '*' in var_name:
        var_address = var_name.replace("*", "")

        printf = {str(line): "printf(" + "\"(" + str(hex_dig) + ")" + "<line>;" + str(type) + ";" +
                  str(var_name) + ";" + "%p" + ";" + "%p" + ";" + str(output_symbol) + ";" + "%s" + ';' + "%d"
                  + ';' + "%d" + "(" + str(hex_dig) + ")" + "\\n" + "\"," + str("&" + var_name) + "," +
                  str("&" + var_address) + "," + str(var_name) + "," + "\"" + str(malloc) + "\"" + "," + str(line_begin)
                  + "," + str(line_end) + ");"}

    # Process arrays
    elif '[' in var_name and ']' in var_name:
        var_name = var_name[0: var_name.find('[')]
        printf = {str(line):  "printf(\"(" + str(hex_dig) + ")" + "<line>;" + str(var_name) + ";\");" +
                              "{int max = sizeof("+var_name+")/sizeof("+var_name+"[0]);" +
                              "int i;" +
                              "for(i = 0; i < max; i++)" +
                              "{printf(\"" + str(output_symbol) + "->\"," + str(var_name) + "[i]" + ");}}" +
                              "printf(\"(" + str(hex_dig) + ")\");"}
    # Process variables
    else:
        printf = {str(line): "printf(" + "\"(" + str(hex_dig) + ")" + "<line>;" + str(type) + ";" +
                  str(var_name) + ";" + str(output_symbol) + ";" + "%p" + ";" + "%s" + ';' + "%d"
                  + ';' + "%d" + "(" + str(hex_dig) + ")" + "\\n" + "\"," + str(var_name) + "," + str(var_address) +
                  "," + "\"" + str(malloc) + "\"" + "," + str(line_begin) + "," + str(line_end) + ");"}

    return printf


def find_return_statements(line):
    """Find all return statements indexes in a line"""
    return_list = list(find_all_occurrences(line, "return"))
    string_constant_list = find_string_constants(line)
    string_constant_list_size = len(string_constant_list)
    for return_index in return_list:
        index = 0
        while string_constant_list_size > index:
            if string_constant_list[index] <= return_index and \
               string_constant_list[index+1] >= (return_index+len("return")):
                return_list.remove(return_index)
            index += 2
    return return_list


def count_line_declarations(print_details, line_count):
    """Count number """
    declaration_counter = 0
    for print_statement in print_details:
        if str(line_count) in print_statement:
            declaration_counter += 1
    return declaration_counter


