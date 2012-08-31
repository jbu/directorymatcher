#!/usr/bin/python

import os
import sys
from os.path import join, isfile, abspath, getsize
import hashlib
# http://pypi.python.org/pypi/futures
from concurrent import futures

'''
To speed up the directory matching we can:
	use better algorithms
	use the available resources more effectively.

I'm going to leave my n^2 solution alone. Of the top of my head I can't think of a better one.
So that leaves using the computer better. I'll go for some simple concurrency to allow better use of
disc bandwith and multiple processors.

In this simple scheme we have a ThreadPoolExecutor that multiplexes the 'characterization' of the directories.
We could go further and thread by individual files rather than whole directories, or break out the matching
phase into another thread, but that seems excessive for this example.
I'm sure there are other areas for concurrency that i haven't explored here.
This also assumes a single machine. Sharding to multiple machines would use similar principles - essentially
you're breaking the task into a pipeline and executing sub-tasks on available hardware. There are 
frameworks (like mapreduce) that help with this (I should probably try http://discoproject.org/). 
The idea here would be to generate a list of directories, characterize them in a mass of map tasks, and then
reduce. again with a large set of tasks that sub-divide the matching task.
'''

def characterize_files(tup):
	'''Retrieve identifying characteristics of the filename

	These include, in this instance, the
	- filename
	- size
	- hash of contents

	We ignore modification times or owner as these are probably not what we're looking for.

	:param tup: Contains (dirname, [fnames])

	:return: A tuple of the dirname and set of the characteristics
	:raise: 
	'''
	dirname, fnames = tup

	s = set()
	for fname in fnames:
		path = abspath(join(dirname, fname))
		size = getsize(path)
		hasher = hashlib.sha1()
		hasher.update(open(path, 'rb').read())
		chash = hasher.hexdigest()
		c = (fname, size, chash)
		s.add(c)
	return (dirname, s)

def dir_contents(dir):
	'''Generate a directory listing.

	:parm dir: The directory to walk
	:type dir: str

	:return: Generate (path, [files]) tuples
	:throws:
	'''
	for pth, dirs, files in os.walk(dir):
		c = (pth, [i for i in files if isfile(abspath(join(pth, i)))])
		yield c

def match_directories(root):
	'''Returns pairs of directories that have > 75% identical content.

	:param root: The root directory
	:type root: str
	:param ex: an executor
	:returns: A list of pairs of matching paths
	'''
	done = []
	ret = []
	with futures.ThreadPoolExecutor(max_workers=2) as ex:
		l = ex.map(characterize_files, dir_contents(root))
		for i in l:
			for d in done:
				u = d[1] & i[1]
				# Question: How do we define '75% duplicate content'?
				# how about if the number of duplicate items is greater than 75% of the size of the smallest dir. 
				if len(u) > .75*min(len(d[1]), len(i[1])):
					ret.append((d[0], i[0]))	
			done.append(i)
	return ret

print match_directories(sys.argv[1])