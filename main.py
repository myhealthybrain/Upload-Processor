import os
import time
import sys
import subprocess
import zipfile
import pprint

path_to_watch = "/Processing/incoming"
processing_in_folder = "/Processing/pending"

before = dict ([(f,None) for f in os.listdir (path_to_watch)])

# Set up PID file for watcher process to check
pid = str(os.getpid())
pidfile = "/tmp/filecopier.pid"
if os.path.isfile(pidfile):
    os.unlink(pidfile)

file(pidfile,'w').write(pid)
print "Wrote pid: ", pid, " to PID file at ",pidfile


def ensureDir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        print "Creating folder:  "+f
        os.makedirs(d)

def unzipFileIntoDir(file,dir):
#    os.mkdirs(dir,0777)
    zfobj = zipfile.ZipFile(file)
    for name in zfobj.namelist():
        if name.endswith('/'):
            os.mkdirs(os.path.join(dir,name))
        else:
            outfile = open(os.path.join(dir,name),'wb')
            outfile.write(zfobj.read(name))
            outfile.close()

def getFolderSize(path):
    total_size = 0
    for dirpath,dirnames,filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath,f)
            total_size += os.path.getsize(fp)
            print total_size
    return total_size

def processFolder(path,folder):
    full_path = path+"/"+folder

    # If this is a newly processed folder, don't do anything.
    if full_path.find('processed_') != -1:
        return;

    folder_size = getFolderSize(full_path)

    # Wait for upload to complete -- we check on the
    # upload every 10 seconds and compare file sizes
    # until the file size is the same.

    while 1:
        time.sleep(10)
        new_folder_size = getFolderSize(full_path)
        if (new_folder_size == folder_size & new_folder_size != 0):
            break
        else:
            folder_size = new_folder_size

    # Unzip the files
    for f in os.listdir(path+"/"+folder):
        if folder.find('processed_') != -1:
            continue;

        filepath = path+"/"+folder+"/"+f
        if not os.path.isdir(filepath):
            filename,extension = os.path.splitext(filepath)
            if extension == ".zip":
                print "Unzipping "+filepath
                filename_array = folder.split("_")
                pprint.pprint(filename_array)
                client_id = filename_array[3]
                to_folder = processing_in_folder+'/'+client_id+'/in/'
                ensureDir(to_folder)
                unzipFileIntoDir(filepath,to_folder)
                os.rename(path+"/"+folder, path+"/processed_"+folder)




while 1:
    time.sleep(2)
    after = dict ([(f,None) for f in os.listdir(path_to_watch)])
    added = [f for f in after if not f in before]
    if added:
        for f in added:
            processFolder(path_to_watch,f)
    before = after