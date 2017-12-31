import time
import os

from multiprocessing import Process
from somebox.server.server import main as server_main

from somebox.client.watcher import Watcher
from somebox.client.client import Client

def client(watch_folders):
    Watcher.EventHandlerClass = lambda *args: Client(watch_folders)
    w = Watcher(watch_folders)
    w.run()

def test_overall():
    try:
        os.makedirs('share')
    except:
        pass
    try:
        os.makedirs('testfolder/share')
    except:
        pass
    try:
        os.remove('share/abc')
    except:
        pass

    try:
        os.remove('testfolder/share/abc')
    except:
        pass

    try:
        os.removedirs('share/dir1/dir2')
    except:
        pass

    try:
        os.removedirs('testfolder/share/dir1/dir2')
    except:
        pass

    try:
        p = Process(target=server_main, args=({"share":"share"},))
        p.start()
        time.sleep(0.5)

        p1 = Process(target = client, args=({"share":"share"},))
        p1.start()

        p2 = Process(target = client, args=({"share":"testfolder/share"},))
        p2.start()

        time.sleep(1)
        open('share/abc','wb').write(b'hello')
        while not os.path.exists('testfolder/share/abc'):
            time.sleep(1)
        assert open('testfolder/share/abc','rb').read() == b'hello'

        time.sleep(1)

        msg = b'watermelon is delicious'
        open('testfolder/share/abc', 'wb').write(msg)
        time.sleep(1)
        assert open('share/abc','rb').read() == msg

        os.makedirs('share/dir1/dir2')
        time.sleep(1)
        assert os.path.exists('testfolder/share/dir1/dir2')

        os.rmdir('testfolder/share/dir1/dir2')
        time.sleep(1)
        assert not os.path.exists('share/dir1/dir2')
    finally:
        p.terminate()
        p1.terminate()
        p2.terminate()
