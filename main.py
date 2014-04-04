
import sys, os
import argparse

from PPLS import LogTokenizer, BucketsStoreOnDisk, OnDiskFuzzySummarizer


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='This is the main program for PPLS.')
	parser.add_argument('--log_format', default="weblogic_default",
	                   help='the format of the logs to summarize, see file log_formats.py for a list of possible values.')
	parser.add_argument('--logfile', default="log_samples/weblogiclog.gz",
	                   help='the (optionally gzipped) file were the logs are located')
	parser.add_argument('--fuzzy_fields', nargs='+',
	                   help='the fields to fuzz, must be a list of pairs: <field_name>,<weights>. exemple: full_url,100 req_type,50')
	parser.add_argument('--exact_fields', nargs='+',
	                   help='the fields that will be kept as is in the result')
	parser.add_argument('--working_directory', default=".working",
	                   help='the working directory where intermediate results are stored')
	parser.add_argument('--similarity_threshold', default="0.82",
	                   help='the similarity threshold used when fuzzy matching the log lines')
	parser
	#TODO: add filtering + pre/post processing of the logs
	args = parser.parse_args()

	if args.exact_fields is None or args.fuzzy_fields is None:
		print "You must specify at least one fuzzy_fields and one exact_fields. Use -h for more details."
		sys.exit(0)

	fuzzy_field_names = []
	fuzzy_field_weights = []
	for pair in args.fuzzy_fields:
		ffn,ffw = pair.split(",")
		fuzzy_field_names.append(ffn)
		fuzzy_field_weights.append(int(ffw))
	
	tokenizer = LogTokenizer(args.log_format, args.logfile)
	bucketer = BucketsStoreOnDisk( exact_fields=args.exact_fields, fuzzy_fields=fuzzy_field_names )
	for i, x in enumerate( tokenizer.iter_tokens() ):
		bucketer.to_bucket( x )
	bucketer.close()

	with open("log_summary.txt" ,"w") as outf:
		for f in os.listdir( args.working_directory ):
			disk_summarizer = OnDiskFuzzySummarizer(os.path.join(args.working_directory, f))
			intital_num_pairs, iter_final_summary = disk_summarizer.fuzzymatch(similarity_threshold=float(args.similarity_threshold), field_weights=fuzzy_field_weights)
			for line in iter_final_summary:
				outf.write("\t".join( disk_summarizer.header_line ) + "\t")
				outf.write("\t".join( line  ) + "\n")
