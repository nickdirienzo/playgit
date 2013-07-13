import os
import urllib2
from flask import Flask, jsonify, render_template, request, session, Response, redirect, url_for
from functools import wraps
from rdio import Rdio
import sqlalchemy

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.secret_key = 'yoloswag'
RDIO_CONSUMER_KEY = 'c8pehjw6u8wdatpgxmq8jqkw'
RDIO_CONSUMER_SECRET = '9ADNaSuKSG'

from database import db_session, User, Playlist, Activity

def AuthedRdio(at, ats):
    return Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET), (at, ats))

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

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    request_token = session.get('rt')
    request_token_secret = session.get('rts')
    verifier = request.args.get('oauth_verifier', '')
    if request_token and request_token_secret and verifier:
        rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET), (request_token, request_token_secret))
        rdio.complete_authentication(verifier)
        session['at'] = rdio.token[0]
        session['ats'] = rdio.token[1]
        session['rt'] = ''
        session['rts'] = ''
        rdio_data = rdio.call('currentUser')['result']
        username = rdio_data['url'].replace('/', ' ').split()[-1]
        print 'Creating user model.'
        user = User.query.filter(User.username == username).first()
        if user is None:
            user = User(username=username, token=rdio_data['key'], icon=rdio_data['icon'], first_name=rdio_data['firstName'], last_name=rdio_data['lastName'])
            db_session.add(user)
            db_session.commit()
        print 'Committed.'
        session['user_id'] = user.id
        print session
        return redirect(url_for('main'))
    else:
        # Login failed, clear everything
        print 'Auth failed.'
        logout()
        return redirect(url_for('main'))

@app.route('/user')
def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return jsonify(id=user.id, username=user.username, icon=user.icon, first_name=user.first_name, last_name=user.last_name, is_logged_in=True)

    return jsonify(is_logged_in=False)

@app.route('/user/<user_id>')
def get_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    if user:
        return jsonify(id=user.id, username=user.username, icon=user.icon, first_name=user.first_name, last_name=user.last_name, is_logged_in=True)

    return Response('No such user', 404)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('at', None)
    session.pop('ats', None)
    session.pop('rt', None)
    session.pop('rts', None)
    return jsonify(success=True)

@app.route('/login')
def login():
    access_token = session.get('at')
    access_token_secret = session.get('ats')
    if access_token and access_token_secret:
        rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET), (access_token, access_token_secret))
        try:
            current_user = rdio.call('currentUser')['result']
            print current_user
            return jsonify(current_user=current_user)
        except urllib2.HTTPError:
            # Something went horribly wrong, like Rdio told us our app sucks.
            logout()
            return redirect(url_for('main'))
    else:
        session['at'] = ''
        session['ats'] = ''
        session['rt'] = ''
        session['rts'] = ''
        rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET))
        login_url = rdio.begin_authentication(callback_url='http://' + request.host + '/auth')
        session['rt'] = rdio.token[0]
        session['rts'] = rdio.token[1]
        return jsonify(login_url=login_url)

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
        playlist.initGit(playlist.id) # xxx might not work
        return jsonify(success=True, playlist=playlist.toDict())
    except Exception as e:
        return jsonify(success=False, error='%s' % repr(e))

@app.route('/fork_playlist/<playlist_id>')
@require_login
def fork_playlist(user, playlist_id):
    try:
        playlist = Playlist.query.filter(Playlist.id == playlist_id).first()
        new_playlist = Playlist(uid=user.id, name=playlist.name, parent=playlist.id)
        db_session.add(new_playlist)
        db_session.commit()
        return jsonify(success=True, playlist=new_playlist.toDict(with_songs=True))
    except Exception as e:
        return jsonify(success=False, error='%s' % repr(e))

@app.route('/playlist/<playlist_id>')
@require_login
def get_playlist(user, playlist_id):
    playlist = Playlist.query.filter(Playlist.id == playlist_id).first()
    if not playlist:
        return Response('No such playlist', 404)

    return jsonify(playlist.toDict(with_songs=True))

@app.route('/playlist/<playlist_id>/log')
def get_playlist_log(user, playlist_id):
    playlist = Playlist.query.filter(Playlist.id == playlist_id).first()
    if not playlist:
        return Response('No such playlist', 404)

    return jsonify(playlist.getLog())

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
    query = request.args.get('q')
    types = ['Artist', 'Album', 'Track']
    rdio = AuthedRdio(session.get('at'), session.get('ats'))
    try:
        results = rdio.call('search', params={'query': query, 'types': ','.join(types)})['result']
        return jsonify(results)
    except urllib2.HTTPError:
        return jsonify(error='failure')

@app.route('/activity')
def get_latest_activity():
    latest_activity = Activity.query.order_by(Activity.activity_date.desc()).limit(25).all()
    return jsonify([a.toDict() for a in latest_activity])

# Misc

@app.route('/test')
def testingPage():
    return render_template('test.html')

@app.route('/')
def main():
    return render_template('index.html')

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
