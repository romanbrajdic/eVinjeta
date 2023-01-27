from flask import Flask, jsonify, render_template, request, send_from_directory
import os
from helpers import aux
from discord_webhook import DiscordWebhook
import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

# Logs to both console and app.log file
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")
logger = logging.getLogger('server')
handler = logging.FileHandler('app.log')
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

def niceDateTime():
  time = datetime.datetime.now()
  return time.strftime("%H:%M:%S -- %d/%m/%Y")
def niceTime():
  time = datetime.datetime.now()
  return time.strftime("%H:%M:%S")

def spamDiscord(logs = ""):
  content = f"@everyone, napaka na strani ob {niceDateTime()}: \n {logs}"
  webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1062432166950219838/tgl04gFFIMkrASeWX2AlETdsgdTHU3CWufzE1NZQMLQ2eZGVeQyGXj4AAt0k4Dj467B'+'d', content=content)
  webhook.execute()


def discordLog(msg):
  DiscordWebhook(url="https://discord.com/api/webhooks/1062474351196262571/V6M_vfhPy9QEEbM-b1W7qxBr2k5olpyeOY1O2RoKZ178c0Fs9_vYzKqJwES3o3suLSF"+"o", content=msg).execute()


app = Flask(__name__, static_folder="static")
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50 per minute"],   
    storage_uri="memory://",
)


def setHeaders(request):
    headers = request.form["headers"]
    with open("headers.txt", "w") as f:
        f.write(headers)
    discordLog(f"Headers so bili spremenjeni ob {niceDateTime()}")
    return "OK"

@app.route('/favicon.ico')
@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/', methods=['POST'])
def apcall():
    if "headers" in request.form:
      setHeaders(request)
      return "OK"
    registrska = request.form["registrska"]
    try:
      ar =  aux(registrska)
      app.logger.info(f"Registrska \"{registrska}\" je veljavna do {ar} ob {niceTime()}")
      # discordLog(f"Registrska \"{registrska}\" je veljavna do {ar} ob {niceTime()}")
      return render_template('index.html', valid_until = ar, license_plate = registrska)
    except Exception as e:
      spamDiscord(str(e))
      app.logger.error(f"\nNapaka pri {registrska} ob {niceTime()}")
      # discordLog(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!\nNapaka pri {registrska} ob {niceTime()}")
      return render_template('failure.html')

@app.route('/', methods=['GET'])
def index():
    app.logger.info("Zahteva za domačo stran")
    # discordLog(f"Zahteva za domačo stran ob {niceTime()}")
    return render_template('index.html')

if __name__ == '__main__':
    app.run()