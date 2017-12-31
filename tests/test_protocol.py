import pytest
import io

from somebox.common.protocol import Protocol

def test_basic():
    assert Protocol.has('add_file')

def test_read_write():
    f = io.BytesIO()
    Protocol.writeto('add_file', 'hi', f)
    f.seek(0)
    a, b = Protocol.readfrom(f)
    assert a == 'add_file'
    assert b == b'hi'

    f = io.BytesIO()
    with pytest.raises(AssertionError):
        Protocol.writeto('wrong', 'hi', f)
