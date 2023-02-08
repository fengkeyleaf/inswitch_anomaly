import re

#######################
# Paraphrase the decision tree txt file.
#######################

def find_action(textfile):
    action = []
    f = open(textfile)
    for line in f:
        n = re.findall(r"class", line)
        if n:
            fea = re.findall(r"\d", line)
            action.append(int(fea[1]))
    f.close()
    return action


def find_feature(textfile):
    f = open(textfile)
    line = f.readline()
    proto = re.findall('\d+', line)
    line = f.readline()
    src = re.findall('\d+', line)
    line = f.readline()
    dst = re.findall('\d+', line)
    f.close
    proto = [int(i) for i in proto]
    src = [int(i) for i in src]
    dst = [int(i) for i in dst]
    return proto, src, dst

def find_classification(textfile, proto, src, dst):
    fea = []
    sign = []
    num = []
    f = open(textfile, 'r')
    for line in f:
        n = re.findall(r"when", line)
        if n:
            fea.append(re.findall(r"(proto|src|dst)", line))
            sign.append(re.findall(r"(<=|>)", line))
            num.append(re.findall(r"\d+\.?\d*", line))
    f.close()

    protocol = []
    srouce = []
    dstination = []
    classfication = []

    for i in range(len(fea)):
        feature1 = [k for k in range(len(proto) + 1)]
        feature2 = [k for k in range(len(src) + 1)]
        feature3 = [k for k in range(len(dst) + 1)]
        for j, feature in enumerate(fea[i]):
            if feature == 'proto':
                sig = sign[i][j]
                thres = int(float(num[i][j]))
                id = proto.index(thres)
                if sig == '<=':
                    while id < len(proto):
                        if id + 1 in feature1:
                            feature1.remove(id + 1)
                        id = id + 1
                else:
                    while id >= 0:
                        if id in feature1:
                            feature1.remove(id)
                        id = id - 1
            elif feature == 'src':
                sig = sign[i][j]
                thres = int(float(num[i][j]))
                id = src.index(thres)
                if sig == '<=':
                    while id < len(src):
                        if id + 1 in feature2:
                            feature2.remove(id + 1)
                        id = id + 1
                else:
                    while id >= 0:
                        if id in feature2:
                            feature2.remove(id)
                        id = id - 1
            else:
                sig = sign[i][j]
                thres = int(float(num[i][j]))
                id = dst.index(thres)
                if sig == '<=':
                    while id < len(dst):
                        if id + 1 in feature3:
                            feature3.remove(id + 1)
                        id = id + 1
                else:
                    while id >= 0:
                        if id in feature3:
                            feature3.remove(id)
                        id = id - 1
        protocol.append(feature1)
        srouce.append(feature2)
        dstination.append(feature3)
        a = len(num[i])
        classfication.append(num[i][a - 1])
    return (protocol, srouce, dstination, classfication)