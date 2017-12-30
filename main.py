import settings
from somebox.client.watcher import Watcher

def main(watch_folders):
    w = Watcher(watch_folders)
    w.run()

if __name__ == '__main__':
    main(settings.watch_folders)
