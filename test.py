RelationShip={}
def readConf():
    Path="../RelateWork/Relationship"
    f = open(Path)  # 返回一个文件对象
    line = f.readline()  # 调用文件的 readline()方法
    while line:
        line= line[0:len(line)-1]
        sarr=line.split(' ')
        RelationShip[sarr[0]] = eval(sarr[1])
        line = f.readline()
    f.close()

if __name__ == '__main__':
    readConf()
    fo = open("Result.txt", "w",encoding='utf-8')
    fo.write("句子:" + "On Thursday, temperatures of 38.3 degrees were recorded in Strážnice in Hodonín, making it the hottest day of the year in the Czech Republic."+"\n")