import re
import clipboard
import stdiomask

from functions_containers import get_container_content
from functions_data_lines import get_values_by_address, get_data_lines
from functions_files import make_container_file_from_raw_file, make_raw_file_from_container_file


def get_next_address(address, all_addresses):
    n = all_addresses.index(address)
    if n == len(all_addresses)-1:
        return False
    else:
        return(all_addresses[n+1])


def get_previous_address(address, all_addresses):
    n = all_addresses.index(address)
    if n == 0:
        return address
    else:
        return (all_addresses[n - 1])


def process_search_loop(search_request, lines): #Search
    all_addresses = list()
    for line in lines:
        if len(line.split("|")) == 3:
            if re.findall(search_request, line.split("|")[0]):
                address = line.split("|")[0] + ":" + line.split("|")[1]
                all_addresses.append(address)

    if all_addresses != list():
        for address in all_addresses:
            print("Found: " + address)

        address = all_addresses[0]
        answer = ""
        while answer != "n":
            value = get_values_by_address(address, lines)
            clipboard.copy(value[address])

            print("Copied to clipboard: " + address + " (next value: Y/n | [p]revious | [s]ame)", end=" ")
            answer = input()

            if answer == "":
                answer = "y"

            if answer == "Y" or answer == "y":
                address = get_next_address(address, all_addresses)
            elif answer == "p":
                address = get_previous_address(address, all_addresses)
            elif answer == "n":
                break

            if address == False:
                break

def run_cli(settings):
    container_file_name = ""
    container_password = ""
    print("Interactive mode (q for exit; fc for favorite commands)")
    favorite_commands = settings['favorite_commands']
    first_command = True
    input_value = settings['startup_command']
    while input_value != "q":

        if first_command and input_value != "":
            print("Command >> " + input_value)
            first_command = False
        else:
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
            make_raw_file_from_container_file(container_file_name, raw_file_name, container_password)

        # Encrypt raw file
        # E.g.: Encrypt raw_file_name container_file_name
        if input_value.split(" ")[0] in ['Encrypt','encrypt','e']: # Search command
            raw_file_name = input_value.split(" ")[1]
            container_file_name = input_value.split(" ")[2]
            container_password = stdiomask.getpass(prompt="Container " + container_file_name + " password >> ")
            container_password2 = stdiomask.getpass(prompt="Repeat container " + container_file_name + " password >> ")
            if container_password == container_password2:
                make_container_file_from_raw_file(raw_file_name, container_file_name, container_password)
            else:
                print("Error: The entered passwords do not match!")

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