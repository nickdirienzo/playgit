import os
import sqlalchemy
from flask import Flask, jsonify, render_template, request, session, Response
from functools import wraps

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.secret_key = 'yoloswag'

from database import db_session, User, Playlist, Song

# User handling

def require_login(original_fn):
    @wraps(original_fn)
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

@app.route('/playlists')
@require_login
def get_user_playlists(user):
    pass

@app.route('/create_playlist', methods=['POST'])
@require_login
def create_playlist(user):
    pass

@app.route('/fork_playlist/<playlist_id>')
@require_login
def fork_playlist(user, playlist_id):
    pass

@app.route('/playlist/<playlist_id>/current')
@require_login
def get_playlist(user, playlist_id):
    pass

@app.route('/playlist/<playlist_id>/log')
def get_playlist_log(user, playlist_id):
    pass

@app.route('/diff/<playlist_id1>/<rev1>/<playlist_id2>/<rev2>')
@require_login
def get_playlist_diff(user, playlist_id1, rev1, playlist_id2, rev2):
    pass

@app.route('/commit/<playlist_id>', methods=['POST'])
@require_login
def commit_playlist_changes(user, playlist_id):
    pass

# Misc

@app.route('/')
def main(user=None):
    return render_template('user.html', user=user)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
