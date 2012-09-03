#!/usr/bin/python

import os
import sys
from os.path import join, isfile, abspath, getsize
import hashlib
import itertools
from collections import Counter, defaultdict

'''In this version we use a reverse map to index files to paths that contain them.
This enables us to search for matching directories in n*m instead of n^2 where m is
the average number of files in a directory.

I've also gone all functional on it and used lots of iterators. This would make 
concurrency easier to express.
'''

def characterize_files(dir, files):

	for filename in files:
		path = abspath(join(dir, filename))
		size = getsize(path)
		hasher = hashlib.sha1()
		hasher.update(open(path, 'rb').read())
		chash = hasher.hexdigest()
		c = (dir, (filename, size, chash))
		yield c

def build_revmap(revmap, cfiles):
	for c in cfiles:
		dir, ctuple = c
		revmap[ctuple].add(dir)
		yield c

def build_forwardmap(fmap, cfiles):
	for c in cfiles:
		dir, ctuple = c
		fmap[dir].add(ctuple)
		#yield c #this is at the end of the chain, so it can just consume.

#forward map will be a dict mapping paths to sets of contained (characterized) files
forwardmap = defaultdict(set)

#revmap maps (characterized) files to paths
revmap = defaultdict(set)

chain = (i for i in os.walk(sys.argv[1]))
chain = itertools.chain.from_iterable(characterize_files(i[0], i[2]) for i in chain)
chain = (build_revmap(revmap, chain))
build_forwardmap(forwardmap, chain)

for pth, files in forwardmap.iteritems():
	# for each path, use revmap to count the paths that contain that file.
	cnter = Counter()
	for f in files:
		cnter.update(revmap[f])
	# emit any paths that contain more than 75% identical content.
	# again, 75% identical is taken to mean that the target dir has more than 75% of the
	# content of this directory
	for k, cnt in cnter.items():
		if pth != k:
			if cnt > .75*len(files):
				print pth, k
