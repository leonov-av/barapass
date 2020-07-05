#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# version 0.1.1

import argparse
import json

# pip3 install clipboard stdiomask pycryptodome
# sudo yum install xclip
# OR
# sudo apt-get install xclip
# python3 barapass.py --interactive
from functions_cli import run_cli

parser = argparse.ArgumentParser(description='Simple password manager')
parser.add_argument('--interactive', help='list all available groups and parameters', action="store_true")

args = parser.parse_args()

f = open("files/settings.json","r")
settings = json.loads(f.read())
f.close()

if args.interactive:
    run_cli(settings)