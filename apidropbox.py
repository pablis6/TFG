import os
from multiprocessing import Pool, TimeoutError
import logging
import dropbox

print 'apidropbox : {0}'.format(os.getcwd())  # getting the working path, just for test

# writeMode for file/folder
overwrite = dropbox.files.WriteMode('overwrite')

#
# private aux. methods
#


def __aux_upload_parallel(xytfile, local_path, dropbox_path, dbx):
    """
    auxiliary function that helps upload_files_parallel() function to upload files in each process
    :param xytfile: str file name
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
        logging.error('failed uploading files')

#
# upload methods (single & multiprocess)
#


def upload_file(local_path, dropbox_path, OAuth_token):
    """
    uploads single file from a given local path to given remote one (dropbox), files up to 150 MB
    :param local_path: str path to the file which will be uploaded
    :param dropbox_path: str destiny remote path
    :param OAuth_token: str authentication token needed to establish a remote connection
    :return: None
    """
    dbx = dropbox.dropbox.Dropbox(OAuth_token)
    try:
        file_name = os.path.basename(local_path)  # gets the name of the file to be uploaded
        fingptr_obj = open(local_path)  # open the file as an object
        dbx.files_upload(fingptr_obj, dropbox_path+file_name, overwrite)  # dropbox_path = /xytFiles/
        fingptr_obj.close()  # close the file
    except dropbox.exceptions.ApiError:
        logging.error('failed uploading files')


def upload_files(local_path, dropbox_path, OAuth_token):
    """
    uploads files from given local path to given remote one (dropbox), files up to 150 MB each
    :param local_path: str local source path whose files will be uploaded
    :param dropbox_path: str dropbox's path where the file will be uploaded
    :param OAuth_token: str authentication token needed to establish a remote connection
    :return: None
    """
    dbx = dropbox.dropbox.Dropbox(OAuth_token)
    try:
        listFiles = os.listdir(local_path)
        for xytfile in listFiles:
            fingptr = open(local_path+'{0}'.format(xytfile))
            dbx.files_upload(fingptr, dropbox_path+xytfile, overwrite)  # dropbox_path = /xytFiles/
            fingptr.close()
    except dropbox.exceptions.ApiError:
        logging.error('failed uploading files')
    except IOError as e:
        logging.error('Unable to open file {0}: {1}'.format(e.errno, e.strerror))


def upload_files_parallel(local_path, dropbox_path, OAuth_token, num_processes=20):
    """
    uploads files from given local path to given remote one (dropbox). Multiprocess function
    :param local_path: str local source path whose files will be uploaded
    :param dropbox_path: str dropbox's path where the file will be uploaded
    :param OAuth_token: str authentication token needed to establish a remote connection
    :param num_processes: int number of parallel process launched simultaneously
            each process makes a connection and uploads a single data object at a time.
    :return: None
    """
    dbx = dropbox.dropbox.Dropbox(OAuth_token)
    pool = Pool(processes=num_processes)
    list_files = os.listdir(local_path)  # file's names in the given path
    multiple_results = [pool.apply_async(__aux_upload_parallel, (xyt_name, local_path, dropbox_path+xyt_name, dbx))
                        for xyt_name in list_files]
    for res in multiple_results:
        res.get()  # timeout=3

#
# download methods (single & multiprocess)
#


def retrieve_file(dropbox_path, local_path, OAuth_token):
    """
    downloads a single file from a given remote path(dropbox) to a local one.
    :param local_path: str local path where the file will be saved, path/file.format'
    :param dropbox_path: str path(remote) to the data '/folder/file.format'
    :param OAuth_token: str authentication token needed to establish a remote connection
    :return: None
    """
    dbx = dropbox.dropbox.Dropbox(OAuth_token)
    try:
        dbx.files_download_to_file(local_path, dropbox_path)
    except dropbox.files.DownloadError:
        logging.error('failed to download {0}'.format(dropbox_path))


def retrieve_folder(local_path, dropbox_path, OAuth_token):
    """
    downloads files from a given dropbox's folder to a given local path
    :param local_path: str path to be saved the files
    :param dropbox_path: str dropbox path
    :param OAuth_token: str authentication token needed to establish a remote connection
    :return: None
    """
    dbx = dropbox.dropbox.Dropbox(OAuth_token)
    folder = dbx.files_list_folder(dropbox_path)
    for k in folder.entries:
        retrieve_file(k.path_lower, local_path+k.name, OAuth_token)


def retrieve_folder_parallel(dropbox_path, local_path, OAuth_token, num_processes=15):
    """
    downloads files from given dropbox's folder to a given local path. Multiprocess function
    :param dropbox_path: str dropbox path
    :param local_path: str path
    :param OAuth_token: str authentication token needed to establish a remote connection
    :param num_processes int number of parallel process launched simultaneously
            each process makes a connection and retrieves a single data object at a time.
    :return: None
    """
    dbx = dropbox.dropbox.Dropbox(OAuth_token)
    folder = dbx.files_list_folder(dropbox_path)
    pool = Pool(processes=num_processes,)
    files_info = [(i.name, i.path_lower) for i in folder.entries]  # filesInfo: (filename, filepath)

    multiple_results = [pool.apply_async(retrieve_file, (k[1], local_path+k[0], OAuth_token)) for k in files_info]
    for res in multiple_results:
        res.get()  # timeout=3

#
# misc methods
#


def delete_content(dropbox_path, OAuth_token):
    """
    deletes given file/folder from dropbox
    :param dropbox_path: str dropbox's (file/folder) path
    :param OAuth_token: str authentication token needed to establish a remote connection
    :return: None
    """
    dbx = dropbox.dropbox.Dropbox(OAuth_token)
    try:
        dbx.files_delete(dropbox_path)
    except dropbox.exceptions.ApiError:
        logging.error('could not delete {0}'.format(dropbox_path))
