from parser import parse_lines
import io

stream = io.open("examples/namecoin.se", "r") #, encoding="utf-8")

print(parse_lines(stream.readlines()))
#
#list = []
#for line in stream.readlines():
#    list.append(line[:-1])
#
#print(list)
#print(parse_lines(list))

