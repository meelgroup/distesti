from interfaces.CNF import cnf
from interfaces.dDNNF import dDNNF

class dist:
    def __init__(self, inputFile, seed, access= ["SAMP"], approx = 0.0, sampler_type = "CNF",input_sampler = 1):
        self.access = access
        self.approx = approx
        self.sampler_type = sampler_type
        self.inputFile = inputFile
        self.inputFileType = inputFile.split('.')[-1]
        self.support_vars = self.dimension_find()
        self.dimensions = len(self.support_vars)
        self.seed = seed
        self.sampler = None
        
        # our approxeval oracle is a dDNNF
        if "APPROXEVAL" in access:
            if sampler_type == "dDNNF" and self.inputFileType == "cnf":
                self.sampler = dDNNF(inputFile)

        if sampler_type == "CNF":
            self.sampler = cnf(input_sampler, inputFile)

            
    def samp(self, numsamp=1, seed=123):
        samplelist = []

        if self.sampler_type == "CNF":
            samplelist,seed = self.sampler.sample(numsamp, seed)
        elif self.sampler_type == "dDNNF":
            samplelist,seed = self.sampler.sample(numsamp, seed)
        else:
            print(f"sampler type {self.sampler_type} is not implemented yet")

        assert(len(samplelist) == numsamp)
        return samplelist,seed

    def eval(self, element, approx = 0.0):
        if self.sampler_type in ["dDNNF"]:
            return self.sampler.eval(element)
    
    def create_subcond_query(self, query):
        if self.sampler_type == "CNF":
            self.sampler.create_subcond_query(query)
    
    def subcond(self,numSamp,query,seed):
        if self.sampler_type == "CNF":
            return self.sampler.subcond(numSamp,query,seed)

    def dimension_find(self):  # returns list of Support Variables
        f = open(self.inputFile, "r")
        lines = f.readlines()
        f.close()
        
        if self.inputFileType == "cnf":
            indList = []
            numVars = 0
            for line in lines:
                if line.startswith("p cnf"):
                    fields = line.split()
                    numVars = int(fields[2])
                if line.startswith("c ind"):
                    indList.extend(
                        line.strip()
                        .replace("c ind", "")
                        .replace(" 0", "")
                        .strip()
                        .replace("v ", "")
                        .split()
                    )
            if len(indList) == 0:
                indList = [int(x) for x in range(1, numVars + 1)]
            else:
                indList = [int(x) for x in indList]
            return indList
        
        else:
            print(f"implement dimension find for filetype {self.inputFileType}")
            return []
            # a method to return the list of support variables

        

