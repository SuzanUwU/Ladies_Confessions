from flask import Flask, request, render_template, redirect, url_for
import requests
import random
import string
from flask import session
import uuid
import secrets
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
app.secret_key = os.getenv('SECRET_KEY')

def generate_submission_id(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def send_to_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    r = requests.post(url, data=payload)
    return r.ok

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        answer = request.form.get('answer')
        if answer == 'yes':
            return redirect(url_for('submit', is_update='true'))
        else:
            return redirect(url_for('update_denied'))
    return render_template('update.html')

@app.route('/update-denied')
def update_denied():
    return render_template('update_denied.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    is_update = request.args.get('is_update', 'false') == 'true'

    if request.method == 'GET':
        token = str(uuid.uuid4())
        session['form_token'] = token
        return render_template('submit.html', form_token=token, is_update=is_update)

    if request.method == 'POST':
        token = request.form.get('form_token')
        if not token or token != session.pop('form_token', None):
            return "Form already submitted", 400

        struggle = request.form.get('struggle') or "N/A"
        summary = request.form.get('summary') or "N/A"
        nickname = request.form.get('nickname') or "N/A"

        if is_update:
            telegram_title = f"🔄 Update by nickname: {nickname}"
            post_type = "update"
        else:
            telegram_title = "🆕 New post"
            post_type = "normal"

        message = (
            f"{telegram_title}\n"
            f"**Title:** {summary}\n"
            f"**Nickname:** {nickname}\n"
            f"**Type:** {post_type}\n"
            f"**Letter:**\n{struggle}"
        )

        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(telegram_url, json=payload)

        return redirect('/thankyou')


@app.route('/thankyou')
def thankyou():
    # Token already popped in /submit POST; no need to pop here.
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
