from hashlib import sha1
from re import finditer, search
import logging

import pdb
from pprint import pprint


'''
Convert code with tags like [student], [blocked] and [hidden] from the starter_code by merging with the user_submission
'''
def process_code_tags(problem_id, user_submission, starter_code):
    #if code from editor, just return straight code
    if (str)(problem_id) == "9999999":
        logger.info("IN HERE PID IS CORRECT")
        if len(user_submission) == 0:
            raise Exception("No code found!")
        else:
            logger.info("length of sub is not 0")
            return user_submission
    else:
        mod_submission = combine_user_code_starter_code(problem_id, user_submission, starter_code)

        # Remove blocked tags from the source code
        mod_submission = mod_submission.replace("[blocked]\r\n", '').replace("[/blocked]\r\n", '')
        mod_submission = mod_submission.replace("[blocked]", '').replace("[/blocked]", '')

        # Remove hidden tags from the source code
        mod_submission = mod_submission.replace("[hidden]\r\n", '').replace("[/hidden]\r\n", '')
        mod_submission = mod_submission.replace("[hidden]", '').replace("[/hidden]", '')


    return mod_submission


def combine_user_code_starter_code(problem_id, user_submission, starter_code):
    # Get student code hashed key
    student_code_key = sha1(str(problem_id).encode('utf-8')).hexdigest()
    student_code_key_list = [m.start() for m in finditer(student_code_key, user_submission)]
    student_code_key_len = len(student_code_key)
    student_code_key_list_len = len(student_code_key_list)

    # Could not find student code
    if len(student_code_key_list) == 0 or len(student_code_key_list) % 2 != 0:
        raise Exception("No student code found!")

    # Get student code from submission and add it to the official exercise (from the database)
    student_code_list = []
    while len(student_code_key_list) >= 2:
        student_code_list.append(
            user_submission[student_code_key_list[0]+student_code_key_len+1: student_code_key_list[1]])
        del student_code_key_list[0], student_code_key_list[0]

    # Create variable mod_submission to handle the fusion of student code with starter_code from the database
    mod_submission = starter_code
    last_tag_size = len('[/student_code]') + 2
    for student_code in student_code_list:
        mod_submission = mod_submission[: mod_submission.find('[student_code]')] + \
                                student_code +\
                                mod_submission[mod_submission.find('[/student_code]')+last_tag_size:]

    return mod_submission


def get_hidden_lines(problem_id, user_submission, starter_code):
    combined_code = combine_user_code_starter_code(problem_id, user_submission, starter_code)

    inside_hidden_tag = False
    hidden_lines_list = []
    line_num = 1
    for line in combined_code.split('\n'):
        if line.find("[hidden]") > -1:
            inside_hidden_tag = True
            continue
        elif line.find("[/hidden]") > -1:
            inside_hidden_tag = False
            continue
        if inside_hidden_tag:
            hidden_lines_list.append(line_num)

        line_num += 1

    return hidden_lines_list
