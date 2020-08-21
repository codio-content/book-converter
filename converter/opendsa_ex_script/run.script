#!/usr/bin/env python3

import sys
import subprocess
import re

sys.path.append('/usr/share/codio/assessments')
from lib.grade import send_partial

ex_path = ''
ex_private_path = ''
file_path = ''
class_name = ''

if len(sys.argv) > 1:
    class_name = sys.argv[1]
    ex_path = f'{sys.argv[2]}'
    ex_private_path = f'.guides/secure/assessments/{ex_path}'
    file_path = f'{ex_private_path}/{class_name}.java'

with open(f'{ex_private_path}/wrapper_code.java') as f:
    wrapper_data = f.read()

with open(f'exercises/{ex_path}/starter_code.java') as f:
    student_data = f.read()

data = re.sub(r"___", student_data, wrapper_data)

with open(file_path, 'w', encoding="utf-8") as f:
    f.write(data)

ret_code = subprocess.call(f'javac -d /tmp/ {file_path} {ex_private_path}/Tester.java', shell=True)
if ret_code != 0:
    sys.exit(1)

p = subprocess.Popen(f'java -cp /tmp/ Tester', shell=True, stdout=subprocess.PIPE,
                     universal_newlines=True)
output, error = p.communicate()
output = output.strip()

if p.returncode != 0:
    sys.exit(1)

if error:
    print(error)
    sys.exit(1)

output = output.split('\n')
total_tests = output.pop(0)
passed_tests = output.pop(0)
feedback = '\n'.join(output)

grade = int(passed_tests) / int(total_tests) * 100
print(feedback)
print("<br><h1>Total Grade: %d </h1>" % grade)
res = send_partial(grade)
exit(0 if res else 1)
