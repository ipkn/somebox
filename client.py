import settings
from somebox.client.watcher import Watcher
from somebox.client.client import Client

def main(watch_folders):
    Watcher.EventHandlerClass = lambda *args: Client(watch_folders)
    w = Watcher(watch_folders)
    w.run()

if __name__ == '__main__':
    main(settings.watch_folders)
