
def execScriptFile(fname, d):
	with open(fname) as f:
		return execScript(f.read(), d)

def execScript(data, d):
	if type(data) is str:
		return execActions(lexScript(data, d), d)
	elif type(data) is list:
		return execActions(data, d)
	elif type(data) is dict:
		return execActions([data], d)
	else:
		return None

def lexScript(data, d);
	ld = []
	i = j = 0
	while i < len(data):
		if i == -1:
			break
		if data[i].isalnum():
			j = nextWhiteSpace(data, i)
			if j == -1:
				word = data[i:]
			else:
				word = data[i:j]
			
			
			i = j
		else:
			c = data[i]
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

