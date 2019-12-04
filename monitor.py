import os
import hashlib
from queue import Queue
from threading import Thread,activeCount

def real_path(path):
	dirs = list()
	files = list()
	for parent,dirnames,filenames in os.walk(path):
		for _ in dirnames:
			dir = os.path.join(parent,_)
			dirs.append(dir)
		for _ in filenames:
			filename = os.path.join(parent,_)
			files.append(filename)
	return [dirs,files]

def file_md5(file):
	global files_md5
	try:
		md5 = hashlib.md5(open(file,'rb').read()).hexdigest() 
		if file not in files_md5.keys():
			files_md5 = dict({file:md5},**files_md5)
	except FileNotFoundError:
		return

def file_create(file):
	if file not in files and file not in copy_files:
		print('\033[1;36m[+]file has been create：{}\033[0m'.format(file))
		copy_files.append(file)
		files.append(file)

def file_delete(walk_path):
	for file in copy_files:
		if file not in walk_path:
			print('\033[1;31m[+]file has been delete：{}\033[0m'.format(file))
			copy_files.remove(file)


def file_change(file):
	try:
		md5 = hashlib.md5(open(file,'rb').read()).hexdigest() 
	except FileNotFoundError:
		return
	try:
		if files_md5[file] != md5:
			print('\033[1;34m[+]file has been change：{}\033[0m'.format(file))
			files_md5[file] = md5
	except KeyError:
		return
def dir_create(dir_name):
	if dir_name not in dirs and dir_name not in copy_dirs:
		print('\033[1;35m[+]dir has create：{}\033[0m'.format(dir_name))
		copy_dirs.append(dir_name)


if __name__ == '__main__':
	path = input('\033[1;36m[+]Input the path you want to moniter：\033[0m')
	if not os.path.exists(path):
		print('\033[1;31mPath not exists,please input a real path\033[0m')
		os._exit(0)
	if not os.path.isdir(path):
		print('\033[1;31mPlease input a path not another\033[0m')
		os._exit(0)
	queue_md5 = Queue()
	dirs,files = real_path(path)
	copy_files = files[:]
	copy_dirs = dirs[:]
	files_md5 = {}
	for file in files:
		queue_md5.put(file)
	while queue_md5.qsize()>0:
		if activeCount()<=10:
			Thread(target=file_md5,args=(queue_md5.get(),)).start()
	print('\033[1;36m[+]初始文件md5获取完成\033[0m')
	#print(files_md5)
	while True:
		for file in files:
			queue_md5.put(file)
		while queue_md5.qsize()>0:
			if activeCount()<=10:
				Thread(target=file_md5,args=(queue_md5.get(),)).start()
		filename_ = list()
		for parent,dirnames,filenames in os.walk(path):
			for _ in dirnames:
				dir_create(os.path.join(parent,_))
			for _ in filenames:
				file_create(os.path.join(parent,_))
				file_change(os.path.join(parent,_))
				filename_.append(os.path.join(parent,_))
		file_delete(filename_)

