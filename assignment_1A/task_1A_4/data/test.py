# yonghong HUANG (CIEL)
# yonghong HUANG
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.stats import poisson, multivariate_normal
import math

class SEEM:
    def __init__(self, k, iter, limit=0.001):
        self.limit = limit
        self.iter = iter
        self.X0 = []
        self.X1 = []
        self.S = []
        self.number = 0
        self.k = k
        self.r = []
        self.pi = []
        self.lamda= [] #lambda
        self.cov0 = []
        self.cov1 = []
        self.miu0 = np.zeros((self.k, 2))
        self.miu1 = np.zeros((self.k, 2))
        self.likelihood = 0


    def getX(self):
        X0 = []
        X1 = []
        R = np.loadtxt('X.txt')
        b = np.hsplit(R, 2)
        i = 0
        for item in b[0]:
            X0.append(item[0])
            i += 1
        i = 0
        for item in b[1]:
            X1.append(item[0])
            i += 1
        self.X1 = X1
        self.X0 = X0

    def getS(self):
        self.S = np.loadtxt('S.txt')


    def initia(self):
        self.getX()
        self.getS()
        self.number = len(self.S)
        np.random.seed(0)
        self.pi = np.full(self.k, 1.0 / self.k)
        self.lamda = np.mean(self.S) * np.ones(self.k)

        self.cov0 = np.ones(self.k)
        self.cov1 = np.ones(self.k)
        self.r = [[0]*self.k]*self.number


        self.miu0 = np.mean(self.X0) * np.ones(self.k)
        self.miu1 = np.mean(self.X1) * np.ones(self.k)

    def E_part(self):
        r = []
        for i in range(self.number):
            s = 0
            for j in range(self.k):
                self.r[i][j] = self.pi[j] * poisson.pmf(self.S[i],self.lamda[j])*\
                               multivariate_normal.pdf(self.X0[i],mean=self.miu0[j],cov=self.cov0[j])\
                               *multivariate_normal.pdf(self.X1[i],mean=self.miu1[j],cov=self.cov1[j])

                s += self.r[i][j]
            r.append(s)

        for i in range(self.number):
            for j in range(self.k):
                self.r[i][j] /= r[i]

    def M_part(self):
        self.r = np.array(self.r)
        for k in range(self.k):

            # print(np.array(self.X0).shape)
            # print(np.array(self.r[:,k]).shape)
            n = np.sum(self.r[:, k])
            self.miu0[k] = np.sum(self.r[:, k]*self.X0) / n
            self.miu1[k] = np.dot(self.r[:, k], self.X1) / n
            self.lamda[k] = np.dot(self.S, self.r[:, k]) / n
            self.pi[k] = n / self.number
            for i in range(self.number):
                self.cov0[k] += self.r[i][k] * ((self.X0[i]-self.miu0[k])**2)
                self.cov1[k] += self.r[i][k] * ((self.X0[i]-self.miu0[k])**2)
            self.cov0[k] /= n
            self.cov1[k] /= n

    def loglike(self):
        p = np.zeros((self.number, self.k))
        for i in range(self.number):
            for j in range(self.k):
                p[i][j] = self.pi[j] * poisson.pmf(self.S[i], self.lamda[j])\
                          * multivariate_normal.pdf(self.X0[i], mean=self.miu0[j], cov=self.cov0[j])\
                          *multivariate_normal.pdf(self.X1[i], mean=self.miu1[j], cov=self.cov1[j])
        likelihood = np.sum(np.log(np.sum(p, axis=1)))
        if np.abs(self.likelihood-likelihood) < self.limit:
            return False
        self.likelihood = likelihood
        return True

    def iteration(self):
        i = 0
        self.initia()
        while(i<self.iter):
            self.E_part()
            self.M_part()
            if(self.loglike()== False):
                break
            i += 1


f = SEEM(6,50,0.001)
f.iteration()




