import os
import sys
from rdio import Rdio
import requests

RDIO_CONSUMER_KEY = 'c8pehjw6u8wdatpgxmq8jqkw'
RDIO_CONSUMER_SECRET = '9ADNaSuKSG'

commands = dict()
rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET))

def command(f):
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)
    commands[f.__name__] = wrapper
    return wrapper

def check_auth():
    config_path = os.path.join(os.path.expanduser('~'), '.pit')
    if os.path.exists(config_path):
        config = open(config_path, 'r')
        access_token = config.readlines()[-1].split('=')[-1]
    else:
        config = open(config_path, 'w')
        login_url = rdio.begin_authentication('oob')
        print 'Follow the following URL: '
        print login_url
        user_pin = raw_input('And enter the PIN here: ').strip()
        config.write('pin=%s' % user_pin)
        rdio.complete_authentication(user_pin)
        config.write('at=%s' % data_store['access_token'])
        config.close()
    print 'Authenticated!'

@command
def add(args):
    pass

@command
def rm(args):
    pass

@command
def status(args):
    pass

@command
def commit(args):
    pass

@command
def clone(args):
    pass

@command
def pull(args):
    pass

@command
def push(args):
    pass

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Valid commands are: %s' % ', '.join(commands.keys())
        sys.exit(1)
    args = sys.argv[1::]
    if args[0] in commands:
        check_auth()
        commands[args[0]](args[1::])
    else:
        print 'Valid commands are: %s' + commands.keys()
