from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# File paths
USER_FILE = 'data/users.txt'
CHAT_FILE = 'data/chat.txt'

# Challenge flags with points
FLAGS = {
    '1_Stealing_a_bitcoin_transaction_100': {'flag': 'flag1', 'points': 100},
    '2_Dark_Net_Money_200': {'flag': 'flag2', 'points': 200},
    '3_challenge3_300': {'flag': 'flag3', 'points': 300},
    '4_challenge4_400': {'flag': 'flag4', 'points': 400},
    '5_challenge5_500': {'flag': 'flag5', 'points': 500},
}

# Load users and scores
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    users = {}
    with open(USER_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            username = parts[0]
            score = parts[1]
            solved_challenges = parts[2].split(',') if len(parts) > 2 else []
            users[username] = {'score': score, 'solved_challenges': solved_challenges}
    return users

# Save users and scores
def save_users(users):
    with open(USER_FILE, 'w') as f:
        for user, data in users.items():
            solved_challenges = ','.join(data['solved_challenges'])
            f.write(f'{user}:{data["score"]}:{solved_challenges}\n')

# Load chat messages
def load_chat():
    if not os.path.exists(CHAT_FILE):
        return []
    with open(CHAT_FILE, 'r') as f:
        return [line.strip() for line in f]

# Save chat messages
def save_chat(messages):
    with open(CHAT_FILE, 'w') as f:
        for message in messages:
            f.write(f'{message}\n')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        users = load_users()
        if username not in users:
            users[username] = {'score': '0', 'solved_challenges': []}
            save_users(users)
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    users = load_users()
    chat_messages = load_chat()
    feedback = {}

    if request.method == 'POST':
        for challenge, data in FLAGS.items():
            if challenge in request.form:
                submitted_flag = request.form[challenge]
                if submitted_flag == data['flag']:
                    if challenge not in users[username]['solved_challenges']:
                        users[username]['score'] = str(int(users[username]['score']) + data['points'])
                        users[username]['solved_challenges'].append(challenge)
                        feedback[challenge] = 'Correct flag!'
                    else:
                        feedback[challenge] = 'Flag already solved!'
                else:
                    feedback[challenge] = 'Incorrect flag!'
                save_users(users)
        
        if 'message' in request.form:
            message = f"{username}: {request.form['message']}"
            chat_messages.append(message)
            save_chat(chat_messages)
    
    return render_template('index.html', username=username, users=users, chat_messages=chat_messages, FLAGS=FLAGS, feedback=feedback)

@app.route('/leaderboard')
def leaderboard():
    users = load_users()
    sorted_users = sorted(users.items(), key=lambda x: int(x[1]['score']), reverse=True)
    return render_template('leaderboard.html', users=sorted_users)

if __name__ == '__main__':
    app.run(debug=True)