#!/usr/bin/python

import os
import sys
from os.path import join, isfile, abspath, getsize
import hashlib

def characterize_file(dir, filename):
	'''Retrieve identifying characteristics of the filename

	These include, in this instance, the
	- filename
	- size
	- hash of contents

	We ignore modification times or owner as these are probably not what we're looking for.

	:param dir: The directory containing the filename
	:type dir: str
	:param filename: The filename
	:type filename: str

	:return: A tuple containing the characteristics
	:raise: 
	'''
	path = abspath(join(dir, filename))
	size = getsize(path)
	hasher = hashlib.sha1()
	hasher.update(open(path, 'rb').read())
	chash = hasher.hexdigest()
	c = (filename, size, chash)
	return c

def dir_contents(dir):
	'''Generate a mapping of directory paths to sets of contents. The set of contents
	is a set of tuples, one for each file, that characterize the file.

	:parm dir: The directory to walk
	:type dir: str

	:return: A dict of directory paths mapped to a set of file characterizations for the contents
		of that directory
	:throws:
	'''
	dc = {}
	for pth, dirs, files in os.walk(dir):
		# add to a set using a comprehension. We need to check if files actually exist
		# - the directory I was testing on had some broken links.
		f = {characterize_file(pth, i) for i in files if isfile(abspath(join(pth, i)))}
		dc[pth] =  f
	return dc

def match_directories(root):
	'''Returns pairs of directories that have > 75% identical content.

	:param root: The root directory
	:type root: str
	:returns: A list of pairs of matching paths
	'''
	d = dir_contents(root)
	# we could iterate with for k in d:  but we want to be smart about the inner loop, so the outer
	# list of keys must be sliceable.
	ret = []
	dk = d.keys()
	for i in range(len(dk)):
		k = dk[i]
		# The solution is n^2. But we can cut it in half, and remove a==b, b==a duplicates, by starting
		# the inner loop at one ahead of the outer loop position.
		for j in dk[i+1:]:
			# get the intersection of the two directory contents
			u = d[k] & d[j]
			# Question: How do we define '75% duplicate content'?
			# how about if the number of duplicate items is greater than 75% of the size of the smallest dir. 
			if len(u) > .75*min(len(d[k]), len(d[j])):
				ret.append((k, j))
				# note, we could turn this into a generator here with yeild. Would enable lazy evaluation.
	return ret

print match_directories(sys.argv[1])
