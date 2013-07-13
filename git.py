import os, subprocess, shutil

class Git():
    _root = '/home/patrick/code/playgit/'
    _fileName = 'playlist.txt'
    _dirName = 'playlists/'
    _playlistId = ''
    _playlistDir = ''
    def __init__(self, playlistId):
        self._playlistId = playlistId
        self._playlistDir = self._root + self._dirName + self._playlistId + '/'

        if not os.path.exists(self._playlistDir):
            self._createRepo()

    def getTrackIds(self):
        tracks = []
        with open(self._fileName, 'r') as f:
            trackId = f.read()
            if trackId != '':
                tracks.append(f.read());
        return tracks

    def _createRepo(self):

        #create the directory for the repo for the playlist
        os.makedirs(self._playlistDir)
        os.chdir(self._playlistDir)

        #create the file that holds the song ids for the playlist
        playlistFile = open(self._fileName, 'w')
        playlistFile.close()

        #set up get and add playlist file
        subprocess.call('git init', shell=True)
        subprocess.call('git add ' + self._fileName, shell=True)

        self.commit('Initial commit.')
        
    #just commit it with timestamp as commit message.
    def commit(self, message):
        os.chdir(self._playlistDir)
        subprocess.call('git commit -am "' + message + '"', shell=True)
        pass

    def add(self, id, index=None):
        if index:
            pass
        else:
            os.chdir(self._playlistDir)
            playlistFile = open(self._fileName, 'a')
            playlistFile.write(id + '\n')
            playlistFile.close()

    def remove(self, id):
        pass

    #just copy the directory?
    def fork(self, playlistId):
        newDir = self._root + self._dirName + playlistId
        if not os.path.exists(newDir):
            subprocess.call('cp -r ' + self._playlistDir + '/. ' + newDir, shell=True)
        return Git(playlistId)

    #pull in remote branch and then merge that branch into master.
    def merge(self, remote):
        os.chdir(self._playlistDir)
        subprocess.call('git pull ' + self._root + self._dirName + remote + ' master', shell=True)
        pass

    def diff(self):
        pass

    def delete(self):
        shutil.rmtree(self._playlistDir)

    def getPlaylistId(self):
        return self.playlistId

git = Git("shithappens")
anotherGit = git.fork("anothershit")

anotherGit.add("omg a song")
anotherGit.commit("Added a song")

git.merge("anothershit")