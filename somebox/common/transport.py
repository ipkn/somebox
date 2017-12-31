class Transport:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def sync(self):
        self.dst.write(self.src.read())

