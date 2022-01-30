# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 15:25:15 2020

@author: hcorz
"""

"""
REMEMBER: 
#Non-live Battery Ruby/Sapphire always has 5A0 as its INIT SEED
#Initial seed is the 5th non-zero 4-digit seed reported. Example:
- 0
- 0
- 6073
- E97E7B6A
- 52713895
- 31B0DDE4
- DCD3 <- INIT SEED
"""
natureList = ['hardy','lonely','brave','adamant','naughty',
              'bold','docile','relaxed','impish','lax',
              'timid','hasty','serious','jolly','naive',
              'modest','mild','quiet','bashful','rash',
              'calm','gentle','sassy','careful','quirky']

genderThreshold = [31,63,127,191,225]

unownForms = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O',
              'P','Q','R','S','T','U','V','W','X','Y','Z','!','?']

#SHINY CHECK###################################################################
def shinyCheck(PID,TID,SID):
    PIDbin = _bin32(int(PID,16))
    high = int(PIDbin[2:18],2)
    low = int(PIDbin[18:],2)
    PIDxor = high ^ low
    TIDnSIDxor = TID ^ SID
    if TIDnSIDxor ^ PIDxor < 8:
        return True
    else:
        return False

#SEARCH RELATED################################################################
def shinyTrainerSearch(initSeed,
                       PID,
                       minFrame,
                       maxFrame,
                       superShiny = False):
    PIDbin = _bin32(int(PID,16))
    high = int(PIDbin[2:18],2)
    low = int(PIDbin[18:],2)
    PIDxor = high ^ low    
    frame = 1
    seed = int(simulateSeeds(initSeed,minFrame),16)
    for i in range(minFrame,maxFrame):
        TID,SID = seed2TIDnSID(seed)
        TIDnSIDxor = int(TID,16) ^ int(SID,16)
        if superShiny:
            if TIDnSIDxor ^ PIDxor == 0:
                frame = i - 72
                break
        else:
            if TIDnSIDxor ^ PIDxor < 8:
                frame = i - 72
                break
        seed = int(_advanceFrame(seed),16)
    return frame, TID, SID

def initSeedSearch(seedBase,
                   targetIVs,
                   maxFrame,
                   targetNature = None, targetAbility = None):
    for i in range(0xFFF):
        print('{0:f}%'.format( (i+1)/0xFFF*100 ))
        seed = seedBase+i
        frame, pokemon = search(seed,targetIVs,maxFrame,targetNature,targetAbility)
        IVBool = IVcheck(pokemon[1],targetIVs)
        extraBool = extraConditions(pokemon[2],targetNature,pokemon[3],targetAbility)
        if IVBool and extraBool:
            print(seed,frame,pokemon)
            break

def search(initSeed,
           targetIVs,
           maxFrame,
           targetNature = None, targetAbility = None):
    frame = 1
    seed = int(_advanceFrame(initSeed),16)
    for i in range(1,maxFrame):
        PID,IVs,nature,ability,gender = pokemon(seed)
        IVBool = IVcheck(IVs,targetIVs)
        extraBool = extraConditions(nature,targetNature,ability,targetAbility)
        if IVBool and extraBool:
            frame = i
            break
        seed = int(_advanceFrame(seed),16)
    return frame, pokemon(seed)

def IVcheck(IVs,targetIVs):
    for i in range(6):
        if IVs[i] >= targetIVs[i]:
            check = True
        else:
            check = False
            break
    return check

def extraConditions(nature,targetNature,ability,targetAbility):
    #Check nature
    if targetNature == None or targetNature == nature:
        natureCheck = True
    else:
        natureCheck = False
    #Check ability
    if targetAbility == None or targetAbility == ability:
        abilityCheck = True
    else:
        abilityCheck = False
    #Combine
    if natureCheck and abilityCheck:
        check = True
    else:
        check = False
    return check
        
#POKÉMON RELATED###############################################################
def pokemon(seed):
    PID = seed2PID(seed)
    IVs = seed2IVs(seed)
    nature = PID2Nature(PID)
    ability = PID2Ability(PID)
    gender = PID2Gender(PID)
    return PID,IVs,nature,ability,gender

#PID RELATED###################################################################
def PID2Gender(PID): #As in Gen 3
    genderValue = int(PID[-2:],16)%255
    gender = ['']*5
    for i in range(5):
        if genderValue >= genderThreshold[i]:
            gender[i] = 'M'
        else:
            gender[i] = 'F'
    return gender

def PID2Ability(PID): #As in Gen 3
    return int(PID[-1],16)%2

def PID2Nature(PID):
    base10 = int(PID,16)%25
    return natureList[base10]

def PID2UnownForm(PID):
    binString = _bin32(int(PID,16))
    p1 = binString[8:10]
    p2 = binString[16:18]
    p3 = binString[24:26]
    p4 = binString[32:]
    formString = '0b'+p1+p2+p3+p4
    base10 = int(formString,2)%28
    return unownForms[base10]

def PID2Wurmple(PID):
    binString = _bin32(int(PID,16))
    pw = binString[2:18]
    base10 = int(pw,2)%10
    if base10 <= 4:
        return 'Silcoon>Beautifly'
    else:
        return 'Cascoon>Dustox'

#SEED RELATED##################################################################
def seed2IVs(seed):
    ivSeed_1 = simulateSeeds(seed,2)
    ivSeed_2 = _advanceFrame(int(ivSeed_1,16))
    #Get two random number calls
    ivRNG_1 = int(ivSeed_1[2:6],16)
    ivRNG_2 = int(ivSeed_2[2:6],16)
    #Convert to bin16 string
    ivBin_1 = _bin16(ivRNG_1)
    ivBin_2 = _bin16(ivRNG_2)
#    #Get Def|Atk|HP IVs
    defIV = int(ivBin_1[3:8],2)
    atkIV = int(ivBin_1[8:13],2)
    hpIV = int(ivBin_1[13:],2)
#    #Get SpD|SpA|Spe IVs
    spDIV = int(ivBin_2[3:8],2)
    spAIV = int(ivBin_2[8:13],2)
    speIV = int(ivBin_2[13:],2)
    return hpIV,atkIV,defIV,spAIV,spDIV,speIV

def seed2TIDnSID(seed):
    PID = seed2PID(seed)
    TID,SID = PID2TIDnSID(PID)
    return TID,SID

def PID2TIDnSID(PID):
    TID = PID[0:4]
    SID = PID[4:]
    return TID,SID

def seed2PID(seed):
    half_2 = _hex8(seed)[2:6]
    half_1 = _advanceFrame(seed)[2:6]
    return (half_1+half_2).upper()

def simulateSeeds(initSeed,nFrames):
    seed = initSeed
    iSeed = _hex8(seed)
    for i in range(nFrames):
        iSeed = _advanceFrame(seed)
        seed = int(iSeed,16)
    return iSeed

def _advanceFrame(seed):
    nextSeed = (0x41C64E6D * seed + 0x6073)%0x100000000
    return _hex8(nextSeed)

def _hex8(number):
    hexString = hex(number)
    extraZeroes = '0'*(10 - len(hexString))
    hexNumber = hexString[:2] + extraZeroes + hexString[2:]
    return hexNumber

def _bin16(number):
    binString = bin(number)
    extraZeroes = '0'*(18 - len(binString))
    binNumber = binString[:2] + extraZeroes + binString[2:]
    return binNumber

def _bin32(number):
    binString = bin(number)
    extraZeroes = '0'*(34 - len(binString))
    binNumber = binString[:2] + extraZeroes + binString[2:]
    return binNumber