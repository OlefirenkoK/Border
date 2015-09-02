dic = {}
string = 'asdasdasd asdsad asd , asd.sa dasd as.as dasd a.asd '

from re import findall

pattern = findall('[a-z]+', string)

print(pattern)