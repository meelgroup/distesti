import random
import itertools
import copy 

N = 3

def good(I):
  A = copy.deepcopy(I)
  for i in range(len(A)):
    x = A[i]
    j = random.randint(i,len(A)-1)
    A[i] = A[j]
    A[j] = x
  return A

def bad(I):
  A = copy.deepcopy(I)
  for i in range(len(A)-1):
    x = A[i]
    j = random.randint(0,len(A)-1)
    A[i] = A[j]
    A[j] = x
  return A

A = list(range(N))
print(A)
PA = list(itertools.permutations(A))

Da, Db, Dc= {},{},{}

for i in PA:
  Da = dict.fromkeys(PA, 0)
  Db = dict.fromkeys(PA, 0)
  Dc = dict.fromkeys(PA, 0)

NUM = 100000

for i in range(NUM):
    Da[tuple(good(A))]+=1
    Db[tuple(bad(A))]+=1
    Dc[tuple(good(A))]+=1

dab=0
for key in Da:
    dab+= 0.5* abs(Da[key] - Db[key])/NUM

dac=0
for key in Da:
    dac+= 0.5* abs(Da[key] - Dc[key])/NUM  

print(dab)
print(dac)





