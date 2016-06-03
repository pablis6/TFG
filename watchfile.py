import sys
import os
from multiprocessing import Process, Queue
import time
import logging
import linecache
import yaml
# installed and custom packages
custom_path = '{0}/{1}'
#sys.path.remove('/usr/lib/python2.7/site-packages')  # para test, probar dependencias
sys.path.insert(1, custom_path.format(os.getcwd(), 'depen_packages'))  # dependency packages
sys.path.insert(1, custom_path.format(os.getcwd(), 'payfi'))  # payfi packages with own dependence inside
print sys.path  # paths for modules and packages
from payfi import download_chunks as dw
from payfi.watchdog.observers import Observer
from payfi.watchdog.events import LoggingEventHandler
import apidropbox as drop

filename = 'app_config.yalm'
log_path = 'my_log.log'

#dropbox_paths = ('/pin4444-1', '/pin4444-2', '/pin4444-3')


dict_q = {}
slash = '/'


def __load_config_file(filename):
    """

    :param filename:
    :return:
    """
    with open(filename) as f:
        dataMap = yaml.safe_load(f)
        f.close()
    globals().update(dataMap)
    globals()['tuple_OAuth_tokens'] = tuple(globals()['tuple_OAuth_tokens'])
    globals()['img_ext'] = tuple(globals()['img_ext'])
    globals()['file_ext'] = tuple(globals()['file_ext'])
    globals()['file_suffixes'] = tuple(globals()['file_suffixes'])


def treat_txt_file(path_tfile):
    '''
    manages incoming text file from a terminal, if it's well formed creates a dict otherwise returns false.
    :param path_tfile: str, path to the text file
    :return: tuple or False in case of error
    '''
    id_terminal = linecache.getline(path_tfile, 1).rstrip()  # removes '\n'
    t_op = linecache.getline(path_tfile, 2).rstrip()
    pin = linecache.getline(path_tfile, 3).rstrip()

    if t_op == charge:
        amount = linecache.getline(path_tfile, 4).rstrip()
        #t_res = (id_terminal, t_op, pin, amount)
        t_res = {'ter_id': id_terminal, 'operation': t_op, 'pin': pin, 'amount': amount}
    elif t_op == register:
        usr_name = linecache.getline(path_tfile, 4).rstrip()
        surname = linecache.getline(path_tfile, 5).rstrip()
        family = linecache.getline(path_tfile, 6).rstrip()
        id_usr = linecache.getline(path_tfile, 7).rstrip()
        mail = linecache.getline(path_tfile, 8).rstrip()
        phone = linecache.getline(path_tfile, 9).rstrip()
        #t_res = (id_terminal, t_op, pin, usr_name, surname, family, id_usr, mail, tlf_num)
        t_res = {'ter_id': id_terminal, 'operation': t_op, 'pin': pin, 'name': usr_name,
                 'surname': surname, 'family': family, 'usr_id': id_usr, 'mail': mail, 'phone': phone}
    else:
        return False

    if len(t_res) == 0:  # pensar..
        return False
    else:
        return t_res


def treat_img(path_file):
    '''
    discover whether a directory exists or not (used for incoming images), if exists returns its name, False otherwise.
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
    create directories for a single operation.
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
    '''
    forms a list with the folder's names in dropbox, (ord list 1,2,3..)
    :param pin: int required to form the folder's name
    :return: lst list with names
    '''
    paths = []
    for index, value in enumerate(range(1, 4)):
        paths.append((dropbox_paths_format.format(pin, value), tuple_OAuth_tokens[index]))
    return paths


class MySLoggingEventHandler5(LoggingEventHandler):

    def on_created(self, event):
        print 'file has been created {0}'.format(event.src_path)  # TEST...
        file_format = event.src_path[event.src_path.rfind('.'):]  # finds the last point.

        if file_format in file_ext:
            # read data and return dict or false
            t_res = treat_txt_file(event.src_path)
            # in case of success: charge or register
            queue = Queue(2)  # a queue per job
            paths = create_dir(t_res['ter_id'])  # dir_name -> <id_terminal>
            if t_res and t_res['operation'] == charge:

                if paths:  # paths -> (dir_name, local_cmp)

                    dict_q[paths[0]] = queue  # saves queue dir to dir with dir name as key
                    # pin 4444-> dropbox_paths => (/pin{0}-1, /pin{0}-2, /pin{0}-3)
                    dropbox_paths = form_dropbox_path(t_res['pin'])
                    p = Process(target=dw.download_tar, args=(paths[1], dropbox_paths, queue, name_lis, enc_format,
                                                              suffix_chunk_tar, key_path_1, key_path_2,))
                    p.start()

                    p = Process(target=dw.compare, args=(paths[0], paths[1], watchdog_forward, t_res, queue,
                                                         queue_timeout, min_value, name_lis,))
                    p.start()

            elif t_res:  # register

                if paths:  # paths -> (dir_name, local_cmp)
                    dict_q[paths[0]] = queue  # saves queue dir to dir with dir name as key

                    dropbox_paths = form_dropbox_path(t_res['pin'])
                    p = Process(target=dw.download_tar_up, args=(paths[1], dropbox_paths, queue, enc_format,
                                                                 suffix_chunk_tar, key_path_2,))
                    p.start()

                    p = Process(target=dw.upload_tar, args=(paths, queue, queue_timeout, file_suffixes, enc_format,
                                                            t_res, dropbox_paths_format, suffix_chunk_tar,
                                                            dropbox_tar_format, key_path_1, key_path_2,
                                                            tuple_OAuth_tokens,))
                    p.start()

            os.remove(event.src_path)  # always delete .txt

        elif file_format in img_ext:

            dir_name = treat_img(event.src_path)  # dir_name -> <id_terminal>-<pin>
            if dir_name:  # the folder exist, proceed...
                # get queue object form the dictionary ...
                queue = dict_q.pop(dir_name, False)
                if queue:
                    p = Process(target=dw.extract_mindtct, args=(event.src_path, queue, dir_name))
                    p.start()
            else:  # directory does not exists (timeout, txt to img), remove img
                os.remove(event.src_path)

        else:  # other files, formats
            os.remove(event.src_path)

if __name__ == "__main__":

    # init the logger
    logging.basicConfig(filename=log_path, format='%(asctime)s - %(levelname)s: (%(module)s) %(funcName)s - '
                                                        '%(message)s ', level=logging.ERROR)  # logging.WARNING

    # load config file, in case of error close the program and register the error
    try:
        __load_config_file(filename)
        print globals()
    except IOError:
        logging.error('Could not read config file')
        raise SystemExit

    # define listened path
    path = sys.argv[1] if len(sys.argv) > 1 else custom_path.format(os.getcwd(), watchdog_listening)  # watchdog

    event_handler = MySLoggingEventHandler5()
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
'''
def form_dropbox_path(pin):
    paths = []
    for k in range(1, 4):
        paths.append(dropbox_paths_format.format(pin, k))
    return paths



    class MySLoggingEventHandler4(LoggingEventHandler):

    def on_created(self, event):
        print 'file has been created {0}'.format(event.src_path)  # TEST...
        file_format = event.src_path[event.src_path.rfind('.'):]  # finds the last point.
        if file_format == '.txt':

            # read data and return tuple or false
            t_res = treat_txt_file(event.src_path)
            # in case of success: charge or register
            queue = Queue(2)  # a queue per job
            paths = create_dir(t_res[0])  # dir_name -> <id_terminal>
            if t_res and t_res[1] == 'charge':

                #paths = create_dir(t_res[0])  # dir_name -> <id_terminal>
                if paths:  # paths -> (dir_name, local_cmp)
                    #queue = Queue(2)  # a queue per job
                    dict_q[paths[0]] = queue  # saves queue dir to dir with dir name as key
                    # dropbox path tendrian que seguir algun formato para que lleven el pin al ser pasado ej
                    # pin 4444-> dropbox_paths => (/pin{0}-1, /pin{0}-2, /pin{0}-3)
                    dropbox_paths = form_dropbox_path(t_res[2])
                    p = Process(target=dw.download_tar, args=(paths[1], dropbox_paths, queue, name_lis, enc_format,
                                                              suffix_chunk_tar, key_path_1, key_path_2,))

                    p.start()
                    # hacer o no hacer join para que lo espere, afectara queue_timeout, con join no hace falta queue
                    p = Process(target=dw.compare, args=(paths[0], paths[1], watchdog_forward, t_res, queue,
                                                         queue_timeout, min_value, name_lis,))
                    p.start()

            elif t_res:  # register

                if paths:  # paths -> (dir_name, local_cmp)
                    dict_q[paths[0]] = queue  # saves queue dir to dir with dir name as key

                    dropbox_paths = form_dropbox_path(t_res[2])
                    p = Process(target=dw.download_tar_up, args=(paths[1], dropbox_paths, queue, enc_format,
                                                                 suffix_chunk_tar, key_path_2,))
                    p.start()

                    p = Process(target=dw.upload_tar, args=(paths, queue, queue_timeout, 3, '', enc_format, t_res,
                                                            dropbox_paths_format, suffix_chunk_tar, dropbox_tar_format,
                                                            key_path_1, key_path_2, tuple_OAuth_tokens,))
                    p.start()

            os.remove(event.src_path)  # always delete .txt

        elif file_format == '.png' or '.jpg':

            dir_name = treat_img(event.src_path)  # dir_name -> <id_terminal>-<pin>
            if dir_name:  # the folder exist, proceed...
                # get queue object form the dictionary ...
                queue = dict_q.pop(dir_name, False)
                if queue:
                    p = Process(target=dw.extract_mindtct, args=(event.src_path, queue, dir_name))
                    p.start()
            else:  # directory does not exists (timeout, txt to img), remove img
                os.remove(event.src_path)

        else:  # other files, formats
            os.remove(event.src_path)
    '''