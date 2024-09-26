
import os, sys, json
from _m3ec.actions import *
from _m3ec.util import *

if __name__=='__main__':
	if len(sys.argv) > 1:
		md = {
			"project_path": os.path.dirname(__file__),
			"build_path": os.path.dirname(__file__),
			"source_path": os.path.join(os.path.dirname(__file__), "data"),
		}
		for fname in sys.argv[1:]:
			try:
				with open(fname) as f:
					execActions(json.load(f), md)
			except Exception as e:
				print(f"Error executing actions file \"{fname}\":\n{str(e)}")
	else:
		print(f"Usage: {sys.argv[0]} actions.json [...]")

