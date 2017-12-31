import os
from somebox.common.transport import Transport

def test_basic_sync_if_open():
    open('a','wb').write(b'dummy data')

    with open('a', 'rb') as src, open('b', 'wb') as dst:
        t = Transport(src, dst)
        t.sync()

    assert open('b', 'rb').read() == b'dummy data'
    os.remove('a')
    os.remove('b')


