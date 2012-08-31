import unittest
import peoplebrowsr1
'''
Run with python -m unittest discover
'''

class TestPeopleBrowsr1(unittest.TestCase):

    def test_characterization(self):
        c = peoplebrowsr1.characterize_file('.', 'lorem')
        self.assertEquals(c, ('lorem', 3146L, '1d3bab195e8a64d1cc3c09926a550351def29df0'))

    def test_dirmatch(self):
    	dat = {
    	'tdir/b': set([('lorem', 3146L, '1d3bab195e8a64d1cc3c09926a550351def29df0')]), 
    	'tdir/c': set([('tobe', 1490L, 'addc95b42636c14ea8b888b2ad63eaf2ebbfe2ed')]), 
    	'tdir/a': set([('lorem', 3146L, '1d3bab195e8a64d1cc3c09926a550351def29df0'), ('tobe', 1490L, 'addc95b42636c14ea8b888b2ad63eaf2ebbfe2ed')]), 
    	'tdir': set([])}

    	d = peoplebrowsr1.dir_contents('tdir')
    	self.assertEquals(dat, d)

    def test_dirlist(self):
    	dat = [('tdir/b', 'tdir/a'), ('tdir/c', 'tdir/a')]
    	d = peoplebrowsr1.match_directories('tdir')
    	self.assertEquals(dat, d)
