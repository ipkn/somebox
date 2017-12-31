
class Protocol:
    PACKET_ID_MOD = 256
    packets = {}

    def __init__(self, h, name):
        self.h = h
        self.name = name

    @classmethod 
    def writeto(cls, name, body, file):
        print(cls.name_to_id(s), len(body), file = file)
        file.write(body)

    @classmethod
    def readfrom(cls, s):
        line = s.readline()
        packet_id, size = map(int, line.split())
        body = s.readall(size)
        return cls.packets[packet_id].name, body

    @classmethod
    def name_to_id(cls, name):
        return hash(name) % cls.PACKET_ID_MOD
    
    @classmethod
    def has(cls, name):
        return cls.name_to_id(name) in cls.packets

    @classmethod
    def register(cls, name):
        h = cls.name_to_id(name)
        assert h not in cls.packets, "Packet ID duplicated !!!"
        p = Protocol(h, name)
        cls.packets[h] = [Protocol(h, name)]

Protocol.register("add_file")
Protocol.register("add_dir")
Protocol.register("mod_file")
Protocol.register("del_file")
Protocol.register("del_dir")
Protocol.register("mov_file")
Protocol.register("mov_dir")
