#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# version 0.1.1

import clipboard
import argparse
import re
import stdiomask
import hashlib
import json
import base64
from Crypto.Cipher import AES

# pip3 install clipboard stdiomask pycryptodome
# sudo yum install xclip
# OR
# sudo apt-get install xclip
# python3 barapass.py --interactive

def get_values_by_address(address, lines):
    value = dict()
    for line in lines:
        if len(line.split("|")) == 3:
            if line.split("|")[0] + ":" + line.split("|")[1] == address:
                value[address] = line.split("|")[2]
    return(value)


def get_data_lines(content):
    group = ""
    lines = list()
    for line in content.split("\n"):
        if "###" in line:
            group = re.sub("[ \t]*#*[ \t]*","", line)
        elif line != "":
                #print(line)
                lines.append(line)
                # print(group)
    return lines


def process_search_loop(search_request, lines): #Search
    found_addresses = list()
    for line in lines:
        if len(line.split("|")) == 3:
            if re.findall(search_request, line.split("|")[0]):
                address = line.split("|")[0] + ":" + line.split("|")[1]
                found_addresses.append(address)

    if found_addresses != list():
        for address in found_addresses:
            print("Found: " + address)
        for address in found_addresses:
            value = get_values_by_address(address, lines)
            print("Coppied to clipboard: " + address + " (next value: Y/n)", end=" ")
            clipboard.copy(value[address])
            answer = input()
            if answer == "n":
                break


def get_container_content(container_file_name, container_password):
    container_data = {}
    container_content = ""
    if container_file_name == "":
        container_data =  {'error': True, 'status': 'ERROR: Container name was not specified!'}
    elif container_password == "":
        container_data = {'error': True, 'status': 'ERROR: Container password is empty!'}
    else:
        try:
            container_content = get_plaintext(container_file_name, container_password)
        except:
            container_data = {'error': True, 'status': 'ERROR: Container ' + container_file_name + ' is not found!'}

        if container_content == "":
            container_data = {'error': True, 'status': 'ERROR: Container ' + container_file_name + ' is empty!'}
        else:
            container_data = {'error': False, 'container_content': container_content,
                              'status': 'OK: Container ' + container_file_name + ' was loaded successfully'}

    print(container_data['status'])
    return(container_data)

def encrypt_raw_file(raw_file_name, container_file_name, container_password):
    f = open(raw_file_name)
    data = f.read().encode("utf8")
    f.close()

    key = hashlib.sha256(container_password.encode("utf8")).digest()
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)

    container = {}
    container['profile'] = "Simple AES" # https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html
    container['nonce'] = base64.b64encode(nonce).decode("utf8")
    container['tag'] = base64.b64encode(tag).decode("utf8")
    container['ciphertext'] = base64.b64encode(ciphertext).decode("utf8")

    f = open(container_file_name,"w")
    f.write(json.dumps(container))
    f.close()

    print("OK: Container " + container_file_name + " was created successfully")

def get_plaintext(container_file_name, container_password):
    key = hashlib.sha256(container_password.encode("utf8")).digest()

    f = open(container_file_name, "r")
    container = json.loads(f.read())
    f.close()

    profile = container['profile']
    nonce = base64.b64decode(container['nonce'])
    tag = base64.b64decode(container['tag'])
    ciphertext = base64.b64decode(container['ciphertext'])

    plaintext = ""
    if profile == "Simple AES":
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        try:
            plaintext = cipher.decrypt(ciphertext).decode("utf8")
            cipher.verify(tag)
            print("OK: Container " + container_file_name + " was decrypted successfully")
        except ValueError:
            print("ERROR: Container password is wrong or container " + container_file_name + " is corrupted!")
    return(plaintext)


def decrypt_container(container_file_name, raw_file_name, container_password):
    plaintext = get_plaintext(container_file_name, container_password)
    if plaintext != "":
        f = open(raw_file_name, "w")
        f.write(plaintext)
        f.close()
        print("OK: Raw file " + raw_file_name + " was created")


def run_cli(favorite_commands):
    container_file_name = ""
    container_password = ""
    print("Interactive mode (q for exit; fc for favorite commands)")
    input_value = ""
    while input_value != "q":
        print("Command >>", end=" ")
        input_value = input()

        # Fast commands
        if input_value.split(" ")[0] == "fc": # List all favourite commands
            input_value = ""
            i = 0
            for fc in favorite_commands:
                print("fc" +str(i) + ": " + fc)
                i+=1
        if re.findall("^fc[0-9]", input_value.split(" ")[0]): # Changing input_value to favourite command
            num = re.findall("fc([0-9]*)",input_value.split(" ")[0])[0]
            print("Using fnc" +str(num) + ": " + favorite_commands[int(num)])
            input_value = favorite_commands[int(num)]

        # Use container
        # E.g.: Use container_file_name
        if input_value.split(" ")[0] in ['Use','use','u']: # Search command
            container_file_name = input_value.split(" ")[1]
            container_password = stdiomask.getpass(prompt="Container " + container_file_name + " password >> ")
            container_data = get_container_content(container_file_name, container_password)

        # Decrypt container
        # E.g.: Decrypt container_file_name raw_file_name
        if input_value.split(" ")[0] in ['Decrypt','decrypt','d']: # Search command
            container_file_name = input_value.split(" ")[1]
            raw_file_name = input_value.split(" ")[2]
            container_password = stdiomask.getpass(prompt="Container " + container_file_name + " password >> ")
            decrypt_container(container_file_name, raw_file_name, container_password)

        # Encrypt raw file
        # E.g.: Encrypt raw_file_name container_file_name
        if input_value.split(" ")[0] in ['Encrypt','encrypt','e']: # Search command
            raw_file_name = input_value.split(" ")[1]
            container_file_name = input_value.split(" ")[2]
            container_password = stdiomask.getpass(prompt="Container " + container_file_name + " password >> ")
            encrypt_raw_file(raw_file_name, container_file_name, container_password)

        # Search
        # E.g.: Search Email
        if input_value.split(" ")[0] in ['Search','search','s']: # Search command
            if 'container_content' in container_data:
                container_content = container_data['container_content']
                lines = get_data_lines(container_content)
                if len(input_value.split(" ")) == 1: # Don't have search requests in command
                    print("Search request >>", end=" ")
                    search_request = input()
                else:
                    search_request = input_value.split(" ")[1]
                process_search_loop(search_request, lines)
            else:
                if container_data['error']:
                    print(container_data['status'])


parser = argparse.ArgumentParser(description='Simple password manager')
parser.add_argument('--interactive', help='list all available groups and paramaeters', action="store_true")

args = parser.parse_args()
favorite_commands = []

if args.interactive:
    run_cli(favorite_commands)