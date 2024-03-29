import os, subprocess, shutil, re, fileinput

class Git():
    _root = os.getcwd()
    _fileName = 'playlist.txt'
    _dirName = 'playlists/'
    _playlistId = ''
    _playlistDir = ''
    def __init__(self, playlistId):
        self._playlistId = playlistId
        self._playlistDir = os.path.join(self._root, self._dirName, str(self._playlistId))

        if not os.path.exists(self._playlistDir):
            self._createRepo()

    def filePath(self):
        return os.path.join(self._root, self._dirName, str(self._playlistId), self._fileName)

    def writeTrackKeys(self, track_keys):
        with open(self.filePath(), 'w') as f:
            for track_key in track_keys:
                f.write(track_key)
                f.write('\n')

    def getTrackIds(self):
        with open(self.filePath(), 'r') as f:
            tracks = [track.rstrip() for track in f.readlines()]
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

    def update(self, songs):
        os.chdir(self._playlistDir)
        with open(self._fileName, 'wb') as f:
            for song in songs:
                f.write(song + '\n')

    #just copy the directory?
    def fork(self, playlistId):
        newDir = os.path.join(self._root, self._dirName, str(playlistId))
        print newDir
        if not os.path.exists(newDir):
            subprocess.call('cp -r ' + self._playlistDir + '/. ' + newDir, shell=True)
        return Git(playlistId)

    #pull in remote branch and then merge that branch into master.
    def merge(self, remote, parent_playlist, fork_playlist):
        os.chdir(self._playlistDir)
        subprocess.call('git fetch ' + os.path.join(self._root, self._dirName, remote) + ' master:' + remote + '/master', shell=True)
        subprocess.call('git reset --hard ' + remote + '/master', shell=True)
        self.commit("Pull request accepted from %s to %s" % (fork_playlist, parent_playlist))
        subprocess.call('git branch -D ' + remote + '/master', shell=True)

    def diff(self, remote):
        os.chdir(self._playlistDir)
        newDir = os.path.join(self._root, self._dirName, remote)
        subprocess.call('git fetch ' + newDir + ' master:' + remote + '/master', shell=True)
        diffOutput = subprocess.check_output('git diff ' + remote + '/master..master', shell=True)

        gotToDiffLines = False
        changes = []
        for line in diffOutput.split('\n'):
            if re.search(r'^@@', line):
                gotToDiffLines = True
            if gotToDiffLines:
                if len(line) > 0 and (line[0] == '-' or line[0] == '+'):
                    changes.append([line[0], line[1:]])

        subprocess.call('git branch -D ' + remote + '/master', shell=True)
        return changes

    def delete(self):
        shutil.rmtree(self._playlistDir)

    def getPlaylistId(self):
        return self.playlistId

    def log(self):
        os.chdir(self._playlistDir)
        logOutput = subprocess.check_output('git log --pretty=format:"%s"', shell=True)

        return logOutput.split('\n')
