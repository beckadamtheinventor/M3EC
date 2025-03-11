import os, sys
from _m3ec.util import *

if __name__=='__main__':
	if len(sys.argv) < 3:
		print(f"Usage: {sys.argv[0]} template data.m3ec [output]")
		exit(0)
	
	try:
		d = readDictFile(sys.argv[2])
	except Exception as e:
		print(f"Exception: {str(e)}")
		exit(1)
	
	try:
		data = readf_file(sys.argv[1], d)
	except Exception as e:
		print(f"Exception: {str(e)}")
		exit(1)

	if len(sys.argv) >= 4:
		try:
			with open(sys.argv[3], "w") as f:
				f.write(data)
		except Exception as e:
			print(f"Exception: {str(e)}")
			exit(1)
	else:
		print(data)
