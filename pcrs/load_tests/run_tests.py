from collections import defaultdict
import re
import subprocess
import sys


mean = re.compile(r'Time per request:\s*(\d+.\d+)\s*\[ms\] \(mean\)')
mean_concurrent = re.compile(r'Time per request:\s*(\d+.\d+)\s*\[ms\] '
                             r'\(mean, across all concurrent requests\)')
html_transferred = re.compile(r'HTML transferred:\s*(\d+)\s*bytes')
non_200_responses = re.compile(r'Non-2xx responses:\s*\d+')


def run_get_test(total, concurrent, url):
    return subprocess.check_output(
        ['ab', '-n', str(total), '-c', str(concurrent),
         '-C', 'sessionid={}'.format(sessionid),
         url
        ]).decode('utf-8')


def run_post_test(total, concurrent, url, filename):
    return subprocess.check_output(
        ['ab', '-n', str(total), '-c', str(concurrent),
         '-C', 'sessionid={}'.format(sessionid),
         '-p', filename, '-T', 'applicatio/json',
         url
        ]).decode('utf-8')


def process_output(output):
    transferred = html_transferred.findall(output)[0]
    non_200 = non_200_responses.findall(output)
    if not transferred:
        print('No html was transferred, '
              'please check the cookies and/or sent data.')
    if non_200:
        print('There were {} non-200 responses'.format(non_200[0]))
    else:
        m1 = mean.findall(output)[0]
        m2 = mean_concurrent.findall(output)[0]
        return m1, m2


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sessionid = input('Session id: ')
    else:
        _, sessionid = sys.argv

    tests = open('tests.txt').readlines()
    for test in tests:
        url, post_file = test.split(',')
        print(url)
        results = defaultdict(dict)
        for num_users in [1]:
            for num_concurrent in [1]:
                if num_users >= num_concurrent:
                    if post_file.strip():
                        output = run_post_test(
                            num_users, num_concurrent, url, post_file)
                    else:
                        output = run_get_test(
                            num_users, num_concurrent, url)
                    results[num_users][num_concurrent] = process_output(output)
                else:
                    results[num_users][num_concurrent] = '-'
        for key in sorted(results.keys()):
            print([results[key][key2] for key2 in sorted(results[key].keys())])