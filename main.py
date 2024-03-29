import time, datetime
import os
import urllib2
from flask import Flask, jsonify, render_template, request, session, Response, redirect, url_for
from functools import wraps
from rdio import Rdio

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.secret_key = 'yoloswag'
RDIO_CONSUMER_KEY = 'c8pehjw6u8wdatpgxmq8jqkw'
RDIO_CONSUMER_SECRET = '9ADNaSuKSG'

from database import db_session, User, Playlist, Activity, Song, PullRequest, transform_track_keys

def AuthedRdio(at, ats):
    return Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET), (at, ats))

def import_new_user_playlists(playlist_json, uid):
    for playlist in playlist_json:
        if playlist['isViewable']:
            print 'Playlist added.'
            p = Playlist(uid, playlist['name'], None, playlist['key'], playlist['description'], playlist['url'])
            db_session.add(p)
            db_session.commit()
            p.initGit()
            track_ids = list()
            for song in playlist['tracks']:
                ts = Song.query.filter(Song.key == song['key']).first()
                if not ts:
                    ts = Song(song['name'], song['album'], song['artist'], song['icon'], song['key'])
                    db_session.add(ts)
                    db_session.commit()
                    track_ids.append(song['key'])
            p.git().writeTrackKeys(track_ids)
        else:
            continue

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
        rdio_data = rdio.call('currentUser', params={'extras': 'username,displayName'})['result']
        username = rdio_data['username']
        print 'Creating user model.'
        user = User.query.filter(User.username == username).first()
        if user is None:
            user = User(username=username, key=rdio_data['key'], icon=rdio_data['icon'], name=rdio_data['displayName'])
            db_session.add(user)
            db_session.commit()
            playlists = rdio.call('getPlaylists', params={'extras': 'tracks,description,isViewable'})['result']['owned']
            #print playlists
            import_new_user_playlists(playlists, user.id)
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
            return jsonify(id=user.id, username=user.username, icon=user.icon, name=user.name, is_logged_in=True)

    return jsonify(is_logged_in=False)

@app.route('/user/<user_id>')
def get_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    if user:
        return jsonify(id=user.id, username=user.username, icon=user.icon, name=user.name)

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
            rdio_data = rdio.call('currentUser', params={'extras': 'username,displayName'})['result']
            username = rdio_data['username']
            user = User.query.filter(User.username == username).first()
            session['user_id'] = user.id
            print current_user
            return redirect(url_for('main'))
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

@app.route('/create_playlist', methods=['POST'])
@require_login
def create_playlist(user):
    print 'tt'
    try:
        print 'test'
        name = request.form['name']
        if 'parent' in request.form:
            parent = int(request.form['parent'])
        else:
            parent = None
        playlist = Playlist(uid=user.id, name=name, parent=parent)
        db_session.add(playlist)
        db_session.commit()
        playlist.initGit() # xxx might not work
        fork_activity = Activity(user.id, " created <a href='#playlist?id=%d'>%s</a>" % (playlist.id, name))
        db_session.add(fork_activity)
        db_session.commit()
        return jsonify(success=True, playlist=playlist.toDict())
    except Exception as e:
        return jsonify(success=False, error='%s' % repr(e))

@app.route('/fork_playlist/<playlist_id>')
@require_login
def fork_playlist(user, playlist_id):
    try:
        playlist = Playlist.query.filter(Playlist.id == playlist_id).first()
        print playlist
        new_playlist = Playlist(uid=user.id, name=playlist.name, parent=playlist.id, key=playlist.key, description=playlist.description)
        db_session.add(new_playlist)
        db_session.commit()
        new_playlist.initGit()
        fork_activity = Activity(user.id, " forked <a href='#playlist?id=%d'>%s</a>" % (new_playlist.id, playlist.name))
        db_session.add(fork_activity)
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

    return jsonify(playlist=playlist.toDict(with_songs=True, with_prs=True))

@app.route('/playlist/<playlist_id>/log')
@require_login
def get_playlist_log(user, playlist_id):
    playlist = Playlist.query.filter(Playlist.id == playlist_id).first()
    if not playlist:
        return Response('No such playlist', 404)

    return jsonify(history=playlist.getLog())

@app.route('/pr/<pr_id>')
@require_login
def get_pr(user, pr_id):
    pr = PullRequest.query.filter(PullRequest.id==pr_id).first()
    if not pr:
        return jsonify(error='invalid pr')
    return jsonify(pr.toDict()) 

@app.route('/diff/<playlist_id1>/<rev1>/<playlist_id2>/<rev2>')
@require_login
def get_playlist_diff(user, playlist_id1, rev1, playlist_id2, rev2):
    pass

@app.route('/diff/<playlist_id_1>/<playlist_id_2>')
@require_login
def get_remote_diff(user, playlist_id_1, playlist_id_2):
    playlist_1 = Playlist.query.filter(Playlist.id == playlist_id_1 and Playlist.uid == session.get('user_id')).first()
    if not playlist_1:
        return jsonify(error='invalid playlist')
    changes = playlist_1.git().diff(str(playlist_id_2))

    songIdsThatChanged = []
    howTheyChanged = []
    for change in changes:
        songIdsThatChanged.append(change[1])
        howTheyChanged.append(change[0])
    songsThatChanged = transform_track_keys(songIdsThatChanged)

    changes = []
    for i, song in enumerate(songsThatChanged):
        changes.append({"change": howTheyChanged[i], "songName": songsThatChanged[i]['name'], 'songArtist': songsThatChanged[i]['artist']})
    return jsonify(diff=changes)

@app.route('/commit/<playlist_id>', methods=['POST'])
@require_login
def commit_playlist_changes(user, playlist_id):
    songs = request.json['songs']
    song_keys = list()
    for song in songs:
        if not Song.query.filter(Song.key == song['key']).first():
            s = Song(song['name'], song['album'], song['artist'], song['artwork_url'], song['key'])
            db_session.add(s)
        song_keys.append(song['key'])
    db_session.commit()
    if not songs:
        return jsonify(error='no keys sent')

    playlist = Playlist.query.filter(Playlist.id == playlist_id and Playlist.uid == session.get('user_id')).first()
    print playlist
    if not playlist:
        return jsonify(error='invalid playlist')
    current_songs = set(playlist.git().getTrackIds())
    song_keys = set(song_keys)
    added = song_keys - current_songs
    removed = current_songs - song_keys
    rdio = AuthedRdio(session.get('at'), session.get('ats'))
    if len(added) > 0:
        added_msg = 'Added '
        for a in added:
            ts = Song.query.filter(Song.key == a).first()
            if ts:
                added_msg += '%s by %s ' % (ts.name, ts.artist)
    else:
        added_msg = ''
    if len(removed) > 0:
        removed_msg = 'Removed '
        for r in removed:
            s = Song.query.filter(Song.key == r).first()
            if s:
                removed_msg += '%s by %s ' % (s.name, s.artist)
    else:
        removed_msg = ''
    msg = added_msg + ' ' + removed_msg
    playlist.git().update(song_keys)
    playlist.git().commit(msg)

    activity = Activity(user.id, 'modified <a href="#playlist?id=%d">%s</a>' % (playlist.id, playlist.name))
    db_session.add(activity)
    db_session.commit()

    if playlist.key:
        reply = rdio.call('deletePlaylist', params={'playlist': playlist.key})
    try:
        print 'inside'
        new_playlist = rdio.call('createPlaylist', params={'name': playlist.name, 'description': 'test', 'tracks': ','.join(song_keys)})['result']
        if new_playlist['name'] == playlist.name:
            print 'created new playlist'
            if new_playlist['key'] != playlist.key:
                db_session.query(Playlist).filter(Playlist.id == playlist_id).update({'key': new_playlist['key'], 'url': new_playlist['url']})
                db_session.commit()
            return jsonify(sync=True, commit=True)
    except KeyError as e:
        print repr(e)
        return jsonify(sync=False, commit=True)

@app.route('/search')
@require_login
def search_for_song(user):
    query = request.args.get('q')
    types = ['Track']
    rdio = AuthedRdio(session.get('at'), session.get('ats'))
    try:
        results = rdio.call('search', params={'query': query, 'types': ','.join(types)})['result']
        return jsonify(results)
    except urllib2.HTTPError:
        return jsonify(error='failure')

@app.route('/activity')
def get_latest_activity():
    latest_activity = Activity.query.order_by(Activity.activity_date.desc()).limit(25).all()
    return jsonify(activity=[a.toDict() for a in latest_activity])

@app.route('/pr/<forked_playlist_id>/<parent_playlist_id>', methods=['GET'])
@require_login
def pull_request(user, forked_playlist_id, parent_playlist_id):
    parent = Playlist.query.filter(Playlist.id == parent_playlist_id).first()
    fork = Playlist.query.filter(Playlist.id == forked_playlist_id).first()
    if not parent or not fork:
        return jsonify(error='invalid playlist id')
    pr = PullRequest(parent.uid, parent.id, session.get('user_id'), fork.id, False, None, datetime.datetime.now())
    db_session.add(pr)
    db_session.commit()
    pr_activity = Activity(user.id, 'initiated a Pull Request for <a href="#playlist?id=%d">%s</a>' % (parent.id, parent.name))
    db_session.add(pr_activity)
    db_session.commit()
    return jsonify(success=True)

@app.route('/pr/<parent_playlist_id>/<forked_playlist_id>/accept')
@require_login
def accept_pull_request(user, parent_playlist_id, forked_playlist_id):
    parent = Playlist.query.filter(Playlist.id == parent_playlist_id and Playlist.uid == user.id).first()
    forked = Playlist.query.filter(Playlist.id == forked_playlist_id).first()
    if not parent or not forked:
        return jsonify(error='invalid playlist id')
    fork_owner = User.query.filter(User.id == forked.uid).first()
    db_session.query(PullRequest).filter(PullRequest.parent_uid == user.id and PullRequest.parent_pid == parent_playlist_id and PullRequest.child_pid == forked_playlist_id).update({'accepted': True, 'accepted_on': datetime.datetime.now()})
    db_session.commit()
    parent.git().merge(str(forked_playlist_id), parent.name, forked.name)
    pr_activity = Activity(user.id, " accepted a pull request from %s for <a href='#playlist?id=%d'>%s</a>" % (fork_owner.username, parent.id, parent.name))
    db_session.add(pr_activity)
    db_session.commit()
    return jsonify(success=True)

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
