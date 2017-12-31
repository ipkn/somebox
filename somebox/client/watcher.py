import time

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

class Watcher:
    EventHandlerClass = EventHandler
    def __init__(self, watch_folders):
        self.event_handler = self.EventHandlerClass()
        self.observer = Observer()
        self.done = False

        self.watch_folders = watch_folders

        for name, path in watch_folders.items():
            print('watching', path, '(%s)' % name)
            self.observer.schedule(self.event_handler, path, recursive = True)

    def set_done(self):
        self.done = True

    def is_done(self):
        return self.done

    def run(self):
        observer = self.observer
        observer.start()

        try:
            while not self.is_done():
                time.sleep(0.1)
            observer.stop()
        except KeyboardInterrupt:
            observer.stop()
