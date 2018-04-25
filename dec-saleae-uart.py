import sys

infile=open(sys.argv[1],"r")
lines=infile.readlines()
infile.close()

output=""
for line in lines:
	fields=line.rstrip().split(",")
	if fields[0] == "Time [s]":
		continue
	result=fields[2]
	if result == "' '":
		result=" "
	if result == "COMMA":
		result=","
	output+=result.decode('string_escape')

print output