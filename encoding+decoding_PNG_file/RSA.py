from sys import byteorder
import sympy
import random
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome import Random


global repeat
repeat = True

def get_key():
    global d
    global e
    p = 0
    q = 0


    nonce = random.randint(1,20)

    while p == q:
        p = sympy.randprime(60,120)
        q = sympy.randprime(60,120)

    n = p*q
    #print (f'n={n}')
    euler = (p-1)*(q-1)
    e = 17

    for x in range(1,euler):
        if (e*x)%euler == 1:
            break

    d = x   

    public_key = [e,n]
    private_key = [d,n]

    new_key = RSA.generate(2048)
    private_RSA = new_key.exportKey("PEM")
    public_RSA = new_key.publickey().exportKey("PEM")

    fd = open("private_key.pem", "wb")
    fd.write(private_RSA)
    fd.close()

    fd = open("public_key.pem", "wb")
    fd.write(public_RSA)
    fd.close()

    return(public_key,private_key,nonce)

def ECB_encrypt (data, public_key):
    encrypted_data = (data**public_key[0])%public_key[1]
    #if encrypted_data > 32768:
        #print('warning, encrypted value is close to max range')
    encrypted_byte = (encrypted_data).to_bytes(2,byteorder = 'big')  
    return encrypted_byte  
    


def ECB_decrypt(data, private_key):
    decrypted_data = (data**private_key[0])%private_key[1]
    decrypted_byte = (decrypted_data).to_bytes(1,byteorder = 'big')
    return decrypted_byte


def CTR_encrypt(data, public_key, Nonce, counter):
    encrypted_counter = ((Nonce+counter)**public_key[0])%public_key[1]
    encrypted_data = encrypted_counter^data
    encrypted_byte = (encrypted_data).to_bytes(2,byteorder = 'big')  
    return encrypted_byte[1:2]


def CTR_decrypt(data, public_key, Nonce, counter):
    encrypted_counter = ((Nonce+counter)**public_key[0])%public_key[1]
    decrypted_data = encrypted_counter^data
    decrypted_byte = (decrypted_data).to_bytes(2,byteorder = 'big')
    return decrypted_byte[1:2]


def RSA_encrypt(data):
    key = RSA.import_key(open('public_key.pem').read())
    cipher = PKCS1_OAEP.new(key)
    ciphertext = cipher.encrypt(data)
    return ciphertext  


def RSA_decrypt(data):
    key = RSA.import_key(open('private_key.pem').read())
    cipher = PKCS1_OAEP.new(key)
    ciphertext = cipher.decrypt(data)
    return ciphertext



