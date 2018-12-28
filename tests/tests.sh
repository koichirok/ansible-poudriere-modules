#!/bin/sh -e

cd "${0%/*}"

python -m py_compile ../module_utils/*.py
python -m py_compile ../library/*.py

ansible-playbook -i 'localhost,' test.yml
