import sys
import os
import os.path
import logging
import linecache
import time
#sys.path.remove('/usr/lib/python2.7/site-packages')  # para test, probar dependencias
custom_path = '{0}/{1}'
sys.path.insert(1, custom_path.format(os.getcwd(), 'depen_packages'))
sys.path.insert(1, custom_path.format(os.getcwd(), 'payfi'))
#print sys.path
import yaml
from payfi import download_chunks as dw
from payfi.watchdog.observers import Observer
from payfi.watchdog.observers import Observer
from payfi.watchdog.events import LoggingEventHandler

filename = 'db_listener_config.yalm'
log_path = 'db_log.log'


def __load_config_file(file_name):
    """

    :param filename:
    :return:
    """
    with open(file_name) as f:
        data_map = yaml.safe_load(f)
        f.close()
    globals().update(data_map)
    globals()['file_ext'] = tuple(globals()['file_ext'])
    globals()['register'] = tuple(globals()['register'])
    globals()['charge'] = tuple(globals()['charge'])
    globals()['success'] = tuple(globals()['success'])
    globals()['fail'] = tuple(globals()['fail'])


class MySLoggingEventHandler1(LoggingEventHandler):

    def on_created(self, event):
        print 'file has been created {0}'.format(event.src_path)
        file_format = event.src_path[event.src_path.rfind('.'):]  # finds the last point.
        if file_format in file_ext:

            t_op = linecache.getline(event.src_path, 1).rstrip()  # removes '\n' 0 operation type
            res = linecache.getline(event.src_path, 2).rstrip()  # operation result success/fail
            id_ter = linecache.getline(event.src_path, 3).rstrip()  # terminal id
            print res
        # IMPORTANT: clear the cache, otherwise will read always the same values that come from an individual terminal
            linecache.clearcache()

            if t_op in register and res in fail:  #'FAILURE':
                print 'delete inserted fingerprint needed pin and img_filename.. to do'

            # sends to the terminal's folder
            try:
                destiny_path = id_ter + file_format
                # in case terminal_id folder does not exist, create it
                dir_name = os.path.dirname(forward_path.format(id_ter, destiny_path))  # get destiny folder id
                if not os.path.exists(dir_name):  # in case does not exist, create it
                    os.mkdir(dir_name)  # 0o777

                epoch = str(time.time())
                dw.prepare_client_file(forward_path.format(id_ter, destiny_path), (epoch[:epoch.index('.')], res))
            except OSError:
                logging.error('destiny path is a directory, not a file')

        os.remove(event.src_path)  # remove always everything


if __name__ == "__main__":

    # init the logger
    logging.basicConfig(filename=log_path, format='%(asctime)s - %(levelname)s: (%(module)s) %(funcName)s - '
                                                        '%(message)s ', level=logging.ERROR)  # logging.WARNING

    # load config file, in case of error close the program and register the error
    try:
        __load_config_file(filename)
        print 'watchdog_db has been initialized'
        #print globals()  # just for tests
    except IOError:
        logging.error('Could not read config file')
        raise SystemExit

    path = sys.argv[1] if len(sys.argv) > 1 else db_listening_path  # watchdog

    event_handler = MySLoggingEventHandler1()  # LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
