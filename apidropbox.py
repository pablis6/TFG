import dropbox
import os
from multiprocessing import Pool, TimeoutError

# local paths (Test)
local_path1 = '/home/rnov/tfg/dropboxApi/xytFiles'
local_path2 = '/home/rnov/tfg/dropboxApi/local_path/'

# make a connection to dropBox. OAuth flow authentication
dbx = dropbox.dropbox.Dropbox('rrFPgdcaJP8AAAAAAAAAHbe0eiQ3StEF2OGqWTp1DM90UeAXMEzMyZCBLlOezKbs')

# writeMode for file/folder
overwrite = dropbox.files.WriteMode('overwrite')


def upload_file(local_path, dropbox_path):
    """
    uploads single file from a given local path to given dropbox path
    :param local_path: str source path
    :param dropbox_path: destiny dropbox path
    :return: None
    """
    try:
        dbx.files_upload(local_path, dropbox_path, overwrite)  # dropbox_path = /xytFiles/
        local_path.close()
    except dropbox.exceptions.ApiError:
        print 'failed uploading files'


def upload_files(local_path, dropbox_path):
    """
    uploads files from given local path to given dropbox path
    :param local_path: str local source path whose files will be uploaded
    :param dropbox_path: str dropbox's path where the file will be uploaded
    :return: None
    """
    try:
        listFiles = os.listdir(local_path)
        for xytfile in listFiles:
            fingptr = open(local_path+'{0}'.format(xytfile))
            print fingptr
            dbx.files_upload(fingptr, dropbox_path+xytfile, overwrite)  # dropbox_path = /xytFiles/
            fingptr.close()
    except dropbox.exceptions.ApiError:
        print 'failed uploading files'
    except IOError as e:
        print 'Unable to open file {0}: {1}'.format(e.errno, e.strerror)


def aux_upload_parallel(xytfile, local_path, dropbox_path):
    """
    auxiliary function that helps upload_files_parallel() function to upload files in each process
    :param xytfile: file name
    :param local_path: str local source path whose files will be uploaded
    :param dropbox_path: str dropbox's path where the file will be uploaded
    :return: None
    """
    try:
        fingptr = open(local_path+'{0}'.format(xytfile))
        dbx.files_upload(fingptr, dropbox_path, overwrite)  # dropbox_path = /xytFiles/name.xyt
        fingptr.close()
    except IOError as e:
        print 'Unable to open file {0}: {1}'.format(e.errno, e.strerror)
    except dropbox.exceptions.ApiError:
        print 'failed uploading files'


def upload_files_parallel(local_path, dropbox_path, num_processes=20):
    """
    uploads files from given local path to given dropbox path. Multiprocess function
    :param local_path: str local source path whose files will be uploaded
    :param dropbox_path: str dropbox's path where the file will be uploaded
    :param num_processes: number of processes to be launched
    :return: None
    """
    pool = Pool(processes=num_processes)
    list_files = os.listdir(local_path)  # file's names in the given path
    multiple_results = [pool.apply_async(aux_upload_parallel, (xyt_name, local_path, dropbox_path+xyt_name))
                        for xyt_name in list_files]
    #print multiple_results
    for res in multiple_results:
        res.get()  # timeout=3


def delete_content(dropbox_path):
    """
    deletes given file/folder from dropbox
    :param dropbox_path: str dropbox's (file/folder) path
    :return: None
    """
    try:
        dbx.files_delete(dropbox_path)
    except dropbox.exceptions.ApiError:
        print 'could not delete {0}'.format(dropbox_path)


def retrieve_file(dropbox_path, local_path):
    """
    downloads a single file
    :param local_path: str path/file.format'
    :param dropbox_path: str '/folder/file.format'
    :return: None
    """
    try:
        dbx.files_download_to_file(local_path, dropbox_path)
    except dropbox.files.DownloadError:
        print 'failed to download {0}'.format(dropbox_path)


def retrieve_folder(local_path, dropbox_path):
    """
    downloads files from a given dropbox's folder to a given local path
    :param local_path: str path to be saved the files
    :param dropbox_path: str dropbox path
    :return: None
    """
    folder = dbx.files_list_folder(dropbox_path)
    for k in folder.entries:
        retrieve_file(k.path_lower, local_path+k.name)


def retrieve_folder_parallel(dropbox_path, local_path, num_processes=15):
    """
    downloads files from given dropbox's folder to a given local path. Multiprocess function
    :param dropbox_path: str dropbox path
    :param local_path: str
    :param num_processes int
    :return: None
    """
    folder = dbx.files_list_folder(dropbox_path)
    pool = Pool(processes=num_processes,)
    files_info = [(i.name, i.path_lower) for i in folder.entries]  # filesInfo: (filename, filepath)
    #  print files_info
    multiple_results = [pool.apply_async(retrieve_file, (k[1], local_path+k[0])) for k in files_info]
    # print [res.get(timeout=1) for res in multiple_results]
    for res in multiple_results:
        res.get()  # timeout=3
