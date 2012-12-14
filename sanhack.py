#!/usr/bin/env python3

param_names = ["HHgascharge","HHsubsidy", "HHpvt", "HHCL", "HHCCO", "HHCOMRpercentage", "HHCHHR", "HHCHOR", "seedpercentage"]
variable_names = ["HHusercharge", "noclusters","periodTRclusters","periodTCclusters","periodprofclusters","cumprofclusters","periodinvest","periodinvestval","cuminvest","cuminvval","cumprofclusterslessinv","nooperators","cumrev","cumcost","cumprof"]

infile = open('input_parameters.txt')

def readparam():
    return eval(infile.readline().split(':')[1])

inputs = []
for i in range(13):
    inputs.append(readparam())

HHpopn, HHpercluster, Kcostcluster, clustsperoperator, HHgaschargerange, HHsubsidyrange, HHpvtrange, HHCLrange,\
        HHCCOrange, HHCOMRrange, HHCHHRrange, HHCHORrange, seedrange = inputs

def combinations(ranges):
    if len(ranges)==1:
        return list(map((lambda x: [x]), ranges[0]))
    result = []
    c = combinations(ranges[1:])
    for val in ranges[0]:
        for row in c:
            result.append([val]+row)
    return result

def simulate_scenario(params, numMonths):


    clusterpopn = HHpopn//HHpercluster
    capex = Kcostcluster * clusterpopn

    HHgascharge = params[0]
    HHsubsidy = params[1]
    HHpvt = params[2]
    HHCL = params[3]
    HHCCO = params[4]
    HHCOMRpercentage = params[5]*100
    HHCOMR = params[5] * Kcostcluster/12/HHpercluster # 12 = months per year
    HHCHHR = params[6]
    HHCHOR = params[7]
    seedpercentage = params[8]*100
    seed = params[8] * capex

    HHusercharge = HHCOMR + HHCL
    HHTR = HHgascharge + HHsubsidy + HHpvt + HHusercharge
    HHTC = HHCL + HHCCO + HHCOMR + HHCHHR + HHCHOR

    # First column

    noclusters = [int(params[8] * clusterpopn)]
    periodTRclusters = [noclusters[0] * HHTR * HHpercluster]*2
    periodTCclusters = [noclusters[0] * HHTC * HHpercluster]*2
    periodprofclusters = [periodTRclusters[0] - periodTCclusters[0]]*2
    cumprofclusters = periodprofclusters[:]
    periodinvest = [max([0,int(cumprofclusters[0]//Kcostcluster)])]
    periodinvestval = [periodinvest[0] * Kcostcluster]*2
    cuminvest = periodinvest[:]
    cuminvval = periodinvestval[:]
    cumprofclusterslessinv = [cumprofclusters[0] - periodinvest[0]*Kcostcluster]
    nooperators = [noclusters[0]//clustsperoperator]*2
    cumrev = periodTRclusters[:]
    cumcost = periodTCclusters[:]
    cumprof = [cumrev[0]-cumcost[0]]

    # Second column

    noclusters.append(int(noclusters[0] + periodinvest[0]))
    cumprofclusters[1] = cumprofclusterslessinv[0] + periodprofclusters[1]
    periodinvest.append(max([0,int(cumprofclusters[1]//Kcostcluster)]))
    periodinvestval[1] = periodinvest[0] * Kcostcluster
    cuminvest.append(cuminvest[0] + periodinvest[1])
    cuminvval[1] = cuminvest[1]*Kcostcluster
    cumprofclusterslessinv.append(cumprofclusters[1] - periodinvest[1]*Kcostcluster)
    cumrev[1] = cumrev[0] + periodTRclusters[1]
    cumcost[1] = cumcost[0] + periodTCclusters[1]
    cumprof.append(cumrev[1]-cumcost[1])

    for month in range(2,numMonths):
        noclusters.append(int(noclusters[month-1] + periodinvest[month-1]))
        periodTRclusters.append(noclusters[month] * HHTR * HHpercluster)
        periodTCclusters.append(noclusters[month] * HHTC * HHpercluster)
        periodprofclusters.append(periodTRclusters[month] - periodTCclusters[month])
        cumprofclusters.append(cumprofclusterslessinv[month-1] + periodprofclusters[month])
        periodinvest.append(max([0,int(cumprofclusters[month]//Kcostcluster)]))
        periodinvestval.append(periodinvest[month] * Kcostcluster)
        cuminvest.append(cuminvest[month-1] + periodinvest[month])
        cuminvval.append(cuminvest[month] * Kcostcluster)
        cumprofclusterslessinv.append(cumprofclusters[month] - periodinvest[month]*Kcostcluster)
        nooperators.append(noclusters[month]//clustsperoperator)
        cumrev.append(cumrev[month-1] + periodTRclusters[month])
        cumcost.append(cumcost[month-1] + periodTCclusters[month])
        cumprof.append(cumrev[month]-cumcost[month])

    return [HHusercharge, noclusters, periodTRclusters, periodTCclusters, periodprofclusters, cumprofclusters,\
            periodinvest, periodinvestval, cuminvest, cuminvval, cumprofclusterslessinv, \
            nooperators, cumrev, cumcost, cumprof]


def simulate_all(ranges, numMonths):
    print("Running...")
    datafile = open('datafile.csv', mode='w')
    scenario_id = 1
    frequencies = []
    for i in range(len(param_names)):
        param_freq = []
        for j in range(len(ranges[i])):
            param_freq.append([0])
        frequencies.append(param_freq)

    for params in combinations(ranges):
        scenario = simulate_scenario(params, numMonths)

        for i in range(len(param_names)):
            n = scenario[1][-1]
            param_val_ind = ranges[i].index(params[i])
            if n>=len(frequencies[i][param_val_ind]):
                frequencies[i][param_val_ind].extend([0]*(n - len(frequencies[i][param_val_ind])+1))
            frequencies[i][param_val_ind][n] += 1

        print('Scenario_id:, ' + str(scenario_id) + '\n' + print_simulation(params, scenario), end='\n', file=datafile)

        scenario_id += 1

    statsfile = open('statsfile.csv', mode='w')

    for i in range(len(param_names)):
        print('\n%s, Number scaled, Mean' %param_names[i], file = statsfile)
        for j in range(len(ranges[i])):
            print(str([ranges[i][j], sum(frequencies[i][j][115:]), sum([frequencies[i][j][n]*n for n in range(len(frequencies[i][j]))])/sum(frequencies[i][j])]+frequencies[i][j])[1:-1], file=statsfile)

    statsfile.close()
    datafile.close()

def print_simulation(params, scenario):
    out = ''

    params[5]*=100
    params[8]*=100

    i=0
    arr = params+scenario
    numMonths = len(scenario[1])

    for var in (param_names + variable_names):
        out += var + ':,'
        val = arr[i]
        i+=1
        if type(val)==type([]):
            valstring = str(list(map((lambda x: round(x,1)),val)))[1:-1]
        else:
            valstring = ((str(round(val, 2))+', ')*numMonths)[:-2]

        out += valstring + '\n'

    return out

simulate_all([HHgaschargerange, HHsubsidyrange, HHpvtrange, HHCLrange, HHCCOrange, HHCOMRrange, HHCHHRrange, HHCHORrange, seedrange], 60)
