import sys
import gzip
import os
import re
import hashlib
import log_formats
import shutil
import Levenshtein

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def __knext(iterat, k):
	result = []
	for i,item in enumerate(iterat):
		if i+1 > k: break
		result.append( item )
	return result


class FileBasedLogExtractor(object):
	def log_iterator(self):
		for l in self.fd:
			yield l

class BasicLogExtractor(FileBasedLogExtractor):
	def __init__(self, filepath):
		self.fd = open( filepath )

class GzipLogExtractor(FileBasedLogExtractor):
	def __init__(self, filepath):
		import gzip
		self.fd = gzip.open( filepath )



class LogTokenizer(object):
	def __init__(self, log_format, log_file):
		if log_file.endswith(".gz"):
			self.log_provider = GzipLogExtractor(log_file)
		else:
			self.log_provider = BasicLogExtractor(log_file)
		self.token_extractor = getattr(log_formats, log_format)

	def iter_tokens(self):
		for next_line in self.log_provider.log_iterator():
			try:
				next_line_tokens = self.token_extractor(next_line)
			except AttributeError, e:
				# print next_line
				continue
			yield next_line_tokens



class BucketsStoreOnDisk(object):#TODO: make a proper class hierarchy ;)
	def __init__(self, working_dir=".working", exact_fields=None, fuzzy_fields=None):
		self.working_dir = working_dir
		if os.path.exists( working_dir ): shutil.rmtree( working_dir )#TODO: maybe ask the user beforehand ?
		os.makedirs(working_dir)

		self.bucket_files = dict()
		self.fuzzy_fields = fuzzy_fields[:]
		self.exact_fields = exact_fields[:]
		self.hash_dict = dict()

	def _hashit(self, strng):
		#todo: don't hash small values and only strings containing problematic OS/fs characters
		if strng not in self.hash_dict:
			m = hashlib.md5()
			m.update(strng)
			h = m.hexdigest()
			self.hash_dict[strng] = h
		return self.hash_dict[strng]

	def to_bucket( self, tokens ):
		dest = os.path.join( self.working_dir, "".join( self._hashit( tokens[k] ) for k in self.exact_fields ))

		if dest not in self.bucket_files:
			if not os.path.exists( dest ):
				outf = open( dest, 'w' )
				outf.write( "\t".join( [tokens[x] for x in self.exact_fields] ) + '\n' )
			else: outf = open( dest, 'a' )
			self.bucket_files[dest] = outf
		to_dump = "\t".join( [tokens[x] for x in self.fuzzy_fields] )
		self.bucket_files[dest].write(to_dump + '\n')
		if len(self.bucket_files) > 500:#TODO: must know how much higher it can be set, use a priority queue
			dest, fd = self.bucket_files.popitem()#TODO: isnt this dangerous?
			fd.close()

	def close(self):
		for dest, fd in self.bucket_files.iteritems():
			fd.close()



class OnDiskFuzzySummarizer(object):
	def __init__(self, filepath):
		self.fd = open(filepath, "r")
		self.header_line = self.fd.readline().rstrip().split("\n")

	@staticmethod
	def _multifield_ratio( fields_x1, fields_x2, field_weights ):
		the_ratio = 0.0
		for i, f1 in enumerate(fields_x1):
			the_ratio += Levenshtein.ratio(f1, fields_x2[i]) * field_weights[ i ]
		return the_ratio / sum(field_weights)

	def fuzzymatch(self, similarity_threshold=0.81, field_weights=[100]):
		unique_lines = {tuple(x.rstrip().split('\t')):True for x in self.fd}
		initial_size = len(unique_lines)
		all_pairs = []
		for i1, l1 in enumerate(unique_lines):
			for i2, l2 in enumerate(unique_lines):
				if i2 >= i1: continue
				all_pairs.append( ( OnDiskFuzzySummarizer._multifield_ratio(l1, l2, field_weights), l1, l2 ) )
		all_pairs.sort()
		all_pairs.reverse()

		for best_ratio, l1, l2 in all_pairs:
			if best_ratio >= similarity_threshold:
				# logging.debug("".join(l1) + '<-->' + "".join(l2))
				unique_lines[l2] = False#chooses to eliminate l2
		return initial_size, (x for x in unique_lines if unique_lines[x])