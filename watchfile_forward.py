import sys
import os
import logging
import time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

watchdog_forwarding = 'watchdog_forwarding'
listening_path = '{0}/{1}'


class MySLoggingEventHandler_1(LoggingEventHandler):

    def on_created(self, event):
        print 'file has been created {0}'.format(event.src_path)
        file_format = event.src_path[event.src_path.rfind('.'):]  # finds the last point.
        if file_format == '.txt':
            # connect via ssh to openshift DB
            with open(event.src_path, 'r') as f:
                print f.read()
                f.close()

            os.remove(event.src_path)  # always delete .txt

        else:  # other files, formats
            os.remove(event.src_path)


if __name__ == "__main__":


    # '/home/rnov/tfg/dropboxApi/work_unit/watchdog_forwarding'
    path = sys.argv[1] if len(sys.argv) > 1 else listening_path.format(os.getcwd(), watchdog_forwarding)  # watchdog
    # listening path

    event_handler = MySLoggingEventHandler_1()  # LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()