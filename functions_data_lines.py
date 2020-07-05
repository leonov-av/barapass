import re


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