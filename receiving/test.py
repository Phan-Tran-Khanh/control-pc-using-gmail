x = '"Bảo Anh Trần" <baoanh27042002@gmail.com>'
y = x.replace('<', '')
print(y)
y = y.replace('>', '')
print(y)
y = y.split(' ')
print(y)
y = y[-1]
print(y)