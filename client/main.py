import time
import os
import settings

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class EventHandler(FileSystemEventHandler):
    def on_created(self, event):
        super().on_created(event)
        print('+', event)
    def on_deleted(self, event):
        super().on_deleted(event)
        print('-', event)
    def on_modified(self, event):
        super().on_modified(event)
        print('*', event)
    def on_moved(self, event):
        super().on_moved(event)
        print('M', event)

def main(watch_folders, EventHandlerClass = EventHandler, is_done = lambda : False):
    print(EventHandlerClass)
    event_handler = EventHandlerClass()
    observer = Observer()
    for path in watch_folders:
        print(path)
        observer.schedule(event_handler, path, recursive = True)
    observer.start()

    try:
        while not is_done():
            time.sleep(0.1)
        observer.stop()
    except KeyboardInterrupt:
        observer.stop()

if __name__ == '__main__':
    main(settings.watch_folders)
