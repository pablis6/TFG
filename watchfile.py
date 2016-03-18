import sys
import subprocess
from multiprocessing import Process
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


def myCall():
    subprocess.call(['python2', '/home/rnov/tfg/dropboxApi/myScript.py'])


class MySLoggingEventHandler(LoggingEventHandler):

    def on_created(self, event):
        print 'file has been created {0}'.format(event.src_path)
        p = Process(target=myCall)
        p.start()
        #p.join() # los procesos no son lanzados en paralelo sino uno depues de otro
        print 'end...'

    def on_deleted(self, event):
        print 'file has been deleted {0}'.format(event.src_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '/home/rnov/tfg/dropboxApi/watchdog'

    event_handler = MySLoggingEventHandler()  # LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# about 12 MB of memory