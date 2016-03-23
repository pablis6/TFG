import subprocess as sub
import apidropbox as drop
import encryption as enc

# takes xyt files from a given path and crypts-splits-crypts and uploads them
# to a given dropbox's paths.

source_path = './test_scripts/source/'
dst_chunks = './test_scripts/upload_chunks/'

dst_chunks_1 = './test_scripts/upload_chunks/chunk1/'
dst_chunks_2 = './test_scripts/upload_chunks/chunk2/'
dst_chunks_3 = './test_scripts/upload_chunks/chunk3/'

dropbox_path_1 = '/pin0000-1/'
dropbox_path_2 = '/pin0000-2/'
dropbox_path_3 = '/pin0000-3/'

# encrypts the chunks
enc.encrypt_files(source_path, enc.key_path_1, dst_chunks)
enc.encrypt_chunks(dst_chunks, enc.key_path_2)

# move chunks 02-> chunk1, 03-> chunk2, 04-> chunk3
# relative path from where the script is launch
sub.call('mv ./test_scripts/upload_chunks/*-02.aes ./test_scripts/upload_chunks/chunk1', shell=True)
sub.call('mv ./test_scripts/upload_chunks/*-03.aes ./test_scripts/upload_chunks/chunk2', shell=True)
sub.call('mv ./test_scripts/upload_chunks/*-04.aes ./test_scripts/upload_chunks/chunk3', shell=True)

# upload files to dropbox
drop.upload_files(dst_chunks_1, dropbox_path_1)
drop.upload_files(dst_chunks_2, dropbox_path_2)
drop.upload_files(dst_chunks_3, dropbox_path_3)
