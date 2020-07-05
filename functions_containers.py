from functions_files import get_plaintext_from_container_file


def get_container_content(container_file_name, container_password):
    container_data = {}
    container_content = ""
    if container_file_name == "":
        container_data =  {'error': True, 'status': 'ERROR: Container name was not specified!'}
    elif container_password == "":
        container_data = {'error': True, 'status': 'ERROR: Container password is empty!'}
    else:
        try:
            container_content = get_plaintext_from_container_file(container_file_name, container_password)
        except:
            container_data = {'error': True, 'status': 'ERROR: Container ' + container_file_name + ' is not found!'}

        if container_content == "":
            container_data = {'error': True, 'status': 'ERROR: Container ' + container_file_name + ' is empty!'}
        else:
            container_data = {'error': False, 'container_content': container_content,
                              'status': 'OK: Container ' + container_file_name + ' was loaded successfully'}

    print(container_data['status'])
    return(container_data)


