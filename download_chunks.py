from multiprocessing import Pool, Process
import os
import subprocess as sub
import linecache
import Queue as q_exception  # since queue exceptions are not available in the multiprocessing module
import logging
import tarfile
import shutil
import sys
import time

import apidropbox as drop
import encryption as enc

#print 'download chunks working_path : {0}'.format(os.getcwd())  # getting the working path, just for test

#  checks sistem arch in order to choose binaries
is_64bits = sys.maxsize > 2**32
if is_64bits:
    #print 'im x86_64 system'
    enc.binary = './aescrypt_64'
    cmd_mindtct = './mindtct_64_V2 -b {0} {1}'
    #cmd_bozorth3 = './bozorth3_64 -p {0} -G {1}listXyt.lis '
    cmd_bozorth3 = './bozorth3_64 -p {0}/{0}.xyt -G {1}listXyt.lis '
else:
    #print 'im i386 (32 bit) system'
    enc.binary = './aescrypt_32'
    cmd_mindtct = './mindtct_32_V2 -b {0} {1}'
    #cmd_bozorth3 = './bozorth3_32 -p {0} -G {1}listXyt.lis '
    cmd_bozorth3 = './bozorth3_32 -p {0}/{0}.xyt -G {1}listXyt.lis '

slash = '/'

#
# private aux. and config methods
#


def print_globals():
    """

    :return:
    """
    print globals()


def update_globals(data_map):
    globals().update(data_map)
    globals()['tuple_OAuth_tokens'] = tuple(globals()['tuple_OAuth_tokens'])
    globals()['img_ext'] = tuple(globals()['img_ext'])
    globals()['file_ext'] = tuple(globals()['file_ext'])
    globals()['file_suffixes'] = tuple(globals()['file_suffixes'])
    globals()['register'] = tuple(globals()['register'])
    globals()['charge'] = tuple(globals()['charge'])


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
    with open('{0}/{1}'.format(local_path, name_lis), 'w') as f:  # fix path, writes path's files to listXyt.lis
        for path in files:
            f.write(path)
        f.close()


def __extract_tarfile(input_filename, dst_path, upload=None):
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

        if not upload:
            for file_name in files:
                dst_path_2 = dst_path + slash + file_name  # dst path for files within folder
                src_path_2 = src_path + slash + file_name  # src path files within folder
                os.rename(src_path_2, dst_path_2)  # move files
            os.rmdir(src_path)  # remove folder extracted from tar.gz

    os.remove(dst_path + input_filename)  # removes .tar.gz once got extracted the files


def __get_folders_processes(local_path, dropbox_paths):
    """

    :param local_path:
    :param dropbox_paths:
    :return:
    """
    pro_list = []
    test_t = time.time()
    for path, OAuth_token in dropbox_paths:  # dropbox_paths es ordenado 1,2,3,... por tanto si OAuth_token lo es tambien no hay problema
        k = Process(target=drop.retrieve_folder_parallel, args=(path, local_path, OAuth_token))
        k.start()
        pro_list.append(k)

    for p in pro_list:
        p.join()
    print 'hey there im done {} !'.format(time.time() - test_t)
    # 2.32230401039 2.20498013496


def __prepare_to_write_reg(t_res):
    """

    :param t_res:
    :return:
    """
    return t_res['ter_id'], t_res['operation'], t_res['pin'], t_res['name'], t_res['surname'], t_res['family'], \
           t_res['usr_id'], t_res['mail'], t_res['phone']


def __prepare_to_write_com(t_res):
    """

    :param t_res:
    :return:
    """
    return t_res['ter_id'], t_res['operation'], t_res['pin'], t_res['amount']


def __write_to_file(path, t_res, img_match, prepare):
    """

    :param path:
    :param t_res:
    :param img_match:
    :param prepare:
    :return:
    """
    file_name = '{0}/{1}.txt'.format(path, t_res['ter_id'])  # file's name is the <terminal-id>]
    values = prepare(t_res)
    try:
        with open(file_name, 'w') as f:
            for data in values:
                f.write('{0}\n'.format(data))
            f.write(img_match)
            f.close()
    except IOError:
        logging.error('could not create forwarding file')


def __writ_fail_watchdog_db(db_listening_path, id_ter):
    """

    :param db_listening_path:
    :param id_ter:
    :return:
    """

    file_name = '{0}/{1}.txt'.format(db_listening_path, id_ter)  # file's name is the <terminal-id>]
    data = '{0}\n'
    try:
        with open(file_name, 'w') as f:
            f.write(data.format('CHARGE'))
            f.write(data.format('FAILURE'))
            f.write(data.format(id_ter))
            f.close()
    except IOError:
        logging.error('could not create DB error message')


def __make_tarfile(output_filename, source_dir):
    """
    creates tar.gz file
    :param output_filename: str tar.gz file name
    :param source_dir: str given directory where the files come from
    :return: none
    """
    with tarfile.open(output_filename, 'w:gz') as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
        tar.close()

#
# charge methods
#


def download_tar(local_path, dropbox_paths, download_q):
    """

    :param local_path:
    :param dropbox_paths:
    :param download_q:
    :return:
    """
    try:
        # get the files from the cloud (dropbox accounts)
        __get_folders_processes(local_path, dropbox_paths)
        #  decrypts tar.gz and extract files in local_path
        enc.decrypt_chunks_parallel(local_path, key_path_2, enc_format)
        files = os.listdir(local_path)
        for file_name in files:
            if file_name.rfind(suffix_chunk_tar):
                __extract_tarfile(file_name, local_path)

        # merges and decrypts files
        enc.decrypt_to_file_parallel(local_path, key_path_1, enc_format)
        # build the file .lis
        __buid_bozorth_lis_file(local_path, name_lis)

    except (OSError, IOError):
        logging.error('error ')
        download_q.put(1)
    else:
        download_q.put('done')


def download_chunks(local_path, dropbox_paths, download_q):
    """

    :param local_path:
    :param dropbox_paths:
    :param download_q:
    :return:
    """
    try:
        # get the files from the cloud (dropbox accouts)
        __get_folders_processes(local_path, dropbox_paths)
        # decrypt
        enc.decrypt_chunks_parallel(local_path, key_path_2, enc_format)
        enc.decrypt_to_file_parallel(local_path, key_path_1, enc_format)
        # build the file .lis
        __buid_bozorth_lis_file(local_path, name_lis)

    except (OSError, IOError):
        logging.error('error ')
        download_q.put(1)
    else:
        download_q.put('done')


def compare(paths, t_res, read_q,):
    """

    :param paths:
    :param t_res:
    :param read_q:
    :return:
    """
    try:
        recv_1 = read_q.get(timeout=queue_timeout)
        recv_2 = read_q.get(timeout=queue_timeout)
    except q_exception.Empty:
        logging.error('timeout, no response')
        shutil.rmtree(paths[0])  # remove folder...
    else:
        if (recv_1 and recv_2) != 1:
            try:
                results = sub.check_output([cmd_bozorth3.format(paths[0], paths[1])]
                                           , shell=True)  # compare through bozorth
            except sub.CalledProcessError:
                logging.error('bozorth3 OS error')
            else:
                # find the greatest number from the result and its index
                res_list = map(int, results.split())  # string list to int list

                max_value = max(res_list)  # get greatest number
                max_index = res_list.index(max_value)  # get its index
                # get fingerprint's id from the (index)line number in listxyt.lis
                line = linecache.getline('{0}{1}'.format(paths[1], name_lis), max_index + 1)
        # IMPORTANT: clear the cache, otherwise will read always the same values that come from an individual terminal
                linecache.clearcache()
                line = os.path.basename(line)
                line = line[:line.rfind('.')]
                print max_value
                if min_value <= max_value:  # we got a max.
                    print 'Match with : {0}'.format(line)  # the result, name of the greatest one
                    __write_to_file(watchdog_forward, t_res, line, __prepare_to_write_com)
                else:
                    __writ_fail_watchdog_db(db_listening_path, t_res['ter_id'])
                    print 'not found max value, forward to db_response to be send terminals folder'

        shutil.rmtree(paths[0])  # always remove


#
# register methods
#


def download_tar_up(local_path, dropbox_paths, download_q):
    """

    :param local_path:
    :param dropbox_paths:
    :param download_q:
    :return:
    """
    try:
        # get the files from the cloud (dropbox accounts)
        __get_folders_processes(local_path, dropbox_paths)
        #  decrypts tar.gz and extract files in local_path
        enc.decrypt_chunks_parallel(local_path, key_path_2, enc_format)  # is_64bits
        files = os.listdir(local_path)
        for file_name in files:
            if file_name.rfind(suffix_chunk_tar):
                __extract_tarfile(file_name, local_path, True)

    except (OSError, IOError):
        logging.error('error ')
        download_q.put(1)
    else:
        download_q.put('done')


def upload_tar(paths, read_q, t_res):
    """

    :param paths:
    :param read_q:
    :param t_res:
    :return:
    """
    try:
        recv_1 = read_q.get(timeout=queue_timeout)
        recv_2 = read_q.get(timeout=queue_timeout)
    except q_exception.Empty:
        logging.error('timeout, no response')
        shutil.rmtree(paths[0])  # remove folder
    else:
        if (recv_1 and recv_2) != 1:
            # treat the img given img. (rename it?), encrypt it, split. t_res[3] + t_res[6] -> name of the img !!!!
            enc.encrypt_files(paths[0]+slash, key_path_1, paths[1], enc_format, t_res['name'] + t_res['usr_id'])

            # moves  the generated chunks to chunk's folders
            for index, f_suffix in enumerate(file_suffixes):
                sub.call('mv {0}*-0{2} {0}chunk{1}'.format(paths[1], index+1, f_suffix), shell=True)

            # create tar.gz (name format : <pin>%<part>.tar.gz)
            for index, up_path in enumerate(os.listdir(paths[1])):  # name
                __make_tarfile(dropbox_tar_format.format(paths[1], t_res['pin'], index+1, suffix_chunk_tar),
                               paths[1] + up_path)

            # encrypt tar.gz
            enc.encrypt_chunks_tar(paths[1], key_path_2, suffix_chunk_tar)

            # upload encrypted files (it overwrites files with same name and format in dropbox)
            tar_aes_path = [(i, i[i.find('%')+1:i.find(suffix_chunk_tar)]) for i in os.listdir(paths[1]) if i.find(enc_format) > -1]

            print tar_aes_path
            for tar_aes_file, index in tar_aes_path:
                drop.upload_file(paths[1] + tar_aes_file, dropbox_paths_format.format(t_res['pin'], index+slash),
                                 tuple_OAuth_tokens[int(index)-1])
            __write_to_file(watchdog_forward, t_res, t_res['name'] + t_res['usr_id'], __prepare_to_write_reg)

        shutil.rmtree(paths[0])  # always remove

#
# extract img method
#


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
    except OSError:
        logging.error('mindtct_V2 OS error')
        extract_q.put(1)
    else:
        extract_q.put('done')

#
# watchdog DB methods
#


def prepare_client_file(file_name, values):
    """

    :param file_name:
    :param values:
    :return:
    """
    try:
        with open(file_name, 'w') as f:
            for var in values:
                f.write(var+'\n')
            f.close()
    except IOError:
        logging.error('could not create client file')
