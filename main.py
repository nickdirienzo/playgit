import os
import sqlalchemy
from flask import Flask, jsonify, render_template, request, session, Response

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.secret_key = 'yoloswag'

from database import db_session, User

# User handling

def require_login(original_fn):
    def new_fn(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            if user:
                return original_fn(user, *args, **kwargs)
        return Response('Not allowed', 401)
    return new_fn

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter(User.username == request.form['username'],
                             User.password == request.form['password']).first()
    if (user):
        session['user_id'] = user.id
        return jsonify(success=True)
    else:
        return jsonify(success=False)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return jsonify(success=True)

@app.route('/signup', methods=['POST'])
def signup():
    try:
        new_user = User(request.form['username'], request.form['password'])
        db_session.add(new_user)
        db_session.commit()
        session['user_id'] = new_user.id
        return jsonify(success=True)
    except sqlalchemy.exc.IntegrityError:
        return jsonify(success=False)

# API endpoints

# Misc

@app.route('/')
def main(user=None):
    return render_template('user.html', user=user)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
