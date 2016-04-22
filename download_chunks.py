from multiprocessing import Process
import os
import subprocess as sub
import linecache
import Queue as q_exception  # since queue exceptions are not available in the multiprocessing module
import logging
import apidropbox as drop
import encryption as enc
import tarfile
import shutil
import time
## quitar...
# chunks
dropbox_path_1 = '/pin0000-1'
dropbox_path_2 = '/pin0000-2'
dropbox_path_3 = '/pin0000-3'
# tar.gz
dropbox_path_1_dw = '/pin4444-1'  # sin slash para bajar cosas
dropbox_path_2_dw = '/pin4444-2'
dropbox_path_3_dw = '/pin4444-3'
####

slash = '/'
cmd_mindtct = './mindtct_V2 -b {0} {1}'
cmd_bozorth3 = './bozorth3 -p {0} -G {1}listXyt.lis '
cmd_bozorth32 = './bozorth3 -p {0}.xyt -G {1}listXyt.lis '


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

    with tarfile.open(dst_path+input_filename, 'r:gz') as tar:
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
    os.remove(dst_path+input_filename)  # removes .tar.gz once got extracted the files


def download_tar(local_path, download_q, OAuth_token, name_lis, enc_format):
    '''

    :param local_path:
    :param download_q:
    :param OAuth_token:
    :param name_lis:
    :param enc_format:
    :return:
    '''
    try:

        p1 = Process(target=drop.retrieve_folder_parallel, args=(dropbox_path_1_dw, local_path, OAuth_token))
        p1.start()
        p2 = Process(target=drop.retrieve_folder_parallel, args=(dropbox_path_2_dw, local_path, OAuth_token))
        p2.start()
        p3 = Process(target=drop.retrieve_folder_parallel, args=(dropbox_path_3_dw, local_path, OAuth_token))
        p3.start()

        p1.join()
        p2.join()
        p3.join()
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
    else: # envie el path del fichero .lis
        download_q.put('download_done')


def download_chunks(local_path, download_q, OAuth_token, name_lis, enc_format):
    '''

    :param local_path:
    :param download_q:
    :param OAuth_token:
    :param name_lis:
    :param enc_format:
    :return:
    '''
    # que se le pase el pin -> dropbox_path
    try:
        p1 = Process(target=drop.retrieve_folder_parallel, args=(dropbox_path_1, local_path, OAuth_token))  # local_path
        p1.start()
        p2 = Process(target=drop.retrieve_folder_parallel, args=(dropbox_path_2, local_path, OAuth_token))  # local_path
        p2.start()
        p3 = Process(target=drop.retrieve_folder_parallel, args=(dropbox_path_3, local_path, OAuth_token))  # local_path
        p3.start()

        p1.join()
        p2.join()
        p3.join()
        # decrypt
        enc.decrypt_chunks_parallel(local_path, enc.key_path_2, enc_format)
        enc.decrypt_to_file_parallel(local_path, enc.key_path_1)
        # build the file .lis
        __buid_bozorth_lis_file(local_path, name_lis)

    except (OSError, IOError) as e:
        logging.error('error ')
        download_q.put(1)
    else:
        download_q.put('download_done')


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
        extract_q.put(relative_path)


def compare(dir_name, local_path, read_q, q_timeout, min_value):
    '''

    :param source_path:
    :param local_path:
    :param read_q:
    :param q_timeout:
    :param min_value:
    :return:
    '''
    try:
        extract = read_q.get(timeout=q_timeout)
        download = read_q.get(timeout=q_timeout)
    except q_exception.Empty:
        logging.error('timeout, no response')
        shutil.rmtree(dir_name)  # borra carpeta...
    else:
        #if extract != 1 and download != 1:
        if (extract and download) != 1:
            try:
                results = sub.check_output([cmd_bozorth32.format(extract, local_path)]
                                           , shell=True)  # compare through bozorth
            except sub.CalledProcessError as e:
                shutil.rmtree(dir_name)  # borra carpeta...
                logging.error('bozorth3 OS error')
            else:
                # find the greatest number from the result and its index
                res_list = map(int, results.split())  # string list to int list

                max_value = max(res_list)  # get greatest number
                max_index = res_list.index(max_value)  # get its index
                # get fingerprint's id through the (index)line number from listxyt.lis
                line = linecache.getline('{0}listXyt.lis'.format(local_path), max_index+1)
                #line = line[line.rfind('/')+1:line.rfind('.')]
                line = os.path.basename(line)
                line = line[:line.rfind('.')]
                print max_value
                if min_value <= max_value:
                    print 'Match with : {0}'.format(line)  # the result, name of the greatest one
        #else:
        #    logging.error('timeout, no response') # no tiene mucho sentido ya que los metodos que prvocan lo registran
        shutil.rmtree(dir_name)  # siempre borrar


'''
def compare(source_path, local_path, read_q, q_timeout, min_value):

    try:
        extract = read_q.get(timeout=q_timeout)
        download = read_q.get(timeout=q_timeout)
    except q_exception.Empty:
        logging.error('error sync time')
        # borra carpeta...
    else:
        #if extract != 1 and download != 1:
        if (extract and download) != 1:
            try:
                results = sub.check_output([cmd_bozorth3.format(source_path, local_path)]
                                           , shell=True)  # compare with bozorth
            except sub.CalledProcessError as e:
                # borra carpeta...
                logging.error('bozorth3 OS error')
            else:
                # find the greatest number from the result and its index
                res_list = map(int, results.split())  # string list to int list

                max_value = max(res_list)  # get greatest number
                max_index = res_list.index(max_value)  # get its index
                # get fingerprint's id through the (index)line number from listxyt.lis
                line = linecache.getline('{0}listXyt.lis'.format(local_path), max_index+1)
                #line = line[line.rfind('/')+1:line.rfind('.')]
                line = os.path.basename(line)
                line = line[:line.rfind('.')]
                print max_value
                if min_value <= max_value:
                    print 'the match with : {0}'.format(line)  # the result, name of the greatest one
        else:
            # borra carpeta...
            logging.error('timeout, no response')
'''
