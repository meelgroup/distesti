from WAPS.waps import sampler as samp
from copy import deepcopy

class dDNNF:
    def __init__(self, inputFile):
        self.sampler = samp(cnfFile=inputFile)
        self.sampler.compile()
        self.sampler.parse()
        self.weight_map = self.parseWeights(inputFile)
        self.weighted_count = self.sampler.annotate()

    def parseWeights(self, inputFile):
        f = open(inputFile, "r")
        lines = f.readlines()
        f.close()
        weight_map = {}

        for line in lines:
            if line.startswith("w"):
                variable, weight = line[2:].strip().split()
                variable = int(variable)
                weight = float(weight)
                if (0.0 < weight < 1.0):
                    weight_map[variable] = weight
                else:
                    print("Error: weights should only be in (0,1) ")
                    exit(-1)
        return weight_map

    def sample(self, numSolutions, seed):
        samples, seed = self.sampler.sample(totalSamples=numSolutions)
        solList = list(samples)
        solList = [i.strip().split() for i in solList]
        solList = [[int(x) for x in i] for i in solList]
        return solList, seed

    def eval(self, element):
        element_w = deepcopy(element)

        weight = 1.0/self.weighted_count

        for i in range(len(element_w)):
            if element_w[i] > 0:
                weight *= self.weight_map.get(abs(element_w[i]), 0.5)
            else:
                weight *= 1-self.weight_map.get(abs(element_w[i]), 0.5)    
        return weight
