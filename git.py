class Git():
    filename = "test.txt"
    def __init__(playlist_id=0):
        if (playlist_id > 0):
            pass
        else:
            pass

    def getTrackIds():
        with open(filename, 'r') as f:
            print f.read()

git = new Git()
git.getTrackIds()