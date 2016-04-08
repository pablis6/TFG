import sys
import os
import subprocess
from multiprocessing import Process, Pipe, Queue
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEvent
import download_chunks as dw

queue = Queue(2)
queue_timeout = 20
#f_path = 'docker/local_path/'
local_path = 'docker/local_path/'
log_path = 'my_log.log'
#watch_path = 'docker/watchdog_listening/'
#local_path = 'docker/local_path/'  # local_path == f_path it is the work path ...


class MySLoggingEventHandler(LoggingEventHandler):

    def on_created(self, event):
        print 'file has been created {0}'.format(event.src_path)
        #p = Process(target=my_call)
        #fname = event.src_path
        p = Process(target=dw.download2, args=(event.src_path,))
        #path = event.src_path[event.src_path.find('watchdog'):]
        p.start()
        #p.join() # los procesos no son lanzados en paralelo sino uno depues de otro
        #print 'end...'

    def on_deleted(self, event):
        print 'file has been deleted {0}'.format(event.src_path)


class MySLoggingEventHandler2(LoggingEventHandler):

    def on_created(self, event):
        print 'file has been created {0}'.format(event.src_path)
        file_format = event.src_path[-4:]

        if file_format == '.txt':
            # read the pin code
            p = Process(target=dw.download_chunks, args=(local_path, queue,))
            p.start()
            #print 'at the end should send a signal to start comparing'
        elif file_format == ('.png' or '.jpg'):
            p = Process(target=dw.extract_mindtct, args=(event.src_path, queue,))
            p.start()
            #print 'done with the image'
        elif file_format == '.xyt':
            p = Process(target=dw.compare, args=(event.src_path, local_path, queue, queue_timeout,))
            p.start()
            #print 'send signal to compare... already got xyt'
        else:
            os.remove(event.src_path)
            #print 'remove the file, it s not useful '

    #def on_deleted(self, event):
        #print 'file has been deleted {0}'.format(event.src_path)


if __name__ == "__main__":
    # logger
    logging.basicConfig(filename=log_path, format='%(asctime)s - %(levelname)s: (%(module)s) %(funcName)s - '
                                                        '%(message)s ', level=logging.ERROR)

    path = sys.argv[1] if len(sys.argv) > 1 else '/home/rnov/tfg/dropboxApi/docker/watchdog_listening'  # watchdog
    # listening path

    event_handler = MySLoggingEventHandler2()  # LoggingEventHandler()
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










    #logging.basicConfig(level=logging.INFO,
    #                    format='%(asctime)s - %(message)s',
    #                    datefmt='%Y-%m-%d %H:%M:%S')
