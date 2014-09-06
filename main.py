import tornado.ioloop
import tornado.web
import os
from stat import *
import subprocess
import logging
import collections
from tornado.options import options, define, parse_command_line, parse_config_file
import base64
import hashlib


def get_finger_print(line):
    key = base64.b64decode(line.strip().split()[1].encode('ascii'))
    fp_plain = hashlib.md5(key).hexdigest()
    return ':'.join(a+b for a,b in zip(fp_plain[::2], fp_plain[1::2]))


class KeyManager(object):
    def __init__(self, ssh_file_path):
        self.ssh_file_path = ssh_file_path
        self.sshcommand = '/home/dokku/.sshcommand'

    def add_key(self, user, key):
        finger_print = get_finger_print(key)
        logging.info(finger_print)
        commands = [
'FINGERPRINT={}'.format(finger_print),
'NAME={}'.format(user),
'`cat {}`'.format(self.sshcommand),
'$SSH_ORIGINAL_COMMAND'
        ]
        opts = [
'command="{}"'.format(' '.join(commands)),
'no-agent-forwarding',
'no-user-rc',
'no-X11-forwarding',
'no-port-forwarding'
        ]
        data = '{0} {1}\n'.format(','.join(opts), key)
        with open(self.ssh_file_path, 'a') as fp:
            return fp.write(data)

    def get_key(self, user=None):
        file_path = self.ssh_file_path
        logging.info(file_path)
        with open(file_path, 'r') as fp:
            return fp.read()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(os.path.join('templates', 'index.html'))


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.mgr = KeyManager(options.ssh_file_path)


class KeyHandler(BaseHandler):
    def get(self):
        try:
            res = self.mgr.get_key()
            self.write(res.replace('\n', '<br>'))
        except Exception as e:
            logging.error('error = {0}'.format(e))
            self.send_error(500)


class RegisterHandler(BaseHandler):
    def post(self):
        user = self.get_argument('user')
        key = self.get_argument('key')
        logging.info('user = {0}'.format(user))
        logging.info('key = {0}'.format(key))
        try:
            res = self.mgr.add_key(user, key)
            self.redirect('/keys')
        except Exception as e:
            logging.error('error = {0}'.format(e))
            self.send_error(500)


def setup_options():
    define('debug', type=bool, default=False, help='debug')
    define('listen_port', type=int, default=5000, help='listen_port')
    define('ssh_file_path', type=str, default='/home/dokku/.ssh/authorized_keys', help='ssh_file_path')
    if 'debug' in options and options.debug:
        logging.info('auto reloading mode')
    logging.info('listen port=%d' % options.listen_port)
    logging.info('ssh file path=%s' % options.ssh_file_path)

    try:
        parse_command_line()
    except Exception as e:
        logging.error(e)


def create_ssh_dir(ssh_file_path):
    ssh_dir = os.path.dirname(ssh_file_path)
    if not (os.path.exists(ssh_dir) and os.path.isdir(ssh_dir)):
        os.makedirs(ssh_dir)
        os.chmod(ssh_dir, S_IRUSR | S_IWUSR | S_IXUSR)


def main():
    setup_options()
    create_ssh_dir(options.ssh_file_path)
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/keys", KeyHandler),
        (r"/register", RegisterHandler),
    ], debug=options.debug)
    application.listen(options.listen_port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
