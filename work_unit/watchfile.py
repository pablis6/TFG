import sys
import os
from multiprocessing import Process, Queue
import time
import logging
import linecache
# installed and customized packages
custom_path = '{0}/{1}'
#sys.path.remove('/usr/lib/python2.7/site-packages')  # para test, probar dependencias
sys.path.insert(1, custom_path.format(os.getcwd(), 'depen_packages'))  # dependency packages
sys.path.insert(1, custom_path.format(os.getcwd(), 'payfi'))  # payfi packages with own dependence inside
#print sys.path  # paths for modules and packages, just for test
import yaml
from payfi import download_chunks as dw
from payfi.watchdog.observers import Observer
from payfi.watchdog.events import LoggingEventHandler

filename = 'app_config.yalm'
log_path = 'my_log.log'

dict_q = {}
slash = '/'


def __load_config_file(file_name):
    """
    Loads varibles and constants from yalm config file and turns them into module's global variables, it also load some in
    download_chunks module.
    :param filename: str, config file name
    :return: None
    """
    with open(file_name) as f:
        data_map = yaml.safe_load(f)
        f.close()
    globals().update(data_map)
    globals()['tuple_OAuth_tokens'] = tuple(globals()['tuple_OAuth_tokens'])
    globals()['img_ext'] = tuple(globals()['img_ext'])
    globals()['file_ext'] = tuple(globals()['file_ext'])
    globals()['file_suffixes'] = tuple(globals()['file_suffixes'])
    globals()['register'] = tuple(globals()['register'])
    globals()['charge'] = tuple(globals()['charge'])

    dw.update_globals(data_map)
    #dw.print_globals()  # just for tests


def treat_txt_file(path_tfile):
    '''
    manages incoming text file from a terminal, if it's well formed creates a dict otherwise returns false.
    :param path_tfile: str, path to the text file
    :return: tuple or False in case of error
    '''
    id_terminal = linecache.getline(path_tfile, 1).rstrip()  # removes '\n'
    t_op = linecache.getline(path_tfile, 2).rstrip()
    pin = linecache.getline(path_tfile, 3).rstrip()

    if t_op in charge:
        amount = linecache.getline(path_tfile, 4).rstrip()
        t_res = {'ter_id': id_terminal, 'operation': t_op, 'pin': pin, 'amount': amount}
    elif t_op in register:
        usr_name = linecache.getline(path_tfile, 4).rstrip()
        surname = linecache.getline(path_tfile, 5).rstrip()
        family = linecache.getline(path_tfile, 6).rstrip()
        id_usr = linecache.getline(path_tfile, 7).rstrip()
        mail = linecache.getline(path_tfile, 8).rstrip()
        phone = linecache.getline(path_tfile, 9).rstrip()
        t_res = {'ter_id': id_terminal, 'operation': t_op, 'pin': pin, 'name': usr_name,
                 'surname': surname, 'family': family, 'usr_id': id_usr, 'mail': mail, 'phone': phone}
    else:
        linecache.clearcache()
        return False

    # IMPORTANT: clear the cache, otherwise will read always the same values that come from an individual terminal
    linecache.clearcache()

    if len(t_res) not in (4, 9):  # if the values in t_res are not enough for charge/registration operation
        return False
    else:
        print t_res
        return t_res


def treat_img(path_file):
    '''
    discovers whether a directory exists or not (used for incoming images), if exists returns its name, False otherwise.
    :param path_file: str, dir name
    :return: work dir name or False
    '''
    dir_name = os.path.basename(path_file)
    dir_name = dir_name[:dir_name.index('.')]
    if os.path.exists(dir_name):
        return dir_name

    # logging.warning('orphan image ') # warning an image has arrived but there isn't an folder, reason timeout or error
    return False


def create_dir(ter_id):
    """
    creates directories for a single operation.
    :param ter_id: ter_id
    :return: False in case of error or path for success
    """
    # make dir with the format '<id-termial>'
    dir_name = '{0}'.format(ter_id)  # -{1} , ter_id[2]
    local_cmp = '{0}/local_cmp/'.format(dir_name)
    try:
        os.mkdir(dir_name)  # create dir for terminal's request, raise error if exists
        os.mkdir(local_cmp)  # create sub-dir
    except OSError:
        logging.error('directory already exist')
        return False
    else:
        return dir_name, local_cmp


def form_dropbox_path(pin):
    """
    forms a list with the folder's names in dropbox, (ord list 1,2,3..)
    :param pin: int required to form the folder's name
    :return: lst list with names
    """
    paths = []
    for index, value in enumerate(range(1, 4)):
        paths.append((dropbox_paths_format.format(pin, value), tuple_OAuth_tokens[index]))
    #print paths
    return paths


class MySLoggingEventHandler(LoggingEventHandler):

    def on_created(self, event):
        print 'file has been created {0} {1}'.format(event.src_path, id(event.src_path))  # TEST...
        file_format = event.src_path[event.src_path.rfind('.'):]  # finds the last point.

        if file_format in file_ext:
            # read data and return dict or false, in case of success: operation charge or register
            t_res = treat_txt_file(event.src_path)

            if t_res:  # success at loading the file

                queue = Queue(2)  # register a queue object (a queue per job)
                paths = create_dir(t_res['ter_id'])  # dir_name -> <id_terminal> , paths -> (dir_name, local_cmp)

                if paths:  # success creating workspace directories

                    dict_q[paths[0]] = queue  # saves queue dir to dir with dir name as key
                    dropbox_paths = form_dropbox_path(t_res['pin'])  # form the remote consulting path

                    if t_res['operation'] in charge:
                        p = Process(target=dw.download_tar, args=(paths[1], dropbox_paths, queue,))
                        p.start()

                        p = Process(target=dw.compare, args=(paths, t_res, queue,))
                        p.start()

                    elif t_res['operation'] in register:
                        p = Process(target=dw.download_tar_up, args=(paths[1], dropbox_paths, queue,))
                        p.start()

                        p = Process(target=dw.upload_tar, args=(paths, queue, t_res,))
                        p.start()

            os.remove(event.src_path)  # always delete .txt

        elif file_format in img_ext:

            dir_name = treat_img(event.src_path)  # dir_name -> <id_terminal>-<pin>
            if dir_name:  # the folder exists, proceed...
                # get queue object form the dictionary ...
                queue = dict_q.pop(dir_name, False)
                if queue:
                    p = Process(target=dw.extract_mindtct, args=(event.src_path, queue, dir_name))
                    p.start()
                else:  # duplicated img, object not in queue
                    os.remove(event.src_path)
            else:  # always remove img, (directory does not exists; timeout, txt to img;)
                os.remove(event.src_path)

        else:  # always remove other files, formats
            os.remove(event.src_path)

if __name__ == "__main__":

    # init the logger
    logging.basicConfig(filename=log_path, format='%(asctime)s - %(levelname)s: (%(module)s) %(funcName)s - '
                                                        '%(message)s ', level=logging.ERROR)  # logging.WARNING

    # load config file, in case of error close the program and register the error
    try:
        __load_config_file(filename)
        print 'watchdog listening has been initialized'
        #print globals()  # just for test
    except IOError:
        logging.error('Could not read config file')
        raise SystemExit

    # define listened path
    path = sys.argv[1] if len(sys.argv) > 1 else watchdog_listening  # watchdog

    event_handler = MySLoggingEventHandler()
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
