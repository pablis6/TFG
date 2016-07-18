import sys
import os
import logging
import time
import pysftp
#sys.path.remove('/usr/lib/python2.7/site-packages')  # para test, probar dependencias
custom_path = '{0}/{1}'
sys.path.insert(1, custom_path.format(os.getcwd(), 'depen_packages'))
sys.path.insert(1, custom_path.format(os.getcwd(), 'payfi'))
#print sys.path  # probar dependencias, para tests
import yaml
from payfi.watchdog.observers import Observer
from payfi.watchdog.observers import Observer
from payfi.watchdog.events import LoggingEventHandler


filename = 'forwarding_listener_config.yalm'
log_path = 'my_log.log'


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


class MySLoggingEventHandler1(LoggingEventHandler):

    def on_created(self, event):
        print 'file has been created {0}'.format(event.src_path)
        file_format = event.src_path[event.src_path.rfind('.'):]  # finds the last point.
        if file_format in file_ext:
            with pysftp.Connection(db_conn, username=db_user, private_key=db_auth) as sftp:
                with sftp.cd(db_dir):  # change remote directory
                    sftp.put(event.src_path)  # upload file

        os.remove(event.src_path)


if __name__ == "__main__":

    # init the logger
    logging.basicConfig(filename=log_path, format='%(asctime)s - %(levelname)s: (%(module)s) %(funcName)s - '
                                                        '%(message)s ', level=logging.ERROR)  # logging.WARNING

    # load config file, in case of error close the program and register the error
    try:
        __load_config_file(filename)
        print 'watchdog_forwarding has been initialized'
        #print globals()  # just for tests
    except IOError:
        logging.error('Could not read config file')
        raise SystemExit

    path = sys.argv[1] if len(sys.argv) > 1 else watchdog_forwarding

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
