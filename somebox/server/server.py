import socketserver
import json
import io
import collections
import threading

from ..common.protocol import Protocol
from ..common.transport import TransportDest, TransportSrc

clients = {}

def broadcast(func, ignore = None):
    for p, f in clients.items():
        if p != ignore:
            func(f)

files_lock = threading.Lock()
files = {}
dirs = collections.defaultdict(dict)

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

def meta_to_key(meta):
    return (meta['base'], meta['rel'])

class Handler(socketserver.BaseRequestHandler):
    watch_folders = {}
    def start_cs_sync(self, meta):
        print('start_cs_sync', meta)
        with files_lock:
            k = meta_to_key(meta)
            if k not in files:
                src_file = None
            else:
                src_file = files[k]
        print('src_file:',src_file)
        t = TransportSrc(src_file, self.f)
        t.sync()

        print('file synced from S to C:',k)

    def start_sc_sync(self, meta):
        print('start_sc_sync', meta)
        sync_info = dict(base = meta['base'], rel=meta['rel'])
        Protocol.writeto('sc_sync', json.dumps(sync_info), self.f)
        dest_target_file = io.BytesIO()
        print('send sc_sync', meta)

        t = TransportDest(self.f, dest_target_file)
        t.sync()

        print('sc_sync transport complete', meta)

        with files_lock:
            files[meta_to_key(meta)] = dest_target_file

        print('file synced from C to S:',meta_to_key(meta))

    def handle(self):
        s = self.request
        p = s.getpeername()
        print('Connection from:', p)

        self.f = s.makefile('rwb')
        clients[p] = self.f
        try:
            while True:
                name, body = Protocol.readfrom(self.f)
                print('Recved:', name, body)
                if name == 'add_file' or name == 'mod_file':
                    # request the client to send content of the file
                    meta = json.loads(body)
                    if meta['base'] not in self.watch_folders:
                        break
                    self.start_sc_sync(meta)
                    def send_add_or_mod_file(f):
                        Protocol.writeto(name, body, f)
                    broadcast(send_add_or_mod_file, ignore=p)
                elif name == 'del_file':
                    meta = json.loads(body)
                    if meta['base'] not in self.watch_folders:
                        break
                    with files_lock:
                        k = meta_to_key(meta)
                        if k not in files:
                            print('E:Try to delete non exist file:', meta)
                            break
                        del files[k] 
                    def send_del_file(f):
                        Protocol.writeto(name, body, f)
                    broadcast(send_del_file, ignore=p)
                elif name == 'add_dir':
                    meta = json.loads(body)
                    if meta['base'] not in self.watch_folders:
                        continue
                    with files_lock:
                        if meta['rel'] in dirs[meta['base']]:
                            continue
                        dirs[meta['base']][meta['rel']] = 1
                    def send_add_dir(f):
                        Protocol.writeto(name, body, f)
                    broadcast(send_add_dir, ignore=p)
                elif name == 'del_dir':
                    meta = json.loads(body)
                    if meta['base'] not in self.watch_folders:
                        continue
                    with files_lock:
                        if meta['rel'] not in dirs[meta['base']]:
                            continue
                        del dirs[meta['base']][meta['rel']]
                    def send_del_dir(f):
                        Protocol.writeto(name, body, f)
                    broadcast(send_del_dir, ignore=p)
                elif name == 'cs_sync':
                    meta = json.loads(body)
                    self.start_cs_sync(meta)
        except Exception as e:
            print(e)
        print('Connection closed:', p)
        del clients[p]

HOST, PORT = 'localhost', 10101
def main(watch_folders, host = HOST, port = PORT):
    print('Serving somebox at %s:%d ...' % (host, port))
    Handler.watch_folders = watch_folders
    server = ThreadingTCPServer((host, port), Handler)

    server.serve_forever()

if __name__ == '__main__':
    main({"share":"share"})
