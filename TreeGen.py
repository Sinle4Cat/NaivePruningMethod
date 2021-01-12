import nltk.tree as tree
from stanfordcorenlp import StanfordCoreNLP
import nltk
import copy
import re
from treelib import Tree as Tr
Sub=[]#识别到的从句
Remain=[]#识别到的不可拆词
Trunk=[]#记录为token位置
RelationShip={}
TokenAll=[] #每个句子的全部token
RemoveTreedist={}
StrGen=[]
RemainLt=[] #需要保留的token 不能正常删除
nlpEN=None

class node:
    def __init__(self, type, flag=0, word=""):
        self.type = type
        self.flag = flag
        self.word = word

def ccPart(dependency,token):#################
    dependencyParse = copy.deepcopy(dependency)
    findSource=[]
    findCC=[]
    findDis={}
    RemoveList=[]
    DependList=[]
    ccStr=[]
    isRetoken=[i for i in range(len(token))]
    for dependencyitem in dependency:
        tag,begin,end=dependencyitem
        if tag=="conj":
            findSource.append(begin)
            findCC.append(end)
    if len(findCC) == 0:
        return []
    for item in findSource:
        flag=False
        for key in findDis.keys():
            if(key==item):
                flag=True
        if flag==False:
            findDis[item]=1
        else:
            count=findDis[item]
            count+=1
            findDis[item]=count
    mains=[]
    #判断前后是否有对匹配对依赖
    for i in range(len(findCC)):
        dependencyParseTemp = copy.deepcopy(dependency)
        dependencyParseTemp2 = copy.deepcopy(dependency)
        if(findDis[findSource[i]]==1):
            stack=[]
            stack.append(findSource[i])
            removeItem1=[]
            removeItem=[]

            #判断是否为根节点
            cutindex=-1
            for relation in dependencyParseTemp:
                tag, begin, end = relation
                if (begin == findSource[i] and tag=='nsubj'):
                    cutindex=end
            while(len(stack)>0):
                popitem=stack.pop()
                removeItem.append(popitem)
                num = len(dependencyParseTemp)
                j = 0
                while j < num:
                    relation = dependencyParseTemp[j]
                    tag,begin,end=relation
                    if(begin==popitem and end>cutindex and end!=findCC[i]):
                        stack.append(end)
                        dependencyParseTemp.remove(relation)
                        j-=1
                        num-=1
                    j=j+1

            num=len(dependencyParseTemp)
            j=0

            while j<num:
                relation=dependencyParseTemp[j]
                tag, begin, end = relation
                if (tag == "cc" and begin == findCC[i]):
                    removeItem.append(end)
                    dependencyParseTemp.remove(relation)
                    j=j-1
                    num=num-1
                if (end == findSource[i]):
                    end = findCC[i]
                    dependencyParseTemp.remove(relation)
                    relation = (tag, begin, end)
                    dependencyParseTemp.insert(j,relation)
                if(begin == findSource[i]):
                    if(tag!='aux'):
                        begin=findCC[i]
                        dependencyParseTemp.remove(relation)
                        relation = (tag, begin, end)
                        dependencyParseTemp.insert(j, relation)
                    else:
                        dependencyParseTemp.remove(relation)
                        j = j - 1
                        num = num - 1

                j+=1

            stack.append(findCC[i])
            while len(stack)>0:
                popitem = stack.pop()
                removeItem1.append(popitem)
                num = len(dependencyParseTemp2)
                j = 0
                while j < num:
                    relation = dependencyParseTemp2[j]
                    tag, begin, end = relation
                    if (begin == popitem):
                        stack.append(end)
                        dependencyParseTemp2.remove(relation)
                        j -= 1
                        num -= 1
                    j = j + 1

            isRt1 = copy.deepcopy(isRetoken)
            isRt2 = copy.deepcopy(isRetoken)
            for j in removeItem:
                isRt1.remove(j-1)
            for j in removeItem1:
                isRt2.remove(j-1)
            str1=replacenth(token,isRt1)
            str2 = replacenth(token, isRt2)
            if(str1[-1]==' '):
                str1=str1[0:len(str1)-1]
            if(str1[-1]!='.'):
                str1+='.'
            if(str2[-1] == ' '):
                str2 = str2[0:len(str2) - 1]
            if (str2[-1] != '.'):
                str2 += '.'
            ccStr.append(str2)
            ccStr.append(str1)
        else:
            if findSource[i] not in mains:
                mains.append(findSource[i])
            stack = []
            stack.append(findSource[i])
            removeItem = []
            # 判断是否为根节点
            # 删除出去我们选择的conj以外的所有同级别内容
            while (len(stack) > 0):
                popitem = stack.pop()
                removeItem.append(popitem)
                num = len(dependencyParseTemp)
                j = 0
                while j < num:
                    relation = dependencyParseTemp[j]
                    tag, begin, end = relation
                    if (begin == popitem and end != findCC[i]) or ( begin == popitem and tag == "conj" and end != findCC[i]):
                        stack.append(end)
                        dependencyParseTemp.remove(relation)
                        j -= 1
                        num -= 1
                    j = j + 1


            num = len(dependencyParseTemp)
            j = 0
            while j < num:
                relation = dependencyParseTemp[j]
                tag, begin, end = relation
                if (tag == "cc" and begin == findCC[i]):
                    removeItem.append(end)
                    dependencyParseTemp.remove(relation)
                    j = j - 1
                    num = num - 1
                if (end == findSource[i]):
                    end = findCC[i]
                    dependencyParseTemp.remove(relation)
                    relation = (tag, begin, end)
                    dependencyParseTemp.insert(j, relation)
                j += 1
            isRt1 = copy.deepcopy(isRetoken)
            for j in removeItem:
                isRt1.remove(j - 1)
            str1 = replacenth(token, isRt1)
            str1 = str1.replace(','," ")
            if (str1[-1] == ' '):
                str1 = str1[0:len(str1) - 1]
            ccStr.append(str1)

    for i in mains:
        stack = []
        dependencyParseTemp = copy.deepcopy(dependency)
        for relation in dependencyParseTemp:
            tag, begin, end = relation
            if (begin == i and tag == "conj"):
                stack.append(end)
                dependencyParseTemp.remove(relation)

        removeItem = []
        # 判断是否为根节点
        # 删除出去我们选择的conj以外的所有同级别内容
        while (len(stack) > 0):
            popitem = stack.pop()
            removeItem.append(popitem)
            for relation in dependencyParseTemp:
                tag, begin, end = relation
                if (begin == popitem ) or (begin == popitem and tag == "conj"):
                    stack.append(end)
                    dependencyParseTemp.remove(relation)
        isRt1 = copy.deepcopy(isRetoken)
        for i in removeItem:
            isRt1.remove(i - 1)
        str1 = replacenth(token, isRt1)
        str1 = str1.replace(',', " ")
        if (str1[-1] == ' '):
            str1 = str1[0:len(str1) - 1]
        ccStr.append(str1)
    return ccStr

def dependencyTree(dependency,token):
    tree=[]
    dependencyParse=copy.deepcopy(dependency)
    token = copy.deepcopy(token)
    tree = Tr()
    root = -1
    #构建依存树
    while (len(dependencyParse) != 0):
        dependencyParseItem = dependencyParse.pop(0)
        i, begin, end = dependencyParseItem
        if begin == 0:
            root = end
            tree.create_node(token[end - 1], end, data=node(i, 0, token[end - 1]))
            continue
        elif tree.contains(begin):
            tree.create_node(token[end - 1], end, parent=begin, data=node(i, 0, token[end - 1]))
        elif len(dependencyParse)>=1:
            dependencyParse.append(dependencyParseItem)
    return tree,root



def Cons_Traversal(t):
    queue= []
    queue.append(t)

    current = ""
    while queue:
        current = queue.pop(0)

        if isinstance(current, tree.Tree):
            flag=False
            if current.label()=="SBAR":
                Sub.append(current.leaves())
                continue
            for i in range(len(current)):
                if isinstance(current[i], tree.Tree)and(current[i].label()=="HYPH"):
                    flag=True
            if(flag==False):
                for i in range(len(current)):
                    queue.append(current[i])
                    #print(current.label(),current)
            else:
                Remain.append(current.leaves())


        elif isinstance(current, str):
            #print(current)
            pass



def traverse_tree(tree):
    print("tree:", tree)
    if(tree.label()=="SBAR"):
        Sub.append(tree.leaves())
        return
    if(tree.label()=="NP" or tree.label()=="ADJP" or tree.label()=="ADVP"):
        #判断是否有副词组合，形容词组合，名词组合。在判断某些词汇的时候遇到了一些问题。先去除了表语的识别。
        print(tree.leaves())
        if len(tree.leaves())>1:
            Remain.append(tree.leaves())
        return
   # print("tree2:",tree[0])
    for subtree in tree:
        if type(subtree) == nltk.tree.Tree:
            traverse_tree(subtree)

def Depd_Travesal(dependency_tree,token,Trunk):
    # 保留主干成
    dependencyParse=copy.deepcopy(dependency_tree)
    token = copy.deepcopy(token)
    root = -1
    while (len(dependencyParse) != 0):
        dependencyParseItem = dependencyParse.pop(0)
        i, begin, end = dependencyParseItem
        if RelationShip.get(i,-10)==3:
            Trunk.append(end-1)

def readConf():
    Path = "../RelateWork/Relationship"
    f = open(Path)
    line = f.readline()
    while line:
        line = line[0:len(line) - 1]
        sarr = line.split(' ')
        RelationShip[sarr[0]]=eval(sarr[1])
        line = f.readline()
    f.close()

def Prune(dependency_tree,token):
    pass

def Pruning(Tree,root,dependency,token,isReToken,string):
        global StrGen
        if(len(Tree.children(root))>0):
            temp=Tree.children(root)
            temp.sort(key=lambda x:len(Tree.children(x.identifier)))
            temp.reverse()
            rember=0
            for node in temp:
                index = node.identifier
                if (len(Tree.children(index)) == 0):
                    break
                rember = rember + 1
            tempmax=[]
            if(rember>0):
                tempmax=temp[:rember]
            templow=temp[rember:]
            templow.reverse()
            temp=tempmax+templow
            for node in temp:
                index=node.identifier
                tag=node.data.type
                if RelationShip.get(tag,-10)==1:
                    if len(Tree.children(root)) > 0:
                        string, isReToken = Pruning(Tree, index, dependency, token, isReToken, string)
                elif RelationShip.get(tag,-10)==-10 or RelationShip.get(tag,-10)==3:
                    if len(Tree.children(root)) > 0:
                        string, isReToken = Pruning(Tree, index, dependency, token, isReToken, string)
                elif  RelationShip.get(tag, -10) == 4:
                    return string,isReToken
                elif RelationShip.get(tag,-10)==0 :
                    if len(Tree.children(index)) > 0:
                        string,isRetoken=Pruning(Tree,index,dependency,token,isReToken,string)
                        if len(Tree.children(index))>=0 :
                            remove = Tree.remove_subtree(index)
                            removeNode=remove.nodes
                            listRemove0=[]
                            #判断Remain是否可以整体删除
                            # for lll in RemainLt:
                            #     flag=0
                            #     for jj in lll:
                            #         for iii in removeNode:
                            #             if(iii==jj):
                            #                 flag=1
                            #                 break
                            #
                            #         if flag==1:
                            #             break
                            #     test=1
                            #     for ln in range(len(lll)):
                            #         t1=0
                            #         for iii in removeNode:
                            #             if(lll[ln]==iii):
                            #                 t1=1
                            #                 break
                            #         if(t1==0):
                            #             test=0
                            # if test==0:
                            #         return string,isReToken
                            dependencyParse = copy.deepcopy(dependency)
                            ##进行删除
                            for i in removeNode:
                                listRemove0.append(i)
                            for i in removeNode:
                                isReToken.remove(i-1)
                            treeTemp=copy.deepcopy(Tree)
                            RemoveTreedist[index] = treeTemp
                            for tuple in dependency:
                                if tuple[2] == index:
                                    dependency.remove(tuple)
                            for i in listRemove0:
                                string= replacenth(token, isReToken)
                                string = string.replace("  ", " ")
                            StrGen.append(string)
                    elif not JustReMain(index):
                        remove = Tree.remove_subtree(index)
                        removeNode = remove.nodes
                        listRemove0 = []
                        dependencyParse = copy.deepcopy(dependency)
                        ##进行删除
                        for i in removeNode:
                            listRemove0.append(i)
                        for i in removeNode:
                            isReToken.remove(i-1)
                        for tuple in dependency:
                            if tuple[2] == index:
                                dependency.remove(tuple)
                        tempTree=copy.deepcopy(Tree)
                        RemoveTreedist[index]=tempTree
                        string= replacenth(token, isReToken)
                        string = string.replace("  ", " ")

                        StrGen.append(string)
        else :
            type=Tree.nodes[root].data.type
            index = Tree.nodes[root].identifier
            if RelationShip.get(type,-10)==0 and not JustReMain(index):
                remove = Tree.remove_subtree(index)
                removeNode = remove.nodes
                listRemove0 = []
                dependencyParse = copy.deepcopy(dependency)
                ##进行删除
                for i in removeNode:
                    isReToken.remove(i-1)
                for i in removeNode:
                    listRemove0.append(i)
                for tuple in dependency:
                    if tuple[2] == index:
                        dependency.remove(tuple)
                tempTree = copy.deepcopy(Tree)
                RemoveTreedist[index] = tempTree
                string= replacenth(token, isReToken)
                string=string.replace("  "," ")

                StrGen.append(string)
                return string, isReToken
            else:
                 pass
        return string,isReToken

def JustReMain(index):
    for i in RemainLt:
        for j in i:
            if(index==j):
                return True
    return False


def TokenToStr(string,Token,isRemaintoken):
    pass
    # isRemaintoken.sort()
    # newstring=""
    # for i in isRemaintoken:
    #     if len(token[i])==1 and not ('a'<=token[i]<='z' or 'A'<=token[i]<='Z' or '0'<=token[i]<='9'):
    #         if(len(newstring)>=1):
    #             charw=newstring[-1]
    #             if(charw==' '):
    #                  newstring=newstring[:len(newstring)-1]
    #         if(token[i]==','):
    #             newstring+=token[i]
    #         else:
    #             newstring+=token[i]+" "
    #     else:
    #         newstring=newstring+token[i]+" "

def replacenth(token,isRetoken):
    newstring=""
    for i in range(len(isRetoken)):
        if len(token[isRetoken[i]])==1 and not ('a'<=token[isRetoken[i]]<='z' or 'A'<=token[isRetoken[i]]<='Z' or '0'<=token[isRetoken[i]]<='9'):
            if(len(newstring)>=1):
                charw=newstring[-1]
                if(charw==' '):
                     newstring=newstring[:len(newstring)-1]
            if(i==','):
                newstring+=token[isRetoken[i]]
            else:
                newstring+=token[isRetoken[i]]+" "
        else:
            newstring=newstring+token[isRetoken[i]]+" "

    return newstring


def justTokenSame(token1,token2):
    if(len(token1)+1!=len(token2)):
        return False
    else:
        flag=False
        index1=0
        index2=0
        while index1<len(token1):
            if flag==False:
                if(token1[index1]!=token2[index2]):
                    index2+=1
                    flag==True
                else:
                    index1+=1
                    index2+=1
            else:
                if (token1[index1] != token2[index2]):
                    return False
    return True



def replacethL(string ,sub,isReToken):
    result=""
    newtoken=[]
    for y in range(20):
        try:
            new_sent = replacenth1(string, sub, y + 1).replace("  ", " ")
            newtoken=nlpEN.word_tokenize(new_sent)
            if(justTokenSame(newtoken,isReToken)):
                result=new_sent
                break
        except:
            break
    return result,newtoken

def replacenth1(string, sub, n):
    where = [m.start() for m in re.finditer(sub, string)][n - 1]
    before = string[:where]
    after = string[where:]
    after = after.replace(sub,"", 1)
    newString = before + after
    return newString

def RemoveSub(string,sub,token):
    subtoken=nlpEN.word_tokenize(sub)
    Remainls=[]
    for i in range(0, len(token)-len(subtoken)+1):
        flag=0
        index=0
        while(index<len(subtoken)):
            if(token[i+index]!=subtoken[index]):
                break
            index+=1
        if(index ==len(subtoken)):
            for j in range(len(subtoken)):
                Remainls.append(j+i)
    return Remainls

def FindRemain(token):
    RemainList=[]
    for i in range(len(token)):
        for item  in Remain:
            index=0
            itemNum=len(item)
            while(index<itemNum):
                if token[i+index]!=item[index]:
                    break
                index+=1
            if index==itemNum:
                ll=[]
                for j in range(itemNum):
                    ll.append(j+i)
                RemainList.append(ll)
    return RemainList

def Gen(sent):
    source_tree = tree.Tree.fromstring(nlpEN.parse(sent))
    sentSub = []
    global Sub
    global StrGen
    Sub.clear()
    StrGen.clear()
    sentSubRemain = []
    MainRemoveSub = []

    token = nlpEN.word_tokenize(sent)
    MainRemain = [i for i in range(len(token))]
    # 对于从句的删除应该是连续的token
    Cons_Traversal(source_tree)  # 识别不可拆组合词 从句
    if len(Sub) > 0:

        str = copy.deepcopy(sent)
        for i in range(len(Sub)):
            sub = ""
            for j in Sub[i]:
                sub += j + " "
            sub = sub[0:len(sub) - 1]
            isRemain = RemoveSub(str, sub, token)
            sub += "."
            sentSubRemain.append(isRemain)
            sentSub.append(sub)
    for sentsubtoken in sentSubRemain:
        for j in sentsubtoken:
            MainRemain.remove(j)
    # 对主句进行处理：
    sentMain = replacenth(token, MainRemain)
    if(sentMain[0]==',' or sentMain[0]=='.'):
        sentMain= sentMain[1:len(sentMain)]
    token_main = nlpEN.word_tokenize(sentMain)
    dep_main = nlpEN.dependency_parse(sentMain)

    global RemainLt
    RemainLt.clear()
    RemainLt = FindRemain(token_main)

    Trunk.clear()
    Depd_Travesal(dep_main, token_main, Trunk)  # 识别主干内容
    strlist = ccPart(dep_main, token_main)
    if (len(strlist) == 0):
        dp_tree_main, root = dependencyTree(dep_main, token_main)
        re_token_main = [i for i in range(len(token_main))]
        #dp_tree_main.show()
        # Tree,root,dependency,token,isReToken,string)
        string, re_token_main = Pruning(dp_tree_main, root, dep_main, token_main, re_token_main, sentMain)
    else:
        for sentCC in strlist:

            StrGen.append(sentCC)
            token_cc = nlpEN.word_tokenize(sentCC)
            dep_cc = nlpEN.dependency_parse(sentCC)
            RemainLt.clear()
            RemainLt = FindRemain(token_cc)
            Trunk.clear()
            Depd_Travesal(dep_cc, token_cc, Trunk)
            dp_tree_cc, root = dependencyTree(dep_cc, token_cc)
            re_token_cc = [i for i in range(len(token_cc))]
            #dp_tree_cc.show()
            # Tree,root,dependency,token,isReToken,string)
            string, re_token_cc = Pruning(dp_tree_cc, root, dep_cc, token_cc, re_token_cc, sentCC)

    # 对从句进行处理
    for sentitem in sentSub:

        StrGen.append(sentitem)
        Trunk.clear()
        dependency_tree = nlpEN.dependency_parse(sentitem)
        token_sub = nlpEN.word_tokenize(sentitem)
        RemainLt = FindRemain(token_sub)
        Depd_Travesal(dependency_tree, token_sub, Trunk)  # 识别主干内容
        strlist = ccPart(dependency_tree, token_sub)

        if (len(strlist) == 0):
            dp_tree_sub, root = dependencyTree(dependency_tree, token_sub)
            re_token_sub = [i for i in range(len(token_sub))]
            string, re_token_main = Pruning(dp_tree_sub, root, dependency_tree, token_sub, re_token_sub, sentitem)
            strlist = ccPart(dep_main, token_main)
        else:
            for sentCC in strlist:

                StrGen.append(sentCC)
                token_cc = nlpEN.word_tokenize(sentCC)
                dep_cc = nlpEN.dependency_parse(sentCC)
                RemainLt.clear()
                RemainLt = FindRemain(token_cc)
                Trunk.clear()
                Depd_Travesal(dep_cc, token_cc, Trunk)
                dp_tree_cc, root = dependencyTree(dep_cc, token_cc)
                re_token_cc = [i for i in range(len(token_cc))]
                #dp_tree_cc.show()
                # Tree,root,dependency,token,isReToken,string)
                string, re_token_cc = Pruning(dp_tree_cc, root, dep_cc, token_cc, re_token_cc, sentCC)
    StrResult=copy.deepcopy(StrGen)
    return StrResult
def genAll(dataset,nlpEN):
    file = open(dataset, "r", encoding="utf-8")
    dic = {}
    Strlist=[]
    for line in file:
        sent = line.split("\n")[0]
        print(sent)
        dependcy = nlpEN.dependency_parse(sent)
        token = nlpEN.word_tokenize(sent)
        strr=""
        for i, begin, end in dependcy:
            if begin - 1 < 0:
                first = "NULL"
            else:
                first = token[begin - 1]
            last = token[end - 1]
            strr+=i+'-'.join([str(begin), first])+ '-'.join([str(end), last])+"\n"
        Strlist.append(strr)

        phrases = Gen(sent)
        dic[sent] = []
        for t in phrases:
            dic[sent].append(t)

    return dic,Strlist

def print1(dic,Strlist):
    n=0
    fo = open("Result.txt", "w",encoding='utf-8')
    for sent in dic:
        print("句子:"+sent)
        fo.write("句子:"+sent+"\n")
        print("依存关系：")
        fo.write("依存关系："+"\n")
        print(Strlist[n])
        fo.write(Strlist[n]+"\n")
        print("派生句子：")
        fo.write("派生句子："+"\n")
        n=n+1
        for new in dic[sent]:
            print(" "+new)
            fo.write(" "+new + "\n")

        fo.write("\n")


if __name__ == '__main__':
    readConf()#读取Relationship
    dataset = "../dataset/temp"
    nlpEN = StanfordCoreNLP(r'D:\nlpenvironment\stanford-corenlp-4.1.0')
    # sent = "We're going to Ferguson right now because the police killed an 18-year-old boy and it wasn't right."
    # str=Gen(sent)
    dist,strlist=genAll(dataset, nlpEN)
    print1(dist,strlist)
    nlpEN.close()