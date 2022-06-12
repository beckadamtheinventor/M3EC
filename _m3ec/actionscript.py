
def execScriptFile(fname, d):
	with open(fname) as f:
		return execScript(f.read(), d)

def execScript(data, d):
	if type(data) is str:
		ld = lexScript(data, d)
		if ld is not None:
			return execActions(ld, d)
	elif type(data) is list:
		return execActions(data, d)
	elif type(data) is dict:
		return execActions([data], d)
	else:
		return None

def lexScript(data, d):
	ld = []
	i = 0
	datalines = data.split("\n")
	while line in datalines:
		cmd, args = line.split("(", maxsplit=1)
		args = args.strip(" \t")
		if args.endswith(")"):
			args = args[:-1]
		args = [a.strip(" \t") for a in args.split(",")]
		m = {"action": readf(cmd, d)}
		for arg in args:
			a,b = arg.split(":")
			m[a.strip[" \t"]] = b.strip(" \t")
		ld.append(m)
		i += 1

	return ld

def nextWhiteSpace(data, i):
	l = []
	j = data.find(" ", i)
	if j != -1 and not (j > 1 and data[j-1] == '\\'):
		l.append(j)
	j = data.find("\t", i)
	if j != -1 and not (j > 1 and data[j-1] == '\\'):
		l.append(j)
	j = data.find("\n", i)
	if j != -1 and not (j > 1 and data[j-1] == '\\'):
		l.append(j)
	if len(l):
		return min(l)
	return -1

