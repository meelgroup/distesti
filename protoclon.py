from math import ceil, log, comb, floor
from random import randint, uniform
from statistics import median
import argparse

from distributions import dist

SAMPLER_UNIGEN3 = 1
SAMPLER_QUICKSAMPLER = 2
SAMPLER_STS = 3
SAMPLER_CMS = 4
SAMPLER_APPMC3 = 5
SAMPLER_SPUR = 6
SAMPLER_CUSTOM = 7


def subvssub(P,Q,eps,n,seed):
    
    m = int(16*log(20)/(eps**2)) 
    T = hoeffding(2/3,1/2,1/(10*m))
    M = ceil(10*(2**11*n**3*m*T/eps**3)+ 2**11*n**2*m*T/eps**2)
   
    print(f"eps: {eps}, T: {T}, m: {m}")
    
    Ratios = []
    running_count = 0

    for i in range(m):
        qsample = Q.samp(1,seed)

        p,q = [],[]
        for _ in range(T):
            (qi, running_count) =  subtoeval(Q,epsilon/16,qsample[0], n,running_count, M, seed)
            q.append(qi)
            (pi, running_count) =  subtoeval(P,epsilon/16,qsample[0], n,running_count, M, seed, taming = epsilon/(2*n))
            p.append(pi)

        p,q = median(p), median(q)
        
        if q>p:
            Ratios.append(1-p/q)
    
    print(f"Total Samples = {running_count}")
        
    if sum(Ratios) > m*(epsilon):
        print(f"estimate {sum(Ratios)/m} +- {epsilon} ")

# one sided hoeffding, that returns the minimum # of flips to 
# ensure that the probability that a coin with bias 'a'
# of heads returns heads 'b' fraction of the times is > 1-delta

def hoeffding(a,b,delta):
    for t in range(1, 1000, 2):
        res = 0
        for k in range(floor(t*b)+1, t+1):
            term = comb(t,k) * a**k * (1-a)**(t-k)
            assert(term != 0.0)
            res += term
        if res >= 1- delta:
            return t
    return ceil(log(1/delta)/(2*(b-a)**2))

    
def subtoeval(D,eps,sample, n, running_count,M, seed, taming = 0.0):
    
    k = n*ceil(4/eps**2)
    print(f"k={k}, eps={eps}, n={n}")
    
    marginals = []
    
    estimate = 1.0
    for j in range(n-1,-1,-1):
        print(f"at level {j} looking for {k} many samples")
        t,x = 0,0
        D.create_subcond_query(sample[0][:j])
        
        step = 64
        tamed_step = 0 #this is an implementation of taming, where we will first flip a coin with 2*taming
                       #to decide which subcond query to actually do 
       
        for i in range(step):
            if uniform(0,1) < 2*taming:
                tamed_step += 1
                if randint(0,1) == 1:
                    t+=1

        while(t < k):
            running_count += step
            alpha = D.subcond(step - tamed_step,sample[0][:j], seed + running_count)

            for bit in alpha:
                assert(abs(bit[0])==abs(sample[0][j]))
                if bit[0] == sample[0][j]:
                    t = t+1

            x = x+step
            if running_count >= M:
                print("Reject: Too many samples to reach at p")
                exit(0)
        estimate *= t/x #to account for step size we do t/x instead of k/x

    print(f"estimate is {estimate}")
    marginals.append(estimate)

    return (estimate, running_count)


if __name__=="__main__":

    samplers = str(SAMPLER_UNIGEN3) + " for UniGen3\n"
    samplers += str(SAMPLER_QUICKSAMPLER) + " for QuickSampler\n"
    samplers += str(SAMPLER_STS) + " for STS\n"
    samplers += str(SAMPLER_CMS) + " for CMS\n"

    parser = argparse.ArgumentParser()
    parser.add_argument('--sampler1', type=int, help=samplers,
                        default=SAMPLER_CMS, dest='sampler1')
    parser.add_argument('--sampler2', type=int, help=samplers,
                        default=SAMPLER_CMS, dest='sampler2')
    parser.add_argument('--epsilon', type=float,
                        help="default = 0.5", default=0.5, dest='epsilon')
    parser.add_argument('--delta', type=float,
                        help="default = 0.4", default=0.4, dest='delta')
    parser.add_argument('--max', type=int, default=10**8,
                        help="max samples", dest='max')
    parser.add_argument('--seed', type=int, required=True, dest='seed')
    parser.add_argument('--verb', type=int, dest='verbose')
    parser.add_argument("input", help="input file")
    parser.add_argument("--input2", help="second input file(optional)", default="")

    args = parser.parse_args()

    inputFile1 = args.input
    if args.input2 == "":
        inputFile2 = inputFile1

    sampler1 = args.sampler1
    sampler2 = args.sampler2
    
    epsilon = args.epsilon
    delta = args.delta
    
    verbosity = args.verbose
    seed = int(args.seed)
    
    P = dist(inputFile1, seed, access = ["SAMP", "SUBCOND"], input_sampler=sampler1)
    Q = dist(inputFile2, seed+1, access = ["SAMP", "SUBCOND"], input_sampler=sampler2)
    
    R = hoeffding(3/5,1/2,delta)
    print(f"{R} rounds to get {delta} confidence")

    results = []
    for r in range(R):
        results += subvssub(P,Q,epsilon,P.dimensions,seed)
    
    if median(results) == 1:
        print("Final: Accept")
    else:
        print("Final: Reject")
