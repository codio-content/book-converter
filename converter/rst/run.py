#!/usr/bin/env python3

import sys
import subprocess
import re

ex_dir = ''
file_name = ''
class_name = ''

if len(sys.argv) > 1:
    class_name = sys.argv[1]
    ex_dir = f'.guides/assessments/{sys.argv[2]}'
    file_name = f'{ex_dir}/{class_name}.java'

with open(f'{ex_dir}/wrapper_code') as f:
    wrapper_data = f.read()

with open(f'{ex_dir}/starter_code') as f:
    student_data = f.read()

data = re.sub(r"___", student_data, wrapper_data)

with open(file_name, 'w', encoding="utf-8") as f:
    f.write(data)

retcode = subprocess.call(f'javac {file_name}', shell=True)
if retcode != 0:
    sys.exit(1)

p = subprocess.Popen(f'java -classpath {ex_dir} {class_name}', shell=True, stdout=subprocess.PIPE,
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
