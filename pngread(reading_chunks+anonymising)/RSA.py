import sympy
def Encrypt(data):

    str_encrypted = ""

    while len(str_encrypted) != 3:

        p = 0
        q = 0            

        while p == q:
            p = sympy.randprime(32,100)
            q = sympy.randprime(32,100)

        #print(f'p={p}')
        #print(f'q={q}')
        n = p*q
        #print (f'n={n}')
        euler = (p-1)*(q-1)
        e = 17

        for x in range(1,euler):
            global d
            if (e*x)%euler == 1:
                d = x
                break
    
        public_key = [e,n]
        private_key = [d,n]
        encrypted_data = (data**public_key[0])%public_key[1]
        str_encrypted = str(encrypted_data)
        if len(str_encrypted) < 3:
            for i in range(3-len(str_encrypted)):
                str_encrypted = "0" + str_encrypted
        
    aux = "111"
    print (f"data: {data}")
    print (f'{aux.encode("utf-8")}')
    print (f'encrypted: {str_encrypted}')
    print (f'encoded: {str_encrypted.encode("utf-8")}')
    #decrypted_data = (encrypted_data**private_key[0])%private_key[1]
    #print (f'decrypted: {decrypted_data}')
    print("")
    return str_encrypted.encode("utf-16")

'''for i in range(20):
    Encrypt(999999)'''

