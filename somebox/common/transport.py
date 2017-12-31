# how file sending occurs:
# client want to upload a file to server
# C: file -> TransportSrc -> socket
# S: socket -> TransportDest -> file

INVALID_TRANSPORT = -1

class TransportSrc:
    def __init__(self, src, middle):
        self.src = src
        self.middle = middle

    def sync(self):
        if self.src is None:
            self.middle.write(b'%d\n' % INVALID_TRANSPORT)
            self.middle.flush()
            return
        self.src.seek(0, 2)
        sz = self.src.tell()
        self.src.seek(0)
        self.middle.write(b'%d\n' % sz)
        print(repr(b'%d\n'%sz))
        if sz > 0:
            self.middle.write(self.src.read(sz))
            self.src.seek(0)
            print(repr(self.src.read(sz)), self.src)
        self.middle.flush()

class TransportDest:
    def __init__(self, middle, dest):
        self.middle = middle
        self.dest = dest

    def sync(self):
        print('TransportDest sync')
        s = b''
        while 1:
            c = self.middle.read(1)
            s += c
            if c == b'\n':
                break
        sz = int(s.strip())
        #sz = int(self.middle.readline().strip())
        print('TransportDest', sz)
        if sz == INVALID_TRANSPORT:
            return
        elif sz > 0:
            self.dest.write(self.middle.read(sz))
            self.dest.flush()

