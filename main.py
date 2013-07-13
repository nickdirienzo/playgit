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

@app.route('/user')
def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return jsonify(id=user.id, username=user.username, is_logged_in=True)

    return jsonify(is_logged_in=False)

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

# API endpoints

@app.route('/playlists')
@require_login
def get_user_playlists(user):
    playlists = Playlist.query.filter(Playlist.uid == user.id).all()
    return jsonify(playlists=[p.toDict() for p in playlists])

@app.route('/create_playlist', methods=['POST', 'GET'])
@require_login
def create_playlist(user):
    try:
        name = request.form['name']
        if request.form['parent']:
            parent = int(request.form['parent'])
        else:
            parent = None
        playlist = Playlist(uid=user.id, name=name, parent=parent)
        db_session.add(playlist)
        db_session.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error='%s' % repr(e))

@app.route('/fork_playlist/<playlist_id>')
@require_login
def fork_playlist(user, playlist_id):
    pass

@app.route('/playlist/<playlist_id>')
@require_login
def get_playlist(user, playlist_id):
    playlist = Playlist.query.filter(Playlist.id == playlist_id).first()
    if not playlist:
        return Response('No such playlist', 404)

    return jsonify(playlist.toDict(with_songs=True))

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

@app.route('/search')
@require_login
def search_for_song(user):
    # TODO nick
    pass

# Misc

@app.route('/test')
def testingPage(user):
    return render_template('user.html', user=user)

@app.route('/')
def main():
    return render_template('index.html')

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
