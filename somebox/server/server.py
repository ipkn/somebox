import socketserver

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass
class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        s = self.request
        print('Connection from:', s.getpeername())
        f = s.makefile('rwb')
        line = f.readline() # <- good
        print('Recved:', line)


if __name__ == '__main__':
    HOST, PORT = 'localhost', 10101
    print('Serving somebox at %s:%d ...' % (HOST, PORT))
    server = ThreadingTCPServer((HOST, PORT), Handler)

    server.serve_forever()
