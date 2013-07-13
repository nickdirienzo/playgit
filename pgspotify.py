import os
import getpass
import spotify
from spotify.manager import SpotifySessionManager
from multiprocessing import Process

class SpotifyManager(object):
    def __init__(self):
        # Fuck yeah, multiprocess bullshit
        self.connections = dict() # username: pid
        

class PGSpotifySessionManager(SpotifySessionManager):
    appkey_file = os.path.join(os.path.dirname(__file__), 'spotify_appkey.key')
    def __init__(self, *args, **kwargs):
        SpotifySessionManager.__init__(self, *args, **kwargs)
        self.sm = SpotifyManager()
        print 'New session manager...'

    def logged_in(self, session, error):
        if error:
            return error
        print 'Logged in.'
        if not self.sm.is_alive():
            self.sm.start()

    def logged_out(self, session):
        print 'Logged out.'

    def credentials_blob_updated(self, session, blob):
        self.connections[session.username()] = (session, blob)

def main():
    u = raw_input("user: ")
    p = getpass.getpass("pass: ")
    pgsm = PGSpotifySessionManager(u, p, True)
    pgsm.connect()

if __name__ == '__main__':
    main()
