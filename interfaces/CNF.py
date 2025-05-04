import os
from math import ceil, log, sqrt, e
from copy import deepcopy
import random
import tempfile

from WAPS.waps import sampler as samp
from interfaces.weightcount.weighted_to_unweighted import *

SAMPLER_QUICKSAMPLER = 2
SAMPLER_STS = 3
SAMPLER_CMS = 4
SAMPLER_APPMC3 = 5
SAMPLER_WCMS = 6
SAMPLER_SPUR = 7

SAMPLER_CUSTOM = 8

def getSolutionFromCustomSampler(self, inputFile, numSolutions, indVarList):
    solreturnList = []
    # write your code here

    return solreturnList

# returns List of Independent Variables


def parseIndSupport(indSupportFile):
    with open(indSupportFile, 'r') as f:
        lines = f.readlines()

    indList = []
    numVars = 0
    for line in lines:
        if line.startswith('p cnf'):
            fields = line.split()
            numVars = int(fields[2])

        if line.startswith('c ind'):
            line = line.strip().replace('c ind', '').replace(
                ' 0', '').strip().replace('v ', '')
            indList.extend(line.split())

    if len(indList) == 0:
        indList = [int(x) for x in range(1, numVars+1)]
    else:
        indList = [int(x) for x in indList]
    return indList

def check_cnf(fname):
    with open(fname, 'r') as f:
        lines = f.readlines()

    given_vars = None
    given_cls = None
    cls = 0
    max_var = 0

    for line in lines:
        line = line.strip()
        if len(line) == 0:
            print("ERROR: CNF is incorrectly formatted, empty line!")
            return False

        line = line.split()
        line = [l.strip() for l in line]

        if line[0] == "p":
            assert len(line) == 4
            assert line[1] == "cnf"
            given_vars = int(line[2])
            given_cls = int(line[3])
            continue

        if line[0] == "c":
            continue

        if line[0] == "w":
            assert len(line) == 3
            var = int(line[1])
            weight = float(line[2])
            assert (0 <= weight <= 1)
            max_var = max(var, max_var)
            continue

        cls += 1
        for l in line:
            var = abs(int(l))
            max_var = max(var, max_var)

    if max_var > given_vars:
        print("ERROR: Number of variables given is LESS than the number of variables used")
        print("ERROR: Vars in header: %d   max var: %d" %
              (given_vars, max_var))
        return False

    if cls != given_cls:
        print("ERROR: Number of clauses in header is DIFFERENT than the number of clauses in the CNF")
        print("ERROR: Clauses in header: %d   clauses: %d" % (given_cls, cls))
        return False

    return True

class cnf:
    def __init__(self, samplerType, weighted_inputFile):
        inputFileSuffix = weighted_inputFile.split('/')[-1][:-4]
        self.tempFile = tempfile.gettempdir() + "/" + inputFileSuffix+"_t.cnf"
        self.support_vars = parseIndSupport(weighted_inputFile)
        self.samplerType = samplerType
        self.samplerString = self.get_sampler_string(samplerType)
        self.unweighting = None
        inputFilePrefix = weighted_inputFile.split("/")[-1][:-4]
        self.inputFile = inputFilePrefix + \
            "."+str(self.samplerType)+".cnf"

        lines = []
    
        if samplerType == SAMPLER_WCMS:
            self.unweighting = False
        else:
            self.unweighting = True

        if self.unweighting == True:
            c = Converter(precision=2)  # precision set to 4
            with open(weighted_inputFile, 'r') as f:
                lines = f.readlines()
            self.indVarList = list(c.transform(lines, self.inputFile))
            print("This is the output file after weighted to unweighted:",
              self.inputFile)
        else:
            print("here")
            self.indVarList = self.support_vars
            with open(weighted_inputFile, 'r') as first, open(self.inputFile,'w') as second:
                for line in first:
                    second.write(line)


    def get_sampler_string(self, samplerType):
        if samplerType == SAMPLER_APPMC3:
            return 'AppMC3'
        if samplerType == SAMPLER_QUICKSAMPLER:
            return 'QuickSampler'
        if samplerType == SAMPLER_STS:
            return 'STS'
        if samplerType == SAMPLER_CMS:
            return 'CMSGen'
        if samplerType == SAMPLER_WCMS:
            return 'WCMSGen'
        if samplerType == SAMPLER_SPUR:
            return 'SPUR'
        print("ERROR: unknown sampler type")
        exit(-1)

    def create_subcond_query(self,query):
        
        outputFile = self.tempFile
        
        #to clear the file
        open(outputFile, "w").close()

        with open(self.inputFile,'r') as firstfile, open(outputFile,'w') as secondfile:
            condition = "\n".join([str(i)+" 0" for i in query])
            for line in firstfile:
                if line.startswith("p cnf"):
                    fields = line.split()
                    numClauses = int(fields[3])
                    line = " ".join(fields[:-1])
                    line += f" {numClauses + len(query)}\n" 
                secondfile.write(line)   
            secondfile.write(condition)
        self.conditioned_file = outputFile          
        
 

    def subcond(self, numSamp, prefix_query, seed):
        samplerType = self.samplerType

        topass_withseed = (self.conditioned_file, numSamp, self.indVarList, seed)

        ok = check_cnf(self.conditioned_file)

        if not ok:
            print(
                "ERROR: CNF is malformatted. Sampler may give wrong solutions in this case. Exiting.")
            print("File is: %s" % self.conditioned_file)
            exit(-1)

    #    print("Using sampler: %s" % self.get_sampler_string(samplerType))

        if (samplerType == SAMPLER_APPMC3):
            sols, seed = self.getSolutionFromAppMC3(*topass_withseed)

        elif (samplerType == SAMPLER_QUICKSAMPLER):
            sols, seed = self.getSolutionFromQuickSampler(*topass_withseed)

        elif (samplerType == SAMPLER_STS):
            sols, seed = self.getSolutionFromSTS(*topass_withseed)

        elif (samplerType == SAMPLER_CMS or samplerType == SAMPLER_WCMS):
            sols, seed = self.getSolutionFromCMSsampler(*topass_withseed)

        elif (samplerType == SAMPLER_SPUR):
            sols, seed = self.getSolutionFromSpur(*topass_withseed)

        else:
            print("Error: No such sampler!")
            exit(-1)

#        print("Number of solutions returned by sampler:", len(sols))
        
        solList = []

        for sol in sols:
            projection = []
            for lit in sol:
                if lit not in prefix_query and abs(lit) in self.support_vars:
                    projection.append(lit)
            solList.append(projection)

        return solList

    def sample(self, numSamp, seed):
        samplerType = self.samplerType
        
        topass_withseed = (self.inputFile, numSamp, self.indVarList, seed)

        ok = check_cnf(self.inputFile)

        if not ok:
            print(
                "ERROR: CNF is malformatted. Sampler may give wrong solutions in this case. Exiting.")
            print("File is: %s" % self.inputFile)
            exit(-1)

       # print("Using sampler: %s" % self.get_sampler_string(samplerType))
        if (samplerType == SAMPLER_APPMC3):
            sols, seed = self.getSolutionFromAppMC3(*topass_withseed)

        elif (samplerType == SAMPLER_QUICKSAMPLER):
            sols, seed = self.getSolutionFromQuickSampler(*topass_withseed)

        elif (samplerType == SAMPLER_STS):
            sols, seed = self.getSolutionFromSTS(*topass_withseed)

        elif (samplerType == SAMPLER_CMS or samplerType == SAMPLER_WCMS):
            sols, seed = self.getSolutionFromCMSsampler(*topass_withseed)

        elif (samplerType == SAMPLER_SPUR):
            sols, seed = self.getSolutionFromSpur(*topass_withseed)

        else:
            print("Error: No such sampler!")
            exit(-1)

        #print("Number of solutions returned by sampler:", len(sols))
        
        solList = []

        for sol in sols:
            projection = []
            for lit in sol:
                if abs(lit) in self.support_vars:
                    projection.append(lit)
            solList.append(projection)

        return solList, seed

    @staticmethod
    def getSolutionFromAppMC3(inputFile, numSolutions, indVarList,  newSeed):
        # must construct: ./approxmc3 -s 1 -v2 --sampleout /dev/null --samples 500
        inputFileSuffix = inputFile.split('/')[-1][:-4]
        tempOutputFile = tempfile.gettempdir()+'/'+inputFileSuffix+".txt"

        cmd = './samplers/unigen --arjun 0 -s ' + \
            str(newSeed) + ' -v 0 --samples ' + str(numSolutions)
        cmd += ' --sampleout ' + str(tempOutputFile)
        cmd += ' ' + inputFile + ' > /dev/null 2>&1'
        os.system(cmd)

        with open(tempOutputFile, 'r') as f:
            lines = f.readlines()

        solList = []
        for line in lines:
            sol = []
            lits = line.strip().split(" ")[:-1]
            for y in indVarList:
                if str(y) in lits:
                    sol.append(y)

                if "-" + str(y) in lits:
                    sol.append(-y)
            solList.append(sol)
        
        solreturnList = solList
        if len(solList) == 0:
            print("No solution returned")
            print(cmd)
            exit(0)
        elif len(solList) > numSolutions:
            solreturnList = random.sample(solList, numSolutions)

        os.unlink(str(tempOutputFile))
        return solreturnList, newSeed+1

    @staticmethod
    def getSolutionFromQuickSampler( inputFile, numSolutions, indVarList,  newSeed):
        cmd = "./samplers/quicksampler -n " + \
            str(numSolutions*5)+' '+str(inputFile)+' > /dev/null 2>&1'
        os.system(cmd)
        cmd = "./samplers/z3 "+str(inputFile)+' > /dev/null 2>&1'
        os.system(cmd)

        with open(inputFile+'.samples', 'r') as f:
            lines = f.readlines()

        with open(inputFile+'.samples.valid', 'r') as f:
            validLines = f.readlines()

        solList = []
        for j in range(len(lines)):
            if (validLines[j].strip() == '0'):
                continue
            fields = lines[j].strip().split(':')
            sol = []
            i = 0
            # valutions are 0 and 1 and in the same order as c ind.
            for x in list(fields[1].strip()):
                if (x == '0'):
                    sol.append(-1*indVarList[i])
                else:
                    sol.append(indVarList[i])
                i += 1
            solList.append(sol)

        solreturnList = solList
        if len(solList) == 0:
            print("No solution returned")
            print(cmd)
            exit(0)
        elif len(solList) > numSolutions:
            solreturnList = random.sample(solList, numSolutions)
        elif len(solreturnList) < numSolutions:
            print("Error: Quicksampler did not find required number of solutions")
            solreturnList = random.choices(solList, k=numSolutions)

           # exit(1)

        os.unlink(inputFile+'.samples')
        os.unlink(inputFile+'.samples.valid')

        return solreturnList, newSeed+1

    @staticmethod
    def getSolutionFromSpur(inputFile, numSolutions, indVarList,  newSeed):
        inputFileSuffix = inputFile.split('/')[-1][:-4]
        tempOutputFile = tempfile.gettempdir()+'/'+inputFileSuffix+".out"
        cmd = './samplers/spur -seed %d -q -s %d -out %s -cnf %s' % (
            newSeed, numSolutions, tempOutputFile, inputFile)
        os.system(cmd)

        with open(tempOutputFile, 'r') as f:
            lines = f.readlines()

        solList = []
        startParse = False
        for line in lines:
            if (line.startswith('#START_SAMPLES')):
                startParse = True
                continue
            if (not (startParse)):
                continue
            if (line.startswith('#END_SAMPLES')):
                startParse = False
                continue
            fields = line.strip().split(',')

            solCount = int(fields[0])
            sol = []

            i = 1
            for x in list(fields[1]):
                if (x == '0'):
                    sol.append(-i)
                else:
                    sol.append(i)
                i += 1

            for i in range(solCount):
                solList.append(sol)

        os.unlink(tempOutputFile)
        return solList, newSeed+1

    @staticmethod
    def getSolutionFromSTS( inputFile, numSolutions, indVarList,  newSeed):
        kValue = 50
        samplingRounds = numSolutions/kValue + 1
        inputFileSuffix = inputFile.split('/')[-1][:-4]
        outputFile = tempfile.gettempdir()+'/'+inputFileSuffix+".out"
        cmd = './samplers/STS -k=' + \
            str(kValue)+' -nsamples='+str(samplingRounds)+' '+str(inputFile)
        cmd += ' > '+str(outputFile)
        os.system(cmd)

        with open(outputFile, 'r') as f:
            lines = f.readlines()

        solList = []
        shouldStart = False
        for j in range(len(lines)):
            if (lines[j].strip() == 'Outputting samples:' or lines[j].strip() == 'start'):
                shouldStart = True
                continue
            if (lines[j].strip().startswith('Log') or lines[j].strip() == 'end'):
                shouldStart = False
            if (shouldStart):

                i = 0
                sol = []
                # valutions are 0 and 1 and in the same order as c ind.
                for x in list(lines[j].strip()):
                    if (x == '0'):
                        sol.append(-indVarList[i])
                    else:
                        sol.append(indVarList[i])
                    i += 1
                solList.append(sol)

        if len(solList) == 0:
            print("No solution returned")
            print(cmd)
            exit(0)
        elif len(solList) < numSolutions:
            #print("STS Did not find required number of solutions")
            #we extend the sollist
            solList = random.choices(solList, k=numSolutions)  
            #sys.exit(1)
        elif len(solList) > numSolutions:
            solList = random.sample(solList, numSolutions)

        os.unlink(outputFile)
        return solList, newSeed+1

    @staticmethod
    def getSolutionFromCMSsampler( inputFile, numSolutions, indVarList,  newSeed):
        inputFileSuffix = inputFile.split('/')[-1][:-4]
        outputFile = tempfile.gettempdir()+'/'+inputFileSuffix+".out"
        cmd = "./samplers/cmsgen --seed " + str(newSeed) + " --samples " + str(numSolutions)
        cmd += " " + inputFile
        cmd += " --samplefile " + outputFile + " > /dev/null 2>&1"
        os.system(cmd)

        with open(outputFile, 'r') as f:
            lines = f.readlines()

        solList = []
        for line in lines:
            if line.strip() == 'SAT':
                continue

            sol = []
            lits = line.split(" ")
            for y in indVarList:
                if str(y) in lits:
                    sol.append(y)

                if "-" + str(y) in lits:
                    sol.append(-y)
            solList.append(sol)

        solreturnList = solList
      
        if len(solList) == 0:
            print("No solution returned")
            print(cmd)
            exit(0)
        elif len(solList) > numSolutions:
            solreturnList = random.sample(solList, numSolutions)
        elif len(solList) < numSolutions:
            print("cryptominisat5 Did not find required number of solutions")
            solreturnList = random.choices(solList, k=numSolutions)
            #sys.exit(1)
        os.unlink(outputFile)
        return solreturnList, newSeed+1
