from multiprocessing import Pool, Process
import os
import subprocess as sub
import operator
import linecache
import Queue as q_exception  # since queue exceptions are not available in the multiprocessing module
import logging
import apidropbox as drop
import encryption as enc
import tarfile
import time

# chunks
dropbox_path_1 = '/pin0000-1'
dropbox_path_2 = '/pin0000-2'
dropbox_path_3 = '/pin0000-3'
# tar.gz
dropbox_path_1_dw = '/pin4444-1'  # sin slash para bajar cosas
dropbox_path_2_dw = '/pin4444-2'
dropbox_path_3_dw = '/pin4444-3'


def __buid_bozorth_lis_file(local_path, name_lis):
    """

    :param local_path:
    :param name_lis:
    :return:
    """
    # built the file
    files = os.listdir(local_path)  # lista los ficheros, 'docker/local_path/'
    files = ['{0}{1}\n'.format(local_path, i) for i in files]  # add the path to the files (relative to .py)
    # configures the listXyt.lis which is used by bozorth
    # open mind the mode
    with open('{0}/{1}.lis'.format(local_path, name_lis), 'w') as f:  # fix path, writes path's files to listXyt.lis
        for path in files:
            f.write(path)
        f.close()


def __extract_tarfile(input_filename, dst_path):
    """
    extract files ....
    :param intput_filename: str
    :param dst_path: str
    :return: none
    """
    slash = '/'
    with tarfile.open(input_filename, 'r:gz') as tar:
        ar = tar.getmembers()  # get the members withing tar.gz
        tar.extractall(path=dst_path)  # extract tar.gz in given dst_path
        tar.close()
        ar = ar.pop(0)  # name of the folder within tar.gz
        src_path = dst_path + slash + ar.name  # dst_path with folder within the tar.gz
        files = os.listdir(src_path)  # list files withing folder tar.gz

        for file_name in files:
            dst_path_2 = dst_path + slash + file_name  # dst path for files within folder
            src_path_2 = src_path + slash + file_name  # src path files within folder
            #print dst_path_2
            #print src_path_2
            os.rename(src_path_2, dst_path_2)  # move files
        os.rmdir(src_path)  # remove folder from tar.gz


def __deal_with_tar(local_path, key_tar):
    enc.decrypt_chunks_parallel(local_path, key_tar)
    files = os.listdir(local_path)
    for file_name in files:
        if file_name.rfind('.tar.gz'):
            __extract_tarfile(file_name, local_path)


def __deal_with_chunks(key_chunks, key_file):
    enc.decrypt_chunks_parallel(local_path, key_chunks)
    enc.decrypt_to_file_parallel(local_path, key_file)


def download_tar(local_path, download_q, OAuth_token, name_lis):
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
            enc.decrypt_chunks_parallel(local_path, enc.key_path_2)
            files = os.listdir(local_path)
            for file_name in files:
                if file_name.rfind('.tar.gz'):
                    __extract_tarfile(file_name, local_path)

            # borramos .tar.gz ? por al no estobar ademas al final sera borrado
            # nota el formato de tar.gz contien '-' lo que hace que lo trate aescrypt
            # cambirlo por _ -> pinxxxx_1
            enc.decrypt_to_file_parallel(local_path, enc.key_path_1)
            # build the file .lis
            __buid_bozorth_lis_file(local_path, name_lis)

        except (OSError, IOError) as e:
            logging.error('error ')
            download_q.put(1)
        else:
            download_q.put('download_done')


def download_chunks(local_path, download_q, OAuth_token, name_lis):
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
        #logging.error('esto es otra prueba_2 ')
        # decrypt
        enc.decrypt_chunks_parallel(local_path, enc.key_path_2)
        enc.decrypt_to_file_parallel(local_path, enc.key_path_1)
        # build the file .lis
        __buid_bozorth_lis_file(local_path, name_lis)

    except (OSError, IOError) as e:
        logging.error('error ')
        download_q.put(1)
    else:
        download_q.put('download_done')


def extract_mindtct(source_path, extract_q, dst_path):

    try:
        relative_path = 'docker/{0}/{0}'.format(dst_path)  # docker sobrara ya que el .py estara a la misma altura
        cmd = 'docker/mindtct_V2 -b {0} {1}'.format(source_path, relative_path)
        os.system(cmd)
        os.remove(source_path)  # removes the image
    except OSError as e:
        logging.error('fail')
        extract_q.put(1)
    else:
        extract_q.put('extract_done')


def compare(source_path, local_path, read_q, q_timeout, min_value):

    try:
        extract = read_q.get(timeout=q_timeout)
        download = read_q.get(timeout=q_timeout)
    except q_exception.Empty:
        logging.error('error sync time')
        # borra cosas...
    else:
        #if extract != 1 and download != 1:
        if (extract and download) != 1:
            try:
                results = sub.check_output(['docker/bozorth3 -p {0} -G {1}listXyt.lis '.format(source_path, local_path)]
                                           , shell=True)  # compare with bozorth
            except sub.CalledProcessError as e:
                logging.error('bozorth3 error')
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
                    print 'the match with : {0}'.format(line)  # the result, name of the greates one
        else:
            #print ' delete files as well'
            logging.error('timeout, no response')



#local_path = './local_path/'
#local_path = './docker/local_path/'
local_path = 'docker/local_path/'  # local_path == f_path it is the work path ...

def download(f_path):

    # parallel
    start = time.time()
    retrieve_time = time.time()
    p1 = Process(target=drop.retrieve_folder_parallel, args=(dropbox_path_1, local_path))
    p1.start()
    p2 = Process(target=drop.retrieve_folder_parallel, args=(dropbox_path_2, local_path))
    p2.start()
    p3 = Process(target=drop.retrieve_folder_parallel, args=(dropbox_path_3, local_path))
    p3.start()

    p1.join()
    p2.join()
    p3.join()
    print time.time() - retrieve_time

    print 'decrypt chunks parallel'
    chunks_time = time.time()
    enc.decrypt_chunks_parallel(local_path, enc.key_path_2)
    print 'chunks time: {0}'.format(time.time()-chunks_time)
    print 'decrypt to file parallel'
    file_time = time.time()
    enc.decrypt_to_file_parallel(local_path, enc.key_path_1)
    print 'file time: {0}'.format(time.time()-file_time)
    #print time.time() - start

    compare = time.time()
    files = os.listdir('./docker/local_path')  # lista los ficheros, fix path /home/rnov/tfg/dropboxApi
    files = ['./docker/local_path/{0}\n'.format(i) for i in files]  # add the path to the files (relative to .py)

    with open('docker/local_path/listXyt.lis', 'w') as f:  # fix path, writes path's files to listXyt.lis
        for path in files:
            f.write(path)
        f.close()
    ###########################
    results = sub.check_output('docker/./bozorth3 -p {0} -G ./docker/local_path/listXyt.lis '.
            format(f_path))  # > ./docker/local_path/results.txt
    print 'compare time: {0}'.format(time.time() - compare)

    # find the greates number from the comparation and its index
    res_list = map(int, results.split())  # string list to int list
    pep8 = time.time()  # ganador en tiempo indiscutible !!!!
    max_value = max(res_list)
    max_index = res_list.index(max_value)
    print 'pep8 index-max: {}'.format(time.time()-pep8)
    print 'index : {0} , value: {1} '.format(max_index, max_value)

    # seek into listxyt.lis the index+1 to get the name of the file
    getLine = time.time()
    line = linecache.getline('docker/local_path/listXyt.lis', max_index+1)  # claro ganador
    print 'linecache : {}'.format(time.time() - getLine)

    print time.time() - start


def download2(f_path):
    #files = os.listdir('docker/local_path/')
    #print files
    out = sub.check_output('docker/./bozorth3 -p {0} -G docker/local_path/listXyt.lis '.
            format(f_path), shell=True)  # > ./docker/local_path/results.txt
    #print out.__doc__
    lista = map(int, out.split())  # string list to int list
    #print lista.__doc__
    print lista

    pep8 = time.time()  # ganador en tiempo indiscutible !!!!
    max_value = max(lista)
    max_index = lista.index(max_value)
    print 'pep8 index-max: {}'.format(time.time()- pep8)
    print 'index : {0} , value: {1} '.format(max_index, max_value)

    exe_time = time.time()
    index, value = max(enumerate(lista), key=operator.itemgetter(1))
    print 'exec_time index-max: {}'.format(time.time()- exe_time)
    print 'index : {0} , value: {1} '.format(index, value)

    """
    pep8 index-max: 1.31130218506e-05
    index : 20 , value: 736
    exec_time index-max: 5.19752502441e-05
    index : 20 , value: 736
    """

    getLine = time.time()
    line = linecache.getline('docker/local_path/listXyt.lis', index+1)  # claro ganador
    print 'linecache : {}'.format(time.time() - getLine)
    print line

    """
    getLine2 = time.time()
    line2 = sub.check_call('sed -n {0}p ./docker/local_path/listXyt.lis'.format(index+1), shell=True)
    print 'time sed : {}'.format(time.time() - getLine2)
    """
    """
    linecache : 0.000144958496094
    ./docker/local_path/f0003_10.xyt
    ./docker/local_path/f0003_10.xyt
    time sed : 0.00767111778259
    """

    # > /local_path/results.txt
