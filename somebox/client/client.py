import socket
import os
import json
import threading
import time

from ..common.transport import TransportDest, TransportSrc
from ..common.protocol import Protocol
from ..common import pathtool
from . import watcher

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 10101

def meta_to_key(meta):
    return (meta['base'], meta['rel'])

class Client(watcher.FileSystemEventHandler):
    def __init__(self, watch_folders, host = DEFAULT_HOST, port = DEFAULT_PORT):
        self.watch_folders = watch_folders
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.f = self.s.makefile('rwb')
        self.lock = threading.Lock()

        self.event_ignore_list = {}

        t = threading.Thread(target=self.run)
        t.start()

    def ignore_event_for(self, meta):
        print('ignore', meta['base'], meta['rel'], time.time())
        with self.lock:
            self.event_ignore_list[meta_to_key(meta)] = (True, time.time())
    def unignore_event_for(self, meta):
        print('unignore', meta['base'], meta['rel'], time.time())
        with self.lock:
            self.event_ignore_list[meta_to_key(meta)] = (False, time.time())

    def run(self):
        try:
            while True:
                name, body = Protocol.readfrom(self.f)
                print(name, len(body))
                if name == 'sc_sync':
                    meta = json.loads(body)
                    if meta['base'] not in self.watch_folders:
                        continue
                    base_path = self.watch_folders[meta['base']]
                    path = os.path.normpath(os.path.join(base_path, meta['rel']))
                    src_f = open(path, 'rb')
                    t = TransportSrc(src_f, self.f)
                    t.sync()

                    print('Sending file to server completed:', meta['base'], meta['rel'])

                elif name == 'add_file' or name == 'mod_file':
                    # new or update file data
                    # TODO conflict not implemented
                    meta = json.loads(body)
                    if meta['base'] not in self.watch_folders:
                        continue
                    base_path = self.watch_folders[meta['base']]
                    path = os.path.normpath(os.path.join(base_path, meta['rel']))
                    dest_f = open(path, 'wb')

                    Protocol.writeto('cs_sync', json.dumps(dict(base = meta['base'], rel = meta['rel'])), self.f)

                    self.ignore_event_for(meta)
                    t = TransportDest(self.f, dest_f)
                    t.sync()
                    self.unignore_event_for(meta)

                    print('Recving file from server completed:', meta['base'], meta['rel'], path)

                elif name == 'del_file':
                    meta = json.loads(body)
                    if meta['base'] not in self.watch_folders:
                        continue
                    base_path = self.watch_folders[meta['base']]
                    path = os.path.normpath(os.path.join(base_path, meta['rel']))
                    self.ignore_event_for(meta)
                    try:
                        os.remove(path)
                    except Exception as e:
                        print('del_file exception:', e)
                    self.unignore_event_for(meta)
                    print('Deleting file completed:', meta['base'], meta['rel'], path)
                elif name == 'add_dir':
                    meta = json.loads(body)
                    print('add_dir','C',meta)
                    if meta['base'] not in self.watch_folders:
                        continue
                    base_path = self.watch_folders[meta['base']]
                    path = os.path.normpath(os.path.join(base_path, meta['rel']))
                    print(base_path,path)
                    try:
                        os.makedirs(path)
                    except:
                        pass
                elif name == 'del_dir':
                    meta = json.loads(body)
                    if meta['base'] not in self.watch_folders:
                        continue
                    base_path = self.watch_folders[meta['base']]
                    path = os.path.normpath(os.path.join(base_path, meta['rel']))
                    try:
                        os.rmdir(path)
                    except:
                        pass
        except Exception as e:
            print(e)

        # scan + sync all ?

    def is_event_ignored(self, event):
        def helper(base, rel):
            with self.lock:
                if (base, rel) not in self.event_ignore_list:
                    return False
                v = self.event_ignore_list[(base,rel)]
                if v[0]:
                    print('ignored by v[0]')
                    return True
                # one second after lock
                if time.time() - v[1] < 1:
                    print('ignored by time', time.time())
                    return True
                return False

        base, rel = pathtool.find_base(event.src_path, self.watch_folders)
        if helper(base, rel):
            print('is_event_ignored', event, True)
            return True
        if hasattr(event, 'dest_path'):
            base, rel = pathtool.find_base(event.dest_path, self.watch_folders)
            if helper(base, rel):
                print('is_event_ignored', event, True)
                return True
        print('is_event_ignored', event, False)
        return False

    def on_created(self, event):
        super().on_created(event)
        if self.is_event_ignored(event):
            return
        print(event)
        base, rel = pathtool.find_base(event.src_path, self.watch_folders)
        if event.is_directory:
            name = 'add_dir'
        else:
            name = 'add_file'
        Protocol.writeto(
            name,
            json.dumps(
                dict(
                    base = base,
                    rel = rel,
                )),
            self.f)

    def on_deleted(self, event):
        super().on_deleted(event)
        if self.is_event_ignored(event):
            return
        print(event)
        base, rel = pathtool.find_base(event.src_path, self.watch_folders)
        if event.is_directory:
            name = 'del_dir'
        else:
            name = 'del_file'
        Protocol.writeto(
            name,
            json.dumps(
                dict(
                    base = base,
                    rel = rel,
                )),
            self.f)
    def on_modified(self, event):
        super().on_modified(event)
        if self.is_event_ignored(event):
            return
        print(event)
        base, rel = pathtool.find_base(event.src_path, self.watch_folders)
        if event.is_directory:
            # no packet for modified directory
            # change if needed
            return
        else:
            name = 'mod_file'
        Protocol.writeto(
            name,
            json.dumps(
                dict(
                    base = base,
                    rel = rel,
                )),
            self.f)
    def on_moved(self, event):
        super().on_moved(event)
        if self.is_event_ignored(event):
            return
        print(event)
        #event.is_directory, event.src_path, event.dest_path
        base_s, rel_s = pathtool.find_base(event.src_path, self.watch_folders)
        base_d, rel_d = pathtool.find_base(event.dest_path, self.watch_folders)
        # LATER!
        raise NotImplementedError("i am lazy")
