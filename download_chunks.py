from multiprocessing import Pool, Process
import apidropbox as drop
import encryption as enc
import time

# download the crypt chunks, decrypts and merges them into a single
# file which is decrypted as well .

dropbox_path_1 = '/pin0000-1'
dropbox_path_2 = '/pin0000-2'
dropbox_path_3 = '/pin0000-3'
local_path = './local_path/'

# note: daemonic processes can not have child (overwrite Pool class) or multiprocess process
# dropbox_as = [dropbox_path_1, dropbox_path_2, dropbox_path_3]
# pool = Pool(processes=3,)
# multiple_results = [pool.apply_async(drop.retrieve_folder_parallel, (k, local_path)) for k in dropbox_as]
# for res in multiple_results:
#        res.get()  # timeout=3


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

# drop.retrieve_folder_parallel(dropbox_path_1, local_path)  # serial
# drop.retrieve_folder_parallel(dropbox_path_2, local_path)
# drop.retrieve_folder_parallel(dropbox_path_3, local_path)

print 'decrypt chunks parallel'
chunks_time = time.time()
enc.decrypt_chunks_parallel(local_path, enc.key_path_2)
print 'chunks time: {0}'.format(time.time()-chunks_time)
print 'decrypt to file parallel'
file_time = time.time()
enc.decrypt_to_file_parallel(local_path, enc.key_path_1)
print 'file time: {0}'.format(time.time()-file_time)
print time.time() - start
