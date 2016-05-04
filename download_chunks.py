from multiprocessing import Pool, Process
import os
import subprocess as sub
import linecache
import Queue as q_exception  # since queue exceptions are not available in the multiprocessing module
import logging
import tarfile
import shutil
import time

import apidropbox as drop
import encryption as enc

print 'download chunks working_path : {0}'.format(os.getcwd())  #  getting the working path, just for test
slash = '/'
cmd_mindtct = './mindtct_32_V2 -b {0} {1}'
cmd_bozorth3 = './bozorth3_32 -p {0} -G {1}listXyt.lis '
cmd_bozorth32 = './bozorth3_32 -p {0}/{0}.xyt -G {1}listXyt.lis '


def __buid_bozorth_lis_file(local_path, name_lis):
    """
    creates .lis file which is used by bozorth_3 to compare multiple to 1 files.
    :param local_path: str path to the files
    :param name_lis: str .lis file name
    :return: None
    """
    # create the file
    files = os.listdir(local_path)  # local_cmp/
    files = ['{0}{1}\n'.format(local_path, i) for i in files]  # add the path to the files (relative to .py)
    # open, mind the mode
    with open('{0}/{1}.lis'.format(local_path, name_lis), 'w') as f:  # fix path, writes path's files to listXyt.lis
        for path in files:
            f.write(path)
        f.close()
        # devuelva el path del fichero .lis


def __extract_tarfile(input_filename, dst_path):
    """
    extract files from tar.gz file, same source and destiny path.
    :param intput_filename: str tar.gz file name
    :param dst_path: str path to tar.gz and destiny path to extract.
    :return: None
    """

    with tarfile.open(dst_path + input_filename, 'r:gz') as tar:
        ar = tar.getmembers()  # get the members withing tar.gz
        tar.extractall(path=dst_path)  # extract tar.gz in given dst_path
        tar.close()
        ar = ar.pop(0)  # name of the folder within tar.gz
        src_path = dst_path + slash + ar.name  # dst_path with folder within the tar.gz
        files = os.listdir(src_path)  # list files withing folder tar.gz

        for file_name in files:
            dst_path_2 = dst_path + slash + file_name  # dst path for files within folder
            src_path_2 = src_path + slash + file_name  # src path files within folder
            os.rename(src_path_2, dst_path_2)  # move files
        os.rmdir(src_path)  # remove folder extracted from tar.gz
    os.remove(dst_path + input_filename)  # removes .tar.gz once got extracted the files


def __get_folders_processes(local_path, OAuth_token, dropbox_paths):
    # OAuth_token, dropbox_paths son lista una capeta por cuenta
    # nota: no se puede implementar como un pool de procesos pq esto no pueden lanzar otros procesos(
    # daemonic processes are not allowed to have children ) se podria si se cambia en el modulo de daemonic= yes a no
    # pero hace el codigo no reutilizabel
    pro_list = []
    test_t = time.time()
    for path in dropbox_paths:
        k = Process(target=drop.retrieve_folder_parallel, args=(path, local_path, OAuth_token))
        k.start()
        pro_list.append(k)

    for p in pro_list:
        p.join()
    print 'hey there im done {} !'.format(time.time() - test_t)
    # 2.32230401039 2.20498013496


def __write_to_file(path, t_res, img_match):
    """

    :param path:
    :param t_res:
    :param img_match:
    :return:
    """

    file_name = '{0}/{1}.txt'.format(path, t_res[0])  # file's name is the <terminal-id>
    try:
        with open(file_name, 'w') as f:
            for data in t_res:
                f.write('{0}\n'.format(data))
            f.write(img_match)
            f.close()
    except IOError:
        print 'couldn create the file'


def download_tar(local_path, dropbox_paths, download_q, OAuth_token, name_lis, enc_format):
    '''

    :param local_path:
    :param download_q:
    :param OAuth_token:
    :param name_lis:
    :param enc_format:
    :return:
    '''
    try:
        # get the files from the cloud (dropbox accouts)
        __get_folders_processes(local_path, OAuth_token, dropbox_paths)
        #  decrypts tar.gz and extract files in local_path
        enc.decrypt_chunks_parallel(local_path, enc.key_path_2, enc_format)
        files = os.listdir(local_path)
        for file_name in files:
            if file_name.rfind('.tar.gz'):
                __extract_tarfile(file_name, local_path)

        # merges and decrypts files
        enc.decrypt_to_file_parallel(local_path, enc.key_path_1, enc_format)
        # build the file .lis
        __buid_bozorth_lis_file(local_path, name_lis)

    except (OSError, IOError) as e:
        logging.error('error ')
        download_q.put(1)
    else:  # envie el path del fichero .lis
        download_q.put('done')


def download_chunks(local_path, dropbox_paths, download_q, OAuth_token, name_lis, enc_format):
    '''

    :param local_path:
    :param dropbox_paths:
    :param download_q:
    :param OAuth_token:
    :param name_lis:
    :param enc_format:
    :return:
    '''
    try:
        # get the files from the cloud (dropbox accouts)
        __get_folders_processes(local_path, OAuth_token, dropbox_paths)
        # decrypt
        enc.decrypt_chunks_parallel(local_path, enc.key_path_2, enc_format)
        enc.decrypt_to_file_parallel(local_path, enc.key_path_1, enc_format)
        # build the file .lis
        __buid_bozorth_lis_file(local_path, name_lis)

    except (OSError, IOError) as e:
        logging.error('error ')
        download_q.put(1)
    else:
        download_q.put('done')


def extract_mindtct(source_path, extract_q, dst_path):
    '''
    extracts minutaie from an img and saves the output in a given path
    :param source_path: str img path
    :param extract_q: queue to signal another process.
    :param dst_path: str path to be placed the output (.xyt and .brw)
    :return: None
    '''
    try:
        relative_path = '{0}/{0}'.format(dst_path)
        cmd = cmd_mindtct.format(source_path, relative_path)
        os.system(cmd)
        os.remove(source_path)  # removes the image
    except OSError as e:
        logging.error('mindtct_V2 OS error')
        extract_q.put(1)
    else:
        extract_q.put('done')


def compare(dir_name, local_path, path_output, t_res, read_q, q_timeout, min_value):
    '''

    :param source_path:
    :param local_path:
    :param read_q:
    :param q_timeout:
    :param min_value:
    :return:
    '''
    try:
        recv_1 = read_q.get(timeout=q_timeout)
        recv_2 = read_q.get(timeout=q_timeout)
    except q_exception.Empty:
        logging.error('timeout, no response')
        shutil.rmtree(dir_name)  # remove folder...
    else:
        if (recv_1 and recv_2) != 1:
            try:
                results = sub.check_output([cmd_bozorth32.format(dir_name, local_path)]
                                           , shell=True)  # compare through bozorth
            except sub.CalledProcessError as e:
                shutil.rmtree(dir_name)  # borrar carpeta...
                logging.error('bozorth3 OS error')
            else:
                # find the greatest number from the result and its index
                res_list = map(int, results.split())  # string list to int list

                max_value = max(res_list)  # get greatest number
                max_index = res_list.index(max_value)  # get its index
                # get fingerprint's id through the (index)line number from listxyt.lis
                line = linecache.getline('{0}listXyt.lis'.format(local_path), max_index + 1)
                # line = line[line.rfind('/')+1:line.rfind('.')]
                line = os.path.basename(line)
                line = line[:line.rfind('.')]
                print max_value
                if min_value <= max_value:
                    print 'Match with : {0}'.format(line)  # the result, name of the greatest one
                    __write_to_file(path_output, t_res, line)

        # else:
        #    logging.error('timeout, no response aqrqr') # no tiene mucho sentido ya que los metodos que prvocan lo registran
        shutil.rmtree(dir_name)  # siempre borrar
