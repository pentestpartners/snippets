import binascii

key="Insert Key Here"

def rc4_crypt( data , key ):
    
    S = range(256)
    j = 0
    out = []
    
    #KSA Phase
    for i in range(256):
        j = (j + S[i] + ord( key[i % len(key)] )) % 256
        S[i] , S[j] = S[j] , S[i]
    
    #PRGA Phase
    i = j = 0
    for char in data:
        i = ( i + 1 ) % 256
        j = ( j + S[i] ) % 256
        S[i] , S[j] = S[j] , S[i]
        out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))
        
    return ''.join(out)

with open("Insertfilenamehere.txt","r") as f:
   lines=f.readlines()
   for line in lines:
      raw=binascii.unhexlify(line.strip())
      rc4_crypt(raw,key)

