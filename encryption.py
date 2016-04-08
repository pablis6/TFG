import subprocess
import os
from multiprocessing import Pool


# relative paths
files_path_1 = './encrypt/'
chunks_path_1 = './encrypt/chunks/'
key_path_1 = '../aesrypt/secret.key'
key_path_2 = '../aesrypt/secret2.key'

# split genera los ficheros en el path de donde ha sido llamado el script...
split_path = '/home/rnov/tfg/dropboxApi/'
global_list = []


def __get_files_names(files_path, filter_char):
    """
    auxiliary function that obtains the files names in a given directory.
    :param files_path: str folder's path
    :param filter_char: str
    :return: None
    """
    list_files = os.listdir(files_path)
    new_list = set([i[:i.find(filter_char)] for i in list_files])
    return new_list


def encrypt_files(files_path, key_path, chunks_path):
    """
    encrypts .xyt files in a given directory with a given key
    :param files_path: str path to the directory
    :param key_path: str key's path
    :param chunks_path: str chunks's path
    :return: generates one .xyt.aes file and three chunks from it.
    """
    list_files = os.listdir(files_path)
    for xytfile in list_files:
        if xytfile.rfind('.xyt') > 1:  # while the file has the format .xyt
            subprocess.call(['aescrypt', '-e', '-k', key_path, files_path+xytfile])  # encrypt .xyt file
            name = xytfile.rstrip('.xyt')
            name += '-'  # name's format for the chunks
            subprocess.call(['split', '-n', '3', files_path+xytfile+'.aes', name,
                             '--numeric-suffixes=2'])  # split the file in chunks (no deja en el mismo dir)

    list_files = os.listdir(split_path)
    for chunks in list_files:
        if chunks.rfind('-0') > -1:
            #print chunks
            subprocess.call(['mv', '-f', split_path+chunks, chunks_path+chunks])


def encrypt_chunks(chunks_path, key_path):
    """
    encrypts files (chunks of a file/s) in a given directory with a given key
    :param chunks_path: str directory's path
    :param key_path: str key's path
    :return: None
    """
    listFiles = os.listdir(chunks_path)
    suffix = '-0'  # needed suffix for the files to be processed
    for chunks_file in listFiles:
        if chunks_file.rfind(suffix) > 1:  # while the file has the suffix and it is not in the first position
            subprocess.call(['aescrypt', '-e', '-k', key_path, chunks_path+chunks_file])


def decrypt_chunks(files_path, key_path_chunk, dst_path=None):
    """
    decrypts chunk files from given path to given directory
    :param files_path: str chunks's path
    :param key_path_chunk: str key's path
    :param dst_path: str destiny file path
    :return: None
    """
    if dst_path is None:
        dst_path = files_path
    list_files = os.listdir(files_path)
    for aes_file in list_files:  # decrypt the chunks
        if aes_file.rfind('.aes') > -1:  # while a file has the format .aes, decrypt it
            subprocess.call(['aescrypt', '-d', '-k', key_path_chunk, dst_path+aes_file])

    subprocess.call('rm -f {0}*.aes'.format(files_path), shell=True)
    # remove all .aes files from files_path, for test in case same folder


def aux_wrapper_decrypt_chunks(aes_file, key_path_chunk, dst_path):
    """
    auxiliary wrapper function used in decrypt_chunks_parallel.
    :param aes_file: str name
    :param key_path_chunk: str key's path
    :param dst_path: str destiny file path
    :return: None
    """
    subprocess.call(['aescrypt', '-d', '-k', key_path_chunk, dst_path+aes_file])


def decrypt_chunks_parallel(files_path, key_path_chunk, dst_path=None):
    """
    decrypts and merge chunk files from given path to given directory/ies
    :param files_path: str source path
    :param key_path_chunk: str key's path
    :param dst_path: str destiny file path
    :return: None
    """
    if dst_path is None:
        dst_path = files_path
    list_files = os.listdir(files_path)
    #print list_files

    pool = Pool(processes=30,)  # 30
    multiple_results = [pool.apply_async(aux_wrapper_decrypt_chunks, (aes_file, key_path_chunk, dst_path))
                        for aes_file in list_files if aes_file.rfind('.aes') > -1]
    #print multiple_results
    for res in multiple_results:
        res.get()  # timeout=3
    subprocess.call('rm -f {0}*.aes'.format(files_path), shell=True)
    # remove all .aes files from files_path, for test in case same folder


def __aux_decrypt_file(chunk, files_path, dst_path, key_path):
        """
        decrypt_to_file() and decrypt_to_file_parallel() auxiliary function that merges the chunks into
        single file and decrypts it.
        :param chunk: file str name (chunk)
        :param files_path: str source path
        :param dst_path: str destiny file path
        :param key_path: str key's path
        :return: None
        """
        from_path = files_path+chunk+'*'
        to_path = dst_path+chunk

        cat_command = '{0} > {1}.xyt.aes'.format(from_path, to_path)  # forms cat call
        subprocess.call('cat {0}'.format(cat_command), shell=True)  # merge the chucks from one file to a file.
        subprocess.call('rm -f {0}{1}-*'.format(files_path, chunk), shell=True)  # removes single file's chucks
        single_file_path = to_path+'.xyt.aes'  # file_name
        subprocess.call(['aescrypt', '-d', '-k', key_path, single_file_path])  # decrypt single file
        subprocess.call('rm -f {0}{1}*.aes'.format(dst_path, chunk), shell=True)  # remove .aes remaining file


def decrypt_to_file(files_path, key_path, dst_path=None):
    """
    decrypts and merges chunks from given path to given directory with a given key
    :param files_path: str chunks source path
    :param key_path: str key's path
    :param dst_path: str destiny path
    :return: None
    """
    if dst_path is None:
        dst_path = str(files_path)

    list_files = __get_files_names(files_path, '-')  # lists the names of all files from the chucks, gets the name's files
    for chunk in list_files:
        __aux_decrypt_file(chunk, files_path, dst_path, key_path)


def decrypt_to_file_parallel(files_path, key_path, dst_path=None):
    """
    decrypts and merges chunks from given path to given directory with a given key. Multiprocess function
    :param files_path: str chunks source path
    :param key_path: str key's path
    :param dst_path: str destiny path
    :return: None
    """
    if dst_path is None:
        dst_path = str(files_path)

    list_files = __get_files_names(files_path, '-')  # lists the names of all files from the chucks, gets the name of the files

    pool = Pool(processes=30,)
    multiple_results = [pool.apply_async(__aux_decrypt_file, (chunk, files_path, dst_path, key_path))
                        for chunk in list_files]
    #print multiple_results
    for res in multiple_results:
        res.get()  # timeout=3


def __aux_decrypt():
    """
    auxiliary function that helps debugging decryption functions from encryption module
    :return: None
    """
    decrypt_chunks_parallel(chunks_path_1, key_path_2)
    # decrypt_chunks(chunks_path_1, key_path_2)
    # decrypt_to_file(chunks_path_1, key_path_1)
    decrypt_to_file_parallel(chunks_path_1, key_path_1)

# encrypt_files(files_path_1, key_path_1, chunks_path_1)  # -> .xyt.aes file and creates 3 chunks from it
# encrypt_chunks(chunks_path_1, key_path_2)  # encrypts the chunks -> chunks.aes

import timeit

# print timeit.timeit(aux_decrypt, number=1)

# decrypt_chunks(chunks_path_1, key_path_2)  # decrypt the chunks.aes -> chunks
# decrypt_to_file(chunks_path_1, key_path_1)  # merge the chunks into files and decrypts them, chunks -> files.xyt
# decrypt_to_file_parallel(chunks_path_1, key_path_1)

# set_list = set(global_list)
# print set_list
