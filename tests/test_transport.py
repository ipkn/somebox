import os
import io
from somebox.common.transport import TransportSrc, TransportDest

def test_basic_sync_if_open():
    open('a','wb').write(b'dummy data')

    with open('a', 'rb') as src, open('b', 'wb') as dest:
        middle = io.BytesIO()
        t1 = TransportSrc(src, middle)
        t1.sync()

        middle.seek(0)
        t2 = TransportDest(middle, dest)
        t2.sync()

    assert open('b', 'rb').read() == b'dummy data'
    os.remove('a')
    os.remove('b')


