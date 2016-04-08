from multiprocessing import Pool, Process
import os
import subprocess as sub
import operator
import linecache
import Queue as q_exception  # since queue exceptions are not available in the multiprocessing module
import logging
import apidropbox as drop
import encryption as enc
import time

dropbox_path_1 = '/pin0000-1'
dropbox_path_2 = '/pin0000-2'
dropbox_path_3 = '/pin0000-3'


def download_chunks(local_path, download_q):


    try:
        p1 = Process(target=drop.retrieve_folder_parallel, args=(dropbox_path_1, local_path))  # local_path
        p1.start()
        p2 = Process(target=drop.retrieve_folder_parallel, args=(dropbox_path_2, local_path))  # local_path
        p2.start()
        p3 = Process(target=drop.retrieve_folder_parallel, args=(dropbox_path_3, local_path))  # local_path
        p3.start()

        p1.join()
        p2.join()
        p3.join()
        #logging.error('esto es otra prueba_2 ')
        # decrypt
        enc.decrypt_chunks_parallel(local_path, enc.key_path_2)
        enc.decrypt_to_file_parallel(local_path, enc.key_path_1)
        # built the file
        files = os.listdir(local_path)  # lista los ficheros, 'docker/local_path/'
        files = ['{0}{1}\n'.format(local_path, i) for i in files]  # add the path to the files (relative to .py)
        # configures the listXyt.lis which is used by bozorth
        # open mind the mode
        with open('{0}listXyt.lis'.format(local_path), 'w') as f:  # fix path, writes path's files to listXyt.lis
            for path in files:
                f.write(path)
            f.close()

    except (OSError, IOError) as e:
        logging.error('error ')
        download_q.put(1)
    else:
        download_q.put('download_done')


def extract_mindtct(source_path, extract_q):

    try:
        name = source_path[source_path.rfind('docker'):source_path.rfind('.')]  # docker, relative to .py caller
        #logging.error('esto es una prueba ')
        cmd = 'docker/mindtct -b {0} {1}'.format(source_path, name)
        os.system(cmd)
        os.remove(source_path)  # removes the image
    except OSError as e:
        logging.error('error')
        extract_q.put(1)
    else:
        extract_q.put('extract_done')


def compare(source_path, local_path, read_q, q_timeout):

    try:
        extract = read_q.get(timeout=q_timeout)
        download = read_q.get(timeout=q_timeout)
    except q_exception.Empty:
        logging.error('error sync time')
        # borra cosas...
    else:
        if extract != 1 and download != 1:
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
                #mide = time.time()
                line = line[line.rfind('/')+1:line.rfind('.')]
                #print time.time() - mide
                print 'the match with : {0}'.format(line)  # the result, name of the greates one
        else:
            #print ' delete files as well'
            logging.error('timeout, no response')







#local_path = './local_path/'
#local_path = './docker/local_path/'
#local_path = 'docker/local_path/'  # local_path == f_path it is the work path ...

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
