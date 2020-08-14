#!/usr/bin/env python3

import sys
import subprocess
import re

ex_path = ''
file_path = ''
class_name = ''

if len(sys.argv) > 1:
    class_name = sys.argv[1]
    ex_path = f'{sys.argv[2]}'
    file_path = f'{ex_path}/{class_name}.java'

with open(f'{ex_path}/wrapper_code.java') as f:
    wrapper_data = f.read()

with open(f'../../../exercises/{ex_path}/starter_code.java') as f:
    student_data = f.read()

data = re.sub(r"___", student_data, wrapper_data)

with open(file_path, 'w', encoding="utf-8") as f:
    f.write(data)

ret_code = subprocess.call(f'javac -d /tmp/ {file_path} {ex_dir}/Tester.java', shell=True)
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

print(output)
print('<br/><hr/><h3>Challenge Feedback</h3>')

if output != '323':
    print('Your code is not outputing the correct value')
else:
    print('Well done you passed the challenge!')
