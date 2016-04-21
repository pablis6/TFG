import sys
import os
import subprocess
from multiprocessing import Process, Pipe, Queue
import time
import logging
import linecache
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEvent
import download_chunks as dw

queue = Queue(2)
queue_timeout = 20
#f_path = 'docker/local_path/'
local_path = 'docker/local_path/'  # sobra para yalm ahora se lo generamos
log_path = 'my_log.log'
OAuth_token = 'rrFPgdcaJP8AAAAAAAAAHbe0eiQ3StEF2OGqWTp1DM90UeAXMEzMyZCBLlOezKbs'
OAuth_token_2 = ''
OAuth_token_3 = ''
min_value = 30
name_lis = 'listXyt'
#watch_path = 'docker/watchdog_listening/'
#local_path = 'docker/local_path/'  # local_path == f_path it is the work path ...

slash = '/'


def treat_txt_file(path_tfile):
    '''
    manages incoming text file from a terminal, if it's well formed creates a tuple otherwise returns false.
    :param path_tfile: str, path to the text file
    :return: tuple or False in case of error
    '''
    id_terminal = linecache.getline(path_tfile, 1).rstrip()  # removes '\n'
    t_op = linecache.getline(path_tfile, 2).rstrip()
    pin = linecache.getline(path_tfile, 3).rstrip()

    if t_op == 'charge':
        amount = linecache.getline(path_tfile, 4).rstrip()
        t_res = (id_terminal, t_op, pin, amount)
    elif t_op == 'register':
        usr_name = linecache.getline(path_tfile, 4).rstrip()
        t_res = (id_terminal, t_op, pin, usr_name)
        #  other data
    else:
        return False

    if t_res.count('') > 0 or len(t_res) == 0:
        return False
    else:
        return t_res


def treat_img(path_file):
    '''
    discover whether a directory for a img exists or not, if exists returns its name, False otherwise.
    :param path_file: str, dir name
    :return: work dir name or False
    '''
    dir_name = os.path.basename(path_file)
    dir_name = dir_name[:dir_name.index('.')]
    docker = 'docker/'  # docker/ sobra ya que estaran a la misma altura los .py
    if os.path.exists(docker+dir_name):
        return dir_name
    return False


def create_dir(t_res):
    '''
    creates directories for a single operation
    :param t_res: tuple
    :return: False in case of error or path for success
    '''
    # make dir with the format '<id-termial>-<pin>'
    dir_name = 'docker/{0}-{1}'.format(t_res[0], t_res[2])  # docker/ es temporal !!!! misma alt codigo
    local_cmp = '{0}/local_cmp/'.format(dir_name)
    try:
        os.mkdir(dir_name)  # create dir for terminal's request
        os.mkdir(local_cmp)  # create sub-dir
    except OSError:
        logging.error('directory already exist')
        return False
    else:
        return local_cmp


class MySLoggingEventHandler2(LoggingEventHandler):

    def on_created(self, event):
        print 'file has been created {0}'.format(event.src_path)
        file_format = event.src_path[event.src_path.rfind('.'):]  # finds the last point.

        if file_format == '.txt':
            p = Process(target=dw.download_tar, args=(local_path, queue, OAuth_token, name_lis,))  # download_chunks download_tar
            p.start()
            #print 'at the end should send a signal to start comparing'
        elif file_format == ('.png' or '.jpg'):
            p = Process(target=dw.extract_mindtct, args=(event.src_path, queue,))  #  falta un arg donde guardar
            p.start()
            #print 'done with the image'
        elif file_format == '.xyt':
            print "here"
            p = Process(target=dw.compare, args=(event.src_path, local_path, queue, queue_timeout, min_value,))
            p.start()
            #print 'send signal to compare... already got xyt'
        else:
            os.remove(event.src_path)
            #print 'remove the file, it s not useful '

    #def on_deleted(self, event):
        #print 'file has been deleted {0}'.format(event.src_path)


class MySLoggingEventHandler3(LoggingEventHandler):

    def on_created(self, event):
        print 'file has been created {0}'.format(event.src_path)
        file_format = event.src_path[event.src_path.rfind('.'):]  # finds the last point.

        if file_format == '.txt':
            # read data and return tuple or false
            t_res = treat_txt_file(event.src_path)
            # in case of success: charge or register
            if t_res and t_res[1] == 'charge':
                local_cmp = create_dir(t_res)
                if local_cmp:
                    p = Process(target=dw.download_tar, args=(local_cmp, queue, OAuth_token, name_lis,))  # download_chunks download_tar
                    p.start()
                    # hacer o no hacer join para que lo espere, afectara queue_timeout, con join no hace falta queue
                    #print 'at the end should send a signal to start comparing'
                    p = Process(target=dw.compare, args=(event.src_path, local_cmp, queue, queue_timeout, min_value,))
                    p.start()
            elif t_res and t_res[1] == 'register':
                print 'to do register'

            os.remove(event.src_path)  # always deletes .txt
        elif file_format == ('.png' or '.jpg'):
            dst_path = treat_img(event.src_path)
            if dst_path:  # the folder exist, proceed
                p = Process(target=dw.extract_mindtct, args=(event.src_path, queue, dst_path))  #  falta un arg donde guardar
                p.start()
            else:
                os.remove(event.src_path)
        else:
            os.remove(event.src_path)

if __name__ == "__main__":
    # logger
    logging.basicConfig(filename=log_path, format='%(asctime)s - %(levelname)s: (%(module)s) %(funcName)s - '
                                                        '%(message)s ', level=logging.ERROR)

    path = sys.argv[1] if len(sys.argv) > 1 else '/home/rnov/tfg/dropboxApi/docker/watchdog_listening'  # watchdog
    # listening path

    event_handler = MySLoggingEventHandler3()  # LoggingEventHandler()
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
