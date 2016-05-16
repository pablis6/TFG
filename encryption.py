import subprocess
import os
from multiprocessing import Pool

print 'encryption : {0}'.format(os.getcwd())  # getting the working path, just for test
# subprocess.call(['./aescrypt_32', '-e', '-k', 'secret.key', 'encrypt'])

key_path_1 = 'secret.key'
key_path_2 = 'secret2.key'

# split genera los ficheros en el path de donde ha sido llamado el script...
split_path = os.getcwd()  # gets current working path, '/home/rnov/tfg/dropboxApi/work_unit'
# variables que se utilizan a lo largo de todas las funciones, internar que se cargue su valor por YALMP

binary = ''
#
# private aux. methods
#


def __get_files_names(files_path, filter_char):
    """
    auxiliary function, obtains files names from a given directory.
    :param files_path: str folder's path
    :param filter_char: str
    :return: None
    """
    list_files = os.listdir(files_path)
    new_list = set([i[:i.find(filter_char)] for i in list_files])
    return new_list


def __aux_wrapper_decrypt_chunks(aes_file, key_path_chunk, dst_path):
    """
    auxiliary wrapper function used in decrypt_chunks_parallel.
    :param aes_file: str name
    :param key_path_chunk: str key's path
    :param dst_path: str destiny file path
    :return: None
    """
    subprocess.call([binary, '-d', '-k', key_path_chunk, dst_path+aes_file])  # './aescrypt_32'


def __aux_decrypt_file(chunk, files_path, dst_path, key_path, enc_format):
        """
        decrypt_to_file() and decrypt_to_file_parallel() auxiliary function that merges the chunks into
        single file and decrypts it.
        :param chunk: file str name (chunk)
        :param files_path: str source path
        :param dst_path: str destiny file path
        :param key_path: str key's path
        :return: None
        """
        #print binary
        from_path = files_path+chunk+'*'
        to_path = dst_path+chunk

        cat_command = '{0} > {1}.xyt{2}'.format(from_path, to_path, enc_format)  # forms cat call
        subprocess.call('cat {0}'.format(cat_command), shell=True)  # merge the chucks from one file to a file.


        aux1 = subprocess.call('rm -f {0}{1}-*'.format(files_path, chunk), shell=True)  # removes single file's chucks
        single_file_path = to_path+'.xyt{0}'.format(enc_format)  # file_name

        aux2 = subprocess.call([binary, '-d', '-k', key_path, single_file_path])  # decrypt single file './aescrypt_32'
        aux3 = subprocess.call('rm -f {0}{1}*{2}'.format(dst_path, chunk, enc_format), shell=True)
        # remove .aes remaining file
        if chunk == 'robert':
            print chunk
            print cat_command
            print aux1
            print 'single_file_path {0}'.format(single_file_path)
            print aux2
            print aux3# """
        #print single_file_path

#
# encryption methods
#


def encrypt_files(files_path, key_path, chunks_path, enc_format, new_name=None):
    """
    encrypts .xyt files in a given directory with a given key, and splits them.
    :param files_path: str path to the directory
    :param key_path: str key's path
    :param chunks_path: str chunks's path
    :return: generates one .xyt.aes file and three chunks from it.
    """
    list_files = os.listdir(files_path)
    for xytfile in list_files:
        if xytfile.rfind('.xyt') > 1:  # while the file has .xyt format
            subprocess.call([binary, '-e', '-k', key_path, files_path+xytfile])  # encrypt .xyt file './aescrypt_32'
            if new_name:  # tenemos un nombre que darle, registro
                name = new_name
            else:  # dejar el mismo nombre que trae la imagen, para subir gran cantidad de datos
                name = xytfile.rstrip('.xyt')
            name += '-'  # name's format for the chunks
            subprocess.call(['split', '-n', '3', files_path + xytfile + enc_format, chunks_path+name,
                             '--numeric-suffixes=2'])  # split the file in chunks (no deja en el mismo dir)
    # move the chunks back to the given path
    """
    list_files = os.listdir(split_path)  # split_path -> current working path, where chunks are generated
    for chunks in list_files:
        if chunks.rfind('-0') > -1:
            #print chunks
            print subprocess.call(['mv', '-f', split_path+chunks, chunks_path+chunks])
    #"""


def encrypt_chunks_tar(chunks_path, key_path, suffix):
    """
    encrypts files (chunks of a file/s) in a given directory with a given key
    :param chunks_path: str directory's path
    :param key_path: str key's path
    :return: None
    """
    listFiles = os.listdir(chunks_path)
    #suffix = '-0'  # needed suffix for the files to be processed
    for chunks_file in listFiles:
        if chunks_file.rfind(suffix) > 1:  # while the file has the suffix and it is not in the first position
            subprocess.call([binary, '-e', '-k', key_path, chunks_path+chunks_file])  # './aescrypt_32'


#
# decryption methods
#


def decrypt_chunks(files_path, key_path_chunk, enc_format, dst_path=None):
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
        if aes_file.rfind(enc_format) > -1:  # while a file has the format .aes, decrypt it
            subprocess.call([binary, '-d', '-k', key_path_chunk, dst_path+aes_file])  # './aescrypt_32'

    subprocess.call('rm -f {0}*{1}'.format(files_path, enc_format), shell=True)
    # remove all .aes files from files_path, for test in case same folder


def decrypt_chunks_parallel(files_path, key_path_chunk, enc_format, dst_path=None):
    """
    decrypts chunk files from given path to given directory/ies
    :param files_path: str source path
    :param key_path_chunk: str key's path
    :param dst_path: str destiny file path
    :return: None
    """
    if dst_path is None:
        dst_path = files_path
    list_files = os.listdir(files_path)

    pool = Pool(processes=30,)  # 30
    multiple_results = [pool.apply_async(__aux_wrapper_decrypt_chunks, (aes_file, key_path_chunk, dst_path))
                        for aes_file in list_files if aes_file.rfind(enc_format) > -1]
    for res in multiple_results:
        res.get()  # timeout=3
    subprocess.call('rm -f {0}*{1}'.format(files_path, enc_format), shell=True)
    # remove all .aes files from files_path, for test in case same folder


def decrypt_to_file(files_path, key_path, enc_format, dst_path=None):
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
        __aux_decrypt_file(chunk, files_path, dst_path, key_path, enc_format)


def decrypt_to_file_parallel(files_path, key_path, enc_format, dst_path=None):
    """
    decrypts and merges chunks from given path to given directory with a given key. Multiprocess function
    :param files_path: str chunks source path
    :param key_path: str key's path
    :param dst_path: str destiny path
    :return: None
    """
    if dst_path is None:
        dst_path = str(files_path)

    list_files = __get_files_names(files_path, '-')  # lists the names of all the chunk files with '-' -> f0150_10-0

    pool = Pool(processes=30,)
    multiple_results = [pool.apply_async(__aux_decrypt_file, (chunk, files_path, dst_path, key_path, enc_format))
                        for chunk in list_files]

    for res in multiple_results:
        res.get()  # timeout=3

