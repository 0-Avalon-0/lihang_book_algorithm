# encoding=utf-8
# @Author: WenDesi
# @Date:   12-11-16
# @Email:  wendesi@foxmail.com
# @Last modified by:   WenDesi
# @Last modified time: 12-11-16

import csv
import random

class SVM(object):

    def __init__(self, kernal='linear'):
        self.kernal = kernal

    def _init_parameters(self, features, labels):
        '''
        初始化一些参数
        '''
        self.X = features
        self.Y = labels

        self.b = 0.0
        self.n = len(features[0])
        self.N = len(features)
        self.alpha = [0.0] * self.N

        self.C = 1000
        self.Max_Interation = 5000

    def _satisfy_KKT(self, i):
        ygx = self.Y[i] * self._g_(i)
        if self.alpha[i] == 0:
            return ygx > 0 or ygx == 0
        elif self.alpha[i] == self.C:
            return ygx < 1 or ygx == 1
        else:
            return ygx == 1

    def _select_two_parameters(self):
        index_list = [i for i in xrange(self.N)]

        i1_list_1 = filter(lambda i: self.alpha[i] > 0 and self.alpha[i] < self.C, index_list)
        i1_list_2 = list(set(index_list) - set(i1_list_1))

        i1_list = i1_list_1
        i1_list.extend(i1_list_2)

        for i in i1_list:
            if not self._satisfy_KKT(i):
                continue

            E1 = self._E_(i)
            max_ = (0, 0)

            for j in index_list:
                if i == j:
                    continue

                E2 = self._E_(j)
                if abs(E1 - E2) > max_[0]:
                    max_ = (abs(E1 - E2), j)

            return i, max_[1]

    def _K_(self, x1, x2):
        '''
        核函数
        '''

        if self.kernal == 'linear':
            return sum([x1[k] * x2[k] for k in xrange(self.n)])

        print '没有定义核函数'
        return 0

    def _g_(self, i):
        '''
        公式(7.104)
        '''
        result = self.b

        for j in xrange(self.N):
            result += self.alpha[j] * self.Y[j] * self._K_(self.X[i], self.X[j])

        return result

    def _E_(self, i):
        '''
        公式(7.105)
        '''

        return self._g_(i) - self.Y[i]

    def train(self, features, labels):

        self._init_parameters(features, labels)

        for times in xrange(self.Max_Interation):
            print 'iterater %d' % times

            i1, i2 = self._select_two_parameters()

            L = max(0, self.alpha[i2] - self.alpha[i1])
            H = min(self.C, self.C + self.alpha[i2] - self.alpha[i1])

            if self.Y[i1] == self.Y[i2]:
                L = max(0, self.alpha[i2] + self.alpha[i1] - self.C)
                H = min(self.C, self.alpha[i2] + self.alpha[i1])

            E1 = self._E_(i1)
            E2 = self._E_(i2)
            eta = self._K_(self.X[i1], self.X[i1]) + self._K_(self.X[i2], self.X[i2]) - 2 * self._K_(self.X[i1], self.X[i2])     # 公式(7.107)

            alpha2_new_unc = self.alpha[i2] + self.Y[i2] * (E1 - E2) / eta        # 公式(7.106)

            # 公式(7.108)
            alph2_new = 0
            if alpha2_new_unc > H:
                alph2_new = H
            elif alpha2_new_unc < L:
                alph2_new = L
            else:
                alph2_new = alpha2_new_unc

            # 公式(7.109)
            alph1_new = self.alpha[i1] + self.Y[i1] * \
                self.Y[i2] * (self.alpha[i2] - alph2_new)

            # 公式(7.115) 及 公式(7.116)
            b_new = 0
            b1_new = -E1 - self.Y[i1] * self._K_(self.X[i1], self.X[i1]) * (alph1_new - self.alpha[i1]) - self.Y[i2] * self._K_(self.X[i2], self.X[i1]) * (alph2_new - self.alpha[i2]) + self.b
            b2_new = -E2 - self.Y[i1] * self._K_(self.X[i1], self.X[i2]) * (alph1_new - self.alpha[i1]) - self.Y[i2] * self._K_(self.X[i2], self.X[i2]) * (alph2_new - self.alpha[i2]) + self.b

            if alph1_new > 0 and alph1_new < self.C:
                b_new = b1_new
            elif alph2_new > 0 and alph2_new < self.C:
                b_new = b2_new
            else:
                b_new = (b1_new + b2_new) / 2

            self.alpha[i1] = alph1_new
            self.alpha[i2] = alph2_new
            self.b = b_new

    def _predict_(self,feature):
        result = self.b

        for i in xrange(self.N):
            result += self.alpha[i]*self.Y[i]*self._K_(feature,self.X[i])

        if result > 0:
            return 1
        return -1

    def predict(self,features):
        results = []

        for feature in features:
            results.append(self._predict_(feature))

        return results

# def build_dataset(origins,radius,labels,size):
#     result = []
#     dim = len(origins[0])
#     class_total = len(labels)
#     print class_total
#
#
#     for k in xrange(size):
#         tmp = []
#
#         index = random.randint(0,class_total-1)
#         print index
#         tmp.append(labels[index])
#
#         origin = origins[index]
#
#         points = [random.randint(0,radius) for i in xrange(dim)]
#         points = [points[i]+origin[i] for i in xrange(dim)]
#
#         tmp.extend(points)
#         result.append(tmp)
#
#     return result

def read_csv(filepath):
    reader = csv.reader(file(filepath, 'rb'))

    result = []
    for line in reader:
        result.append(line)
    return result

def split_features_labels(dataset):
    labels = map(lambda x:float(x[0]),dataset)
    features = map(lambda x:x[1:],dataset)

    for i in xrange(len(dataset)):
        for j in xrange(len(features[0])):
            features[i][j] = float(features[i][j])

    return features,labels

if __name__ == "__main__":
    #
    # dataset = build_dataset([[0,0,0],[30,30,30]],10,[-1,1],100)
    # writer = csv.writer(file('train.csv', 'wb'))
    # for line in dataset:
    #     writer.writerow(line)

    train_features,train_labels = split_features_labels(read_csv('train.csv'))
    test_features,test_labels = split_features_labels(read_csv('test.csv'))
    #
    # train_features,train_labels = [[3,3],[4,4],[1,1]],[1,1,-1]
    # test_features,test_labels = [[0,0],[0,3],[0,6]],[-1,-1,1]

    svm = SVM()
    svm.train(train_features,train_labels)
    test_predict = svm.predict(test_features)

    accuracy = sum([test_labels[i]==test_predict[i] for i in xrange(len(test_predict))])
    print 'accuracy is ', float(accuracy)/float(len(test_labels))
