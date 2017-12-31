import hashlib

class Protocol:
    PACKET_ID_MOD = 256
    packets = {}

    @staticmethod
    def packet_hash(x):
        h = hashlib.sha256()
        h.update(x.encode('utf8'))
        return h.digest()

    def __init__(self, h, name):
        self.h = h
        self.name = name

    @classmethod 
    def writeto(cls, name, body, file):
        assert cls.has(name)
        print('write', name, body)
        if isinstance(body, str):
            body = body.encode('utf8')
        file.write(b'%d %d\n' % (cls.name_to_id(name), len(body)))
        file.write(body)
        file.flush()

    @classmethod
    def readfrom(cls, f):
        line = f.readline()
        assert line, "Read fail: connection closed?"
        packet_id, size = map(int, line.split())
        body = f.read(size)
        return cls.packets[packet_id].name, body

    @classmethod
    def name_to_id(cls, name):
        v = 0
        for c in cls.packet_hash(name):
            v = (v * 256 + c) % cls.PACKET_ID_MOD
        return v
    
    @classmethod
    def has(cls, name):
        return cls.name_to_id(name) in cls.packets

    @classmethod
    def register(cls, name):
        h = cls.name_to_id(name)
        assert h not in cls.packets, "Packet ID duplicated !!!"
        p = Protocol(h, name)
        cls.packets[h] = Protocol(h, name)

Protocol.register("add_file")
Protocol.register("add_dir")
Protocol.register("mod_file")
Protocol.register("del_file")
Protocol.register("del_dir")
Protocol.register("mov_file")
Protocol.register("mov_dir")
Protocol.register("cs_sync")
Protocol.register("sc_sync")
Protocol.register("conflict") # How to version control?
