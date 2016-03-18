import dropbox
import os
from multiprocessing import Pool, TimeoutError

# local paths to work (Test)
local_path1 = '/home/rnov/tfg/dropboxApi/xytFiles'
local_path2 = '/home/rnov/tfg/dropboxApi/xytFiles2/'
local_path3 = '/home/rnov/tfg/dropboxApi/xytFiles3/'

# make a connection to dropBox. OAuth flow authentication
dbx = dropbox.dropbox.Dropbox('rrFPgdcaJP8AAAAAAAAAHbe0eiQ3StEF2OGqWTp1DM90UeAXMEzMyZCBLlOezKbs')

# writeMode for file/folder
overwrite = dropbox.files.WriteMode('overwrite')


def upload_file(local_path, dropbox_path):
    """
    uploads single file from a given local path to given dropbox path
    :param local_path: str source path
    :param dropbox_path: destiny dropbox path
    :return:
    """
    try:
        dbx.files_upload(local_path, dropbox_path, overwrite)  # dropbox_path = /xytFiles/
        local_path.close()
    except dropbox.exceptions.ApiError:
        print 'failed uploading files'


def upload_files(local_path, dropbox_path):
    """
    upload files from given local path to given dropbox path
    :param local_path: str local source path whose files will be uploaded
    :param dropbox_path: str dropbox's path where the file will be uploaded
    :return:
    """
    try:
        listFiles = os.listdir(local_path)
        for xytfile in listFiles:
            fingptr = open(local_path+'/{0}'.format(xytfile))
            dbx.files_upload(fingptr, dropbox_path+xytfile, overwrite)  # dropbox_path = /xytFiles/
            fingptr.close()
    except dropbox.exceptions.ApiError:
        print 'failed uploading files'
    except IOError as e:
        print 'Unable to open file {0}: {1}'.format(e.errno, e.strerror)


def delete_content(dropbox_path):
    """
    deletes given file/folder from dropbox
    :param dropbox_path: str dropbox's (file/folder) path
    :return:
    """
    try:
        dbx.files_delete(dropbox_path)
    except dropbox.exceptions.ApiError:
        print 'could not delete {0}'.format(dropbox_path)


def retrieve_file(dropbox_path, local_path):
    """
    download a single file
    :param local_path: str path/file.format'
    :param dropbox_path: str '/folder/file.format'
    :return:
    """
    try:
        dbx.files_download_to_file(local_path, dropbox_path)
    except dropbox.files.DownloadError:
        print 'failed to download {0}'.format(dropbox_path)


def retrieve_folder(local_path, dropbox_path):
    """
    download files from a given dropbox's folder to a given local path
    :param local_path: str path to be saved the files
    :param dropbox_path: str dropbox path
    :return:
    """
    folder = dbx.files_list_folder(dropbox_path)
    for k in folder.entries:
        retrieve_file(k.path_lower, local_path+k.name)


def retrieve_file_parallel(files_name, path_files):
    retrieve_file(path_files, local_path3+files_name)


def retrieve_folder_parallel(dropbox_path):
    """
    download files from a given dropbox's folder to a given local path. Multiprocess function
    :param dropbox_path: str dropbox path
    :return:
    """
    folder = dbx.files_list_folder(dropbox_path)
    pool = Pool(processes=15,)
    filesInfo = [(i.name, i.path_lower) for i in folder.entries]  # filesInfo: (filename, filepath)
    multiple_results = [pool.apply_async(retrieve_file_parallel, (k[0], k[1],)) for k in filesInfo]
    # print [res.get(timeout=1) for res in multiple_results]
    for res in multiple_results:
        res.get()  # timeout=3
