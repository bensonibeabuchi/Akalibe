#!/bin/bash
echo "Python Version:"
python3 --version

echo "Available Python Versions:"
ls /usr/bin/python*

pip install -r requirements.txt
python3.10 manage.py collectstatic
