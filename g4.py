import csv
import hashlib
import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['First Name']
        last_name = request.form['Last Name']
        name = first_name + ' ' + last_name
        dob = request.form['dob']
        username = request.form['username']
        password = request.form['password']
        
        # Validation checks
        if not first_name or not last_name or not dob or not username or not password :
            flash('All fields are required')
            return redirect(url_for('register'))
        
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            flash('Username must contain only letters and numbers')
            return redirect(url_for('register'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long')
            return redirect(url_for('register'))
        
        
        if os.path.exists(os.path.join(app.config['USER_FOLDER'], username)):
            flash('Username already exists')
            return redirect(url_for('register'))
        
        os.makedirs(os.path.join(app.config['USER_FOLDER'], username))
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with open(os.path.join(app.config['USER_FOLDER'], 'users.csv'), 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, password_hash, name, dob])
        
        return redirect(url_for('login'))
    return render_template('register1.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('login'))
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with open(os.path.join(app.config['USER_FOLDER'], 'users.csv'), 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == username and row[1] == password_hash:
                    session['username'] = username
                    return redirect(url_for('homepage', username=username))
        
        flash('Invalid username or password')
        return redirect(url_for('login'))
    return render_template('r1.html')



@app.route('/add_entry', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        username = session['username']
        title = request.form['title']
        date = request.form['date']
        content = request.form['content']
        
        if not title or not date or not content:
            flash('All fields are required')
            return redirect(url_for('add_entry'))
        
        entry_filename = title + ' ' + date + '.txt'
        user_folder = os.path.join(app.config['USER_FOLDER'], username)
        if os.path.exists(os.path.join(user_folder, entry_filename)):
            flash('An entry with this title already exists for the given date')
            return redirect(url_for('add_entry'))
        
        with open(os.path.join(user_folder, entry_filename), 'w') as f:
            f.write(content)
        
        return redirect(url_for('homepage', username=username))
    return render_template('add_entry.html')


@app.route('/homepage',methods=['GET'])
def homepage():
    username = session['username']
    user_folder = os.path.join(app.config['USER_FOLDER'], username)
    entries = []

    for filename in os.listdir(user_folder):
        if filename.endswith('.txt'):
            with open(os.path.join(user_folder, filename), 'r') as f:
                s=filename.split('.txt')[0]
                l=s.split(' ')
                entries.append((l[0], l[1]))
    entries = entries[:4]  # Get the first four entries

    return render_template('homepage.html', entries=entries)

@app.route('/logout',methods=['GET'])
def logout():
    if request.method=='GET':
        session['username']=None
        print(session['username'])
    return render_template('r1.html')



@app.route('/all_entries', methods=['GET'])
def all_entries():
    username = session['username']
    user_folder = os.path.join(app.config['USER_FOLDER'], username)
    entries = []

    for filename in os.listdir(user_folder):
        if filename.endswith('.txt'):
            with open(os.path.join(user_folder, filename), 'r') as f:
                s=filename.split('.txt')[0]
                l=s.split(' ')
                content=f.read()
                entries.append((l[0], l[1], content, filename))

    # Filter entries based on the title query parameter
    title = request.args.get('title')
    if title:
        entries = [e for e in entries if title.lower() in e[0].lower()]

    return render_template('all_entries.html', entries=entries, title=title)

@app.route('/edit_entry/<filename>', methods=['GET', 'POST'])
def edit_entry(filename):
    username = session['username']
    user_folder = os.path.join(app.config['USER_FOLDER'], username)
    entry_path = os.path.join(user_folder, filename)

    if request.method == 'POST':
        new_content = request.form['content']
        
        # Check if the new content is empty
        if not new_content.strip():
            flash('Content cannot be empty')
            return redirect(url_for('edit_entry', filename=filename))
        
        with open(entry_path, 'w') as f:
            f.write(new_content)
        return redirect(url_for('all_entries'))

    with open(entry_path, 'r') as f:
        content = f.read()

    return render_template('edit_entry.html', filename=filename, content=content)


@app.route('/delete_entry/<filename>')
def delete_entry(filename):
    username = session['username']
    user_folder = os.path.join(app.config['USER_FOLDER'], username)
    entry_path = os.path.join(user_folder, filename)

    if os.path.isfile(entry_path):
        os.remove(entry_path)

    return redirect(url_for('all_entries'))



import os

app.config['USER_FOLDER'] = 'users'
app.config['SECRET_KEY'] = 'mysecretkey'

if __name__ == '__main__':
    app.config['USER_FOLDER'] = 'users'
    app.config['SECRET_KEY'] = 'mysecretkey'

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

