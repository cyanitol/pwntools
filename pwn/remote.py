import pwn, socket, basesock, errno
from pwn import log

_DEFAULT_REMOTE_TIMEOUT = 10

class remote(basesock.basesock):
    def __init__(self, host, port = 1337, fam = None, typ = socket.SOCK_STREAM, proto = 0, **kwargs):
        port = int(port)
        self.target = (host, port)
        if fam is None:
            if host.find(':') != -1:
                self.family = socket.AF_INET6
            else:
                self.family = socket.AF_INET
        self.type = typ
        self.proto = proto
        self.sock = None
        self.debug = pwn.DEBUG
        self.timeout = kwargs.get('timeout', _DEFAULT_REMOTE_TIMEOUT)
        self.checked = kwargs.get('checked', True)
        self.lhost = None
        self.lport = None
        self.connect()

    def connect(self):
        if self.connected():
            log.warning('Already connected to %s on port %d' % self.target)
            return
        log.waitfor('Opening connection to %s on port %d' % self.target)
        self.sock = socket.socket(self.family, self.type, self.proto)
        if self.timeout is not None:
            self.sock.settimeout(self.timeout)
        if self.checked:
            try:
                self.sock.connect(self.target)
            except socket.error, e:
                if   e.errno == errno.ECONNREFUSED:
                    pwn.die('Refused', exit_code = pwn.PWN_UNAVAILABLE)
                elif e.errno == errno.ENETUNREACH:
                    pwn.die('Unreachable', exit_code = pwn.PWN_UNAVAILABLE)
                else:
                    raise
            except socket.timeout:
                pwn.die('Timed out', exit_code = pwn.PWN_UNAVAILABLE)
        else:
            self.sock.connect(self.target)
        self.lhost = self.sock.getsockname()[0]
        self.lport = self.sock.getsockname()[1]
        log.succeeded()

    def close(self):
        self.lhost = None
        self.lport = None
        basesock.basesock.close(self)
