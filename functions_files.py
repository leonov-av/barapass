import base64
import hashlib
import json

from Crypto.Cipher import AES

dir = "files/"
def make_container_file_from_raw_file(raw_file_name, container_file_name, container_password):
    f = open(dir + raw_file_name)
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

    f = open(dir + container_file_name,"w")
    f.write(json.dumps(container))
    f.close()

    print("OK: Container " + container_file_name + " was created successfully")


def get_plaintext_from_container_file(container_file_name, container_password):
    key = hashlib.sha256(container_password.encode("utf8")).digest()

    f = open(dir + container_file_name, "r")
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


def make_raw_file_from_container_file(container_file_name, raw_file_name, container_password):
    plaintext = get_plaintext_from_container_file(container_file_name, container_password)
    if plaintext != "":
        f = open(raw_file_name, "w")
        f.write(plaintext)
        f.close()
        print("OK: Raw file " + raw_file_name + " was created")