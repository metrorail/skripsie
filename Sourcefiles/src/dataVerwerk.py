import xml.etree.ElementTree as ET
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from numpy.core.function_base import linspace
import datetime
import time
import json
from mpl_toolkits.axisartist.clip_path import atan2
from scipy.constants.constants import pi
import math
import random


nieBUPseries = {}
BUPseries = {}
# treine = {}
inleesTreine = {}
nommerLys = [] 
tydTrein = {}
# dagTreine = {}


def BUPinit():
    '''
    Inisialiseer die dictionaries BUPseries en nieBUPseries
    deur nieBUPseries.csv en BUPseries.csv in te lees
    nieBUPseries.csv: 'n CSV-leer met die treinseries wat nie met die gewone basisuurpatroon van 60 minute werk nie en hul bedryfsperiode. In die vorm 34,45 (treinserie,periode)
    BUPseries.csv: 'n CSV-leer met die treinseries wat wel volgens die basisuurpatroon diensreeling bedryf word en hul bedryfsperiode. In die vorm 01,12 (treinserie, periode)
    '''
    # Lees die treinseries in wat nie volgens die BUP bedryf word nie
    #nieBUPseries = {}
    with open('nieBUPseries.csv', "rb") as csvfile:
        nieBUPseriesReader = csv.reader(csvfile, delimiter=',')
        for serie in nieBUPseriesReader:
            if(serie.__len__()!=0):
                nieBUPseries[serie[0]] = int(serie[1])             
    #print nieBUPseries

    # Lees die treinseries wat wel volgens die BUP bedryf word in
    #BUPseries = {}
    with open('BUPseries.csv', "rb") as csvfile:
        BUPseriesReader = csv.reader(csvfile, delimiter=',')
        for serie in BUPseriesReader:
            if(serie.__len__()!=0):
                BUPseries[serie[0]] = int(serie[1])               
    #print BUPseries


def dataVerwerk(InputFile):
    '''
    Gebruik die toevoerleers wat deur CPLEX en die gebruiker geskep is om 'n 24 uur rooster te maak/#
     Toevoerleers: 
     @param InputFile: Afvoerleer van CPLEX in XML formaat met die tye in mod60 formaat
     @type InputFile: string in die vorm 'solution.sol'
     kmPunte.csv: 'n CSV-leer wat die stasies en hul afstand vanaf 'n verwysingspunt (soos Kaapstad) gee vir elke treinseries. In die vorm: 01SRX,3.72
    '''
    treinSerieStasieKmPunte = {}
    treinSerieLyne = {}
    treine = {}
    # Lees die afstand vanaf kaapstad in na 'n dictionary
    #treinSerieStasieKmPunte = {}
    with open('kmPunte.csv', "rb") as csvfile:
        kmPuntReader = csv.reader(csvfile, delimiter=',')
        for kmPunte in kmPuntReader:
            if(kmPunte.__len__()!=0):
                treinSerieStasieKmPunte[kmPunte[0]] = float(kmPunte[1])   
                treinSerieLyne[kmPunte[0]] = int(kmPunte[2])            
    
    # Skep 'n ElementTree van die xml toevoerleer
    tree = ET.parse(InputFile)
    root = tree.getroot()
    # Skep 'n lee dictionary vir die treine
    #treine = {}
    
    # Loop deur die XML-afvoer van CPLEX om die veranderlikes en hul waardes te onttrek
    for var in root.iter('variable'):
        # Stoor die huidige veranderlike naam
        varName = var.get('name')
        # Stoor die tipe veranderlike (X wat 'n treintyd aandui of p wat 'n hulpveranderlike is)
        tipeVar = varName[0:1]
        
        # Indien dit 'n treintyd is, moet dit in die treine dictionary gestoor word. 
        if(tipeVar == 'X'):
            # Onttrek die treinnnommer uit die veranderlike naam
            treinNo = varName[2:6]
            # Onttrek die betrokke stasiekode uit die veranderlike naam
            stasieKode = varName[7:10]
            #kry die treinserie en stasie sodat die km-punt uit treinseriestasiekmpunt gelees kan word
            treinSerieStasie = treinNo[0:2] + stasieKode
            # Kyk of die spesifieke trein al in die dictionary voorkom en indien wel:
            if(treine.has_key(treinNo)):
                treine[treinNo]['stasieKode'].append(stasieKode)
                # Verander die 'tyd' wat CPLEX bereken het na 'n wisselpunt getal vir python
                nuweTyd = (float(var.get('value')) + 60.0*treine[treinNo]['p'])/1440.0 +726709
                treine[treinNo]['tyd'].append(nuweTyd)
                treine[treinNo]['kmPunt'].append(treinSerieStasieKmPunte[treinSerieStasie])
                treine[treinNo]['trajek'].append(treinSerieLyne[treinSerieStasie])              
            # Die trein is nog nie in die dictionary nie
            else:
                # As die huidige trein 'n op-trein is (ewe treinnommer), moet die eindwaarde van die ooreenstemmende af-trein se p gebruik word vir die nuwe trein se begin p
                if(int(treinNo)%2 == 0):
                    vorigeP = treine['{:0>4}'.format(str(int(treinNo)-1))]['p']
                    nuweTyd = (float(var.get('value')) + 60.0*vorigeP)/1440.0 +726709
                    treine[treinNo] = {'stasieKode':[stasieKode], 'tyd':[nuweTyd], 'kmPunt':[treinSerieStasieKmPunte[treinSerieStasie]], 'trajek':[treinSerieLyne[treinSerieStasie]], 'p':vorigeP}
                else:
                    # Verander die 'tyd' wat CPLEX bereken het na 'n wisselpunt getal vir python
                    waarde = float(var.get('value'))
                    nuweTyd = waarde/1440.0 +726709
                    treine[treinNo] = {'stasieKode':[stasieKode], 'tyd':[nuweTyd], 'kmPunt':[treinSerieStasieKmPunte[treinSerieStasie]], 'trajek':[treinSerieLyne[treinSerieStasie]], 'p':0}
                # die cp veranderlike word later gebruik om die rooster vir 'n hele dag vol te maak.
                treine[treinNo]['cp'] = 0
        
        # Die huidige veranderlike is 'n hulpveranderlike wat aandui of die betrokke tydstip in die volgende uur val
        elif(tipeVar == 'p'):
            p = round(float(var.get('value')))
            # Kyk net eers of p 1 is, anders hoef dit niks te doen nie...
            if(p==1): 
                treinNo = varName[13:17]
                vorigeTydstipTreinNo = varName[2:6]
                
                # Kyk of die betrokke trein al in die dictionary is
                if(treine.has_key(treinNo)):
                    # Kyk of die p-veranderlike slegs oor een trein gaan
                    if(treinNo == vorigeTydstipTreinNo):
                        # Pas die trein se p-waarde aan
                        treine[treinNo]['p'] += 1
                        # Die vorige x-waarde wat ingelees is, is 'n uur te vroeg, tel dus 'n uur by.
                        treine[treinNo]['tyd'][-1] +=  1.0/24
                    # Die p waarde moet ook verander indien die huidige trein 'n op trein is wat in die volgende uur val as die aankomstyd van die ooreenstemmende af trein (bv aankoms was 50, maar omdraai se vertrek is 2)
                    elif(int(treinNo)%2 == 0 and (vorigeTydstipTreinNo == '{:0>4}'.format(str(int(treinNo)-1)))):
                        treine[treinNo]['p'] += 1
                        treine[treinNo]['tyd'][-1] +=  1.0/24
                else:
                    # Indien die program hier uitkom beteken dit 'n p veranderlike is in CPLEX verklaar (.lp toevoerleer) alvorens die X-veranderlike waarna hy verwys verklaar is.
                    # Indien die .lp leer reg opgestel is, behoort die program dus nooit hierdie boodskap te vertoon nie.
                    print 'o aarde, een p veranderlike het voor een X veranderlike voorgekom, hersien CPLEX se .lp toevoerleer!'
        else:
            continue
#             print varName, var.get('value')
    
    # Hierdie for-lus gaan deur die treine wat volgens 'n basisuurpatroon diensreeling bedryf word en maak seker dat die
    # volgorde van die treine reg is (maw, xx01 moet voor xx03 vertrek). Omdat die  
    for serie in BUPseries:        
        hoogsteTrein = 2*(60/BUPseries[serie])-2
        hetVerander = 1
        while(hetVerander):            
            hetVerander = 0
            for onewe in range(1,hoogsteTrein,2):                
                currTrein = serie + '{:0>2}'.format(onewe)
                volgTrein = serie + '{:0>2}'.format(onewe+2)                    
                if(treine[currTrein]['tyd'][0]>treine[volgTrein]['tyd'][0]):                    
                    currTreinOmdraai = serie + '{:0>2}'.format(onewe+1)
                    volgTreinOmdraai = serie + '{:0>2}'.format(onewe+3)
                    hetVerander = 1
                    tydelik = treine.pop(currTrein)
                    treine[currTrein] = treine[volgTrein]
                    treine[volgTrein] = tydelik
                    tydelik = treine.pop(currTreinOmdraai)
                    treine[currTreinOmdraai] = treine[volgTreinOmdraai]
                    treine[volgTreinOmdraai] = tydelik
    return treine

def dagDict(treine):
    dagtreine = {}
    
    # maak 'n dag se rooster vol van die basisuurpatroon en stoor dit in 'n CSV-formaat...
    nieBUPure = int(nieBUPseries.values()[0]/(60.0-nieBUPseries.values()[0]))    
    for cp in linspace(0,24-nieBUPure*2,24.0/nieBUPure-1):  # vir nieBUPure=3 (45 min periode): [0,3,6,9,12,15,18]
        # Stap deur die treine wat volgens treinnommer gesorteer is (begin dus by 0101 en eindig by 9999)
        for trein in sorted(treine):
            # Verwerk eers die treine wat nie volgens die BUP bedryf word nie
            if(nieBUPseries.has_key(trein[0:2])):
                
                # Die huidige trein moenie eindig met 01 nie en ook nie met 02 nie
                if(trein[2:4] != '01' and trein[2:4] != '02'):
                    vorigeTreinInSerieNo = '{:0>4}'.format(str(int(trein)-2))  
                    if(treine[trein]['tyd'][0] > treine[vorigeTreinInSerieNo]['tyd'][0]):
                        # val nog in selfe uur, hoef niks te doen nie.
                        treine[trein]['cp'] = treine[vorigeTreinInSerieNo]['cp']
                        tye = np.array(treine[trein]['tyd'])+treine[trein]['cp']/24.0
                       
                    else:
                        treine[trein]['cp'] = treine[vorigeTreinInSerieNo]['cp'] +1 
                        tye = np.array(treine[trein]['tyd'])+(treine[trein]['cp'])/24.0
                else:
                    treine[trein]['cp'] = cp/3*3
                    tye = np.array(treine[trein]['tyd'])+treine[trein]['cp']/24.0
                uniekeTreinno = '{:0>4}'.format(str(int(trein)+int(cp)/3*2*(nieBUPure+1)))
                dagtreine[uniekeTreinno] = {'stasieKode':treine[trein]['stasieKode'], 'tyd':tye.tolist(), 'kmPunt':treine[trein]['kmPunt'], 'trajek':treine[trein]['trajek']}                    
                
            # Verwerk dan die treine wat wel volgens die BUP werk
            elif(BUPseries.has_key(trein[0:2])): 
                for cpa in [cp, cp+1, cp+2]:
                    tye = np.array(treine[trein]['tyd'])+cpa/24.0
                    uniekeTreinno = '{:0>4}'.format(str(int(trein)+int(cpa)*2*(60/BUPseries[trein[0:2]])))
                    dagtreine[uniekeTreinno] = {'stasieKode':treine[trein]['stasieKode'], 'tyd':tye.tolist(), 'kmPunt':treine[trein]['kmPunt'], 'trajek':treine[trein]['trajek']}
            else:
                print 'FOUT: Treinserie ', trein, ' kom in die CPLEX-afvoer voor, maar die periode is nie bekend nie! \nGaan die leers BUPseries.csv en nieBUPseries.csv na.'
    with open("dagrooster.txt",'wb') as outfile:
        json.dump(dagtreine, outfile)
       
 
 
def leesDag():
    with open("dagrooster.txt") as f:
        dagTreine = json.load(f)#[u'specialKey']
    return dagTreine
  
       
def stipLeesData(dagTreine, serieStipDict,xMin,xMax):
    minTyd = xMin/24.0+726709
    minTydObjek = mpl.dates.num2date(minTyd)
    maksTyd = xMax/24.0+726709
    maksTydObjek = mpl.dates.num2date(maksTyd)
    fig = plt.figure(figsize=(23, 12))
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.04, right=0.96, bottom=0.04, top=0.96)
    maksY = 0
    # Gaan deur al die treine wat gestip moet word en kyk wat die maksimum KM-punt is
    # sodat die maksimum y-as waarde bepaal kan word
    # Gaan deur al die treine wat ingelees is
    for trein in sorted(dagTreine):
        # Kyk of die huidige trein gestip moet word
        if(serieStipDict.has_key(trein[0:2])):
		 # Kry die maksimum KM-punt van die huidige trein
            tempMaks = max(dagTreine[trein]['kmPunt'])
            if(maksY<tempMaks):
                maksY = tempMaks
    maksY = int(math.ceil(maksY/10.0))*10
    y=960.0/maksY
    yOffset = 0.015*maksY
    x=1840.0/(maksTyd-minTyd)

    # Stap deur die treine wat volgens treinnommer gesorteer is (begin dus by 0101 en eindig by 9999)
    for trein in sorted(dagTreine):
        # Kyk of die huidige trein gestip moet word
        if(serieStipDict.has_key(trein[0:2])):
            tye = mpl.dates.num2date(dagTreine[trein]['tyd'])
            # minuteLys word gebruik om die minute op die grafiek te stip.
            minuteLys = timeListToMinuteList(tye)
                            
            ax.plot_date(tye, dagTreine[trein]['kmPunt'], drawstyle = 'default', linestyle = '-', color = serieStipDict[trein[0:2]])
            # As treinnommer onewe is, is dit 'n AF-trein en moet die treinnommer by die eindbestemming gesit word
            if(int(trein)%2 == 1 and tye[-1] > minTydObjek and tye[-1] < maksTydObjek):
                    # Die helling van die lyn word bereken sodat die treinnommer parrallel daarop geplaas kan word.
                    ya = dagTreine[trein]['kmPunt'][-1] - dagTreine[trein]['kmPunt'][-2]
                    xa = mpl.dates.date2num(tye[-1])-mpl.dates.date2num(tye[-2])
                    hoek = atan2(ya*y, xa*x)*180/pi             
                    ax.text(tye[-1], dagTreine[trein]['kmPunt'][-1]-maksY*0.01, trein, horizontalalignment='right', verticalalignment='bottom', rotation=360-hoek)
            # As die treinnommer ewe is, is dit 'n OP-trein en moet die treinnommer by die oorsprongstasie gesit word
            elif(int(trein)%2 == 0 and tye[0] > minTydObjek and tye[0] < maksTydObjek):
                    ya = dagTreine[trein]['kmPunt'][0] - dagTreine[trein]['kmPunt'][1]
                    xa = mpl.dates.date2num(tye[1])-mpl.dates.date2num(tye[0])
                    hoek = atan2(ya*y, xa*x)*180/pi             
                    ax.text(tye[0], dagTreine[trein]['kmPunt'][0]-maksY*0.01, trein, horizontalalignment = 'left', verticalalignment = 'bottom', rotation=hoek)
            for a in range(dagTreine[trein]['kmPunt'].__len__()):
                # Sit die stasie waar dit plaasvind links
                ax.text(minTydObjek, dagTreine[trein]['kmPunt'][a], dagTreine[trein]['stasieKode'][a], horizontalalignment = 'right')
                if(tye[a]>minTydObjek and tye[a]< maksTydObjek):
                    # sit die minute waarop die gebeurtenis plaasvind op die grafiek
                    ax.text(minuteLys[a], dagTreine[trein]['kmPunt'][a]+yOffset, minuteLys[a].minute, horizontalalignment = 'right', rotation=90, fontsize=8)
      
        elif(serieStipDict.has_key(trein[0:2])):
            print 'FOUT: Treinserie ', trein, ' kom in die CPLEX-afvoer voor, maar die periode is nie bekend nie! \nGaan die leers BUPseries.csv en nieBUPseries.csv na.'
        else:
            pass
    
    ax.set_xlim(minTyd, maksTyd)
    ax.set_ylim(0,maksY)
    ax.invert_yaxis()
    ax.grid()    
#     print fig.canvas.get_width_height()
#     plt.grid()
    print 'Maak eers die Marvey-diagram toe alvorens die program verder gebruik word.'
    plt.show()
    
    
def dagNaCSV(dagTreine, OutputFile):
    # Stoor 'n dag se rooster in CSV-formaat
    with open(OutputFile,'wb') as csvfile:
        skryf = csv.writer(csvfile)
        # Stap deur die treine wat volgens treinnommer gesorteer is (begin dus by 0101 en eindig by 9999)
        for trein in sorted(dagTreine):
            # Skakel die tydstip om van 'n wisselpuntgetal sedert 1900 na 'n string in die vorm HH:MM:SS
            tye = mpl.dates.num2date(dagTreine[trein]['tyd'])
            skryfLys = timeListToStringList(tye)
            skryfLys.insert(0, trein)
            skryf.writerow(skryfLys)
            
 
def timeListToMinuteList(objekLys):
    minuteLys = []
    for objek in objekLys:
        minuut = objek.minute
        sek = int(round(objek.second + objek.microsecond/1000000.0))
        uur = objek.hour
        if(sek==60):
            sek = 0
            minuut += 1
        if(minuut == 60):
            minuut = 0
            uur += 1
        afgerond = objek.replace(minute = minuut, second = 30, hour = uur)
        minuteLys.append(afgerond)
    return minuteLys

def timeListToStringList(objekLys):
    tydLys = []
    for objek in objekLys:
        uur = objek.hour
        minuut = objek.minute
        sek = int(round(objek.second + objek.microsecond/1000000.0))
        if(sek==60):
            sek = 0
            minuut += 1
        if(minuut==60):
            minuut = 0
            uur += 1
        tydLys.append(str(datetime.time(uur,minuut,sek)))
    return tydLys

def stringListToTimeList(objekLys):
    tydLys = []
    for objek in objekLys:
        tydelik = datetime.datetime(*(time.strptime(("30-08-90 " + objek), "%d-%m-%y %H:%M:%S")[0:6]))
        tydLys.append(tydelik)
    return tydLys


def leesRooster(roosterInputFileName):
    '''
    Lees die CSV-file wie se naam as argument gestuur is in en laai dit in die dictionary inleesTreine
    Hoef slegs treine wat vanaf Kaapstad vertrek in ag te neem, want CPLEX het reeds die omdraaitye bepaal vir die op-ritte.
    LW: Indien 'n rooster geanaliseer moet word vanaf 'n 3e party, moet 'n trein met ewe-treinnommer die omdraai wees van die vorige onewe-treinnommer
    Bv: 3202 moet die omdraai van 3201 wees.
    '''
                
    tydTrein = {}
    inleesTreine= {}
    with open(roosterInputFileName, "rb") as csvfile:
        roosterReader = csv.reader(csvfile, delimiter=',')
        for trein in roosterReader:
            if(trein.__len__()!=0):
                timeLys = stringListToTimeList(trein[1:50])
                inleesTreine[trein[0]] = timeLys
                # Tydtrein is 'n tydlyn van al die vertrekke in 'n dag
                if(int(trein[0])%2==1):
                    dagminute = timeLys[0].time()
                    if(tydTrein.has_key(dagminute)):
                        tydTrein[dagminute].append(trein[0])
                    else:
                        tydTrein[dagminute] = [trein[0]]
    
    return tydTrein, inleesTreine


def omdraaie(omdraaiSeries, tydTrein, inleesTreine):
    tienMinute = datetime.timedelta(minutes = 10)
    omdraaiDict = {}
    stelwerking = {}
    
    with open(omdraaiSeries, "rb") as csvfile:
        omdraaiReader = csv.reader(csvfile, delimiter=',')
        for omdraaiPare in omdraaiReader:
            if(omdraaiPare.__len__()!=0):
                for serie in omdraaiPare[1:10]:
                    omdraaiDict[serie] = omdraaiPare[0]
    
    for tydstip in sorted(tydTrein):
        for trein in tydTrein[tydstip]:
            treinserie = trein[0:2]   
            ewe = '{:0>4}'.format(str(int(trein)+1))       
            if omdraaiDict[treinserie] in stelwerking:               
                verander = False
                for stel in sorted(stelwerking[omdraaiDict[treinserie]]['stelle']):
                    if(inleesTreine[trein][0] > (inleesTreine[stelwerking[omdraaiDict[treinserie]]['stelle'][stel][-1]][-1] + tienMinute)):
                        stelwerking[omdraaiDict[treinserie]]['stelle'][stel].extend((trein, ewe))   
                        verander = True
                        break                 
                if verander == False:
                    stelwerking[omdraaiDict[treinserie]]['stelle'][trein] = [trein, ewe]
            else:
                stelwerking[omdraaiDict[treinserie]] = {'stelle':{trein:[trein, ewe]}, 'CWNwag':[], 'nieCWNwag':[]}
#     print 'Hierdie diensregeling kort die volgende aantal stelle per lyn'
#     for lyne in sorted(stelwerking):
#         print lyne, stelwerking[lyne].__len__()#, sorted(stelwerking[lyne].keys())
#         for stel in sorted(stelwerking[lyne]):
#             print stelwerking[lyne][stel]
#     print ''
    stelbenutting = {}
#     print stelwerking
    print "Aantal stelle en benutting, Benuttingsgraad = (reistyd/(reistyd+staantyd))"
    print "--------------------------------------------------------------------------"
    totaleHoevStelle = 0
    for lyn in sorted(stelwerking):
        hoevStelle = 0
        benutting = 0
        print 'Lyn:',lyn,'aantal stelle benodig =',len(stelwerking[lyn]['stelle'])
        totaleHoevStelle += len(stelwerking[lyn]['stelle'])
        for stel in sorted(stelwerking[lyn]['stelle']):
            stelbenutting[stel] = {'reistyd':0,'staantyd':0}
            if(len(stelwerking[lyn]['stelle'][stel]) >4):
                for i in range(2,len(stelwerking[lyn]['stelle'][stel])):	#range(i, j) returns [i, i+1, i+2, ..., j-1];
                    currTreinNo = stelwerking[lyn]['stelle'][stel][i]
                    
                    tempStaantyd = (inleesTreine[currTreinNo][0] - inleesTreine[stelwerking[lyn]['stelle'][stel][i-1]][-1]).total_seconds()
                    tempReistyd = (inleesTreine[currTreinNo][-1] - inleesTreine[currTreinNo][0]).total_seconds()
                    if(tempReistyd > 0 and tempStaantyd>0):
                        # Hoef geen aanpassing te doen nie, beide tye is in dieselfde dag
#                         print currTreinNo, 'staan:', tempStaantyd, 'reis:', tempReistyd
                        pass
                    elif(tempReistyd < 0 and tempStaantyd>0):
                        # Reis val oor twee dae, moet reis aanpas
                        tempReistyd += 86400
#                         print currTreinNo, 'staan:', tempStaantyd, 'reis:', tempReistyd+86400, '(aangepas)'
                    elif(tempReistyd > 0 and tempStaantyd<0):
                        # Staan val oor twee dae, moet staan aanpas
                        tempStaantyd += 86400
#                         print currTreinNo, 'staan:', tempStaantyd+86400, 'reis:', tempReistyd, '(aangepas)'
                    else:
                        print "Daar is groot fout, beide die reis en die staan strek oor twee dae, bespreek jou kaartjie Oslo toe!"
                    stelbenutting[stel]['staantyd']+= tempStaantyd
                    stelbenutting[stel]['reistyd']+= tempReistyd
                    # Voeg die staantyd by die lys
                    # kaapstad staantyd sal deur ongelyke nommers gegee word
                    if(int(currTreinNo)%2==1):
                        stelwerking[lyn]['CWNwag'].append(tempStaantyd/60)
                    else:
                        stelwerking[lyn]['nieCWNwag'].append(tempStaantyd/60)
                # Bereken die benutting vir die lyn    
                hoevStelle +=1
                # Benutting vir die lyn word as die totale reistyd oor die som van die staan- en reistyd bereken
                benutting += (stelbenutting[stel]['reistyd'])/(stelbenutting[stel]['staantyd']+stelbenutting[stel]['reistyd'])
                print "Stel benuttingsgraad =", round((stelbenutting[stel]['reistyd'])/(stelbenutting[stel]['staantyd']+stelbenutting[stel]['reistyd'])*100,1),"%\t Eerste trein:", stel #stelwerking[lyn]['stelle'][stel]      
            else:
                print "Stel doen vier of minder ritte, dus kan sinvolle benutting nie bereken word nie\n", stelwerking[lyn]['stelle'][stel] 
        
        print "Gemiddelde staantyd by Kaapstad", int(round(np.average(stelwerking[lyn]['CWNwag']))), "\n(min =",int(round(np.min(stelwerking[lyn]['CWNwag']))) ,", max =",int(round(np.max(stelwerking[lyn]['CWNwag']))),", modus =", np.bincount(stelwerking[lyn]['CWNwag']).argmax(),", mediaan =",int(round(np.median(stelwerking[lyn]['CWNwag']))), ")"# \t\t"#, stelwerking[lyn]['CWNwag']
        print "Gemiddelde staantyd by omdraaistasie(s)", int(round(np.average(stelwerking[lyn]['nieCWNwag']))), "\n(min =",int(round(np.min(stelwerking[lyn]['nieCWNwag']))) ,", max =",int(round(np.max(stelwerking[lyn]['nieCWNwag']))),", modus =", np.bincount(stelwerking[lyn]['nieCWNwag']).argmax(),", mediaan =",int(round(np.median(stelwerking[lyn]['nieCWNwag']))), ")"# \t", stelwerking[lyn]['nieCWNwag']
        print "-------------------------------------"
        print "Gemiddelde benutting vir lyn =", round(benutting/hoevStelle*100,1), "%"
        print "=====================================\n"
    print "Totale aantal stelle benodig =", totaleHoevStelle,"\n\n"
        
 
def volgTyd(seriesLyneFileName, inleesTreine):
    # lyneTye word gebruik om vir elkeen van die lyne wat die gebruiker gespesifiseer het die aankoms- en vertrektye te stoor.
    # Die gebruiker gee in die seriesLyneFileName-file 'n lys van die netwerk se lyne en watter series oor elke lyn loop        
    lyneTye = {}
    
    with open(seriesLyneFileName, "rb") as csvfile:
        lyneSeriesReader = csv.reader(csvfile, delimiter=',')
        for lyn in lyneSeriesReader:
            if(lyn.__len__()!=0):
                lyneTye[lyn[0]] = {'series':lyn[1:10],'optye':[],'aftye':[], 'afdeltas':[],'opdeltas':[]}

    # Die program gaan deur die treine wat vanaf die .csv-file ingelees is om die aankoms- en vertrektye te kry vir 'n enkele basisuur of nie-basisuur (bv drie ure)
    # Hierdie tye word dan gebruik om die delta-verskille te bereken.
    for trein in sorted(inleesTreine):
        series = trein[0:2]
        for lyn in lyneTye:            
            if(series in lyneTye[lyn]['series']):                
                if(int(trein)%2 == 1):
                    # af trein (vergelyk begintye)
                    lyneTye[lyn]['aftye'].append(inleesTreine[trein][0].hour*60 + inleesTreine[trein][0].minute)
                else:
                    # op trein (vergelyk eindtye)
                    if(inleesTreine[trein][-1].hour==0 and int(trein[2:4])>20):
                        lyneTye[lyn]['optye'].append(24*60 + inleesTreine[trein][-1].minute)
                    else:
                        lyneTye[lyn]['optye'].append(inleesTreine[trein][-1].hour*60 + inleesTreine[trein][-1].minute)
                        
    kleure = ['red', 'crimson', 'maroon', 'chocolate', 'blue', 'teal', 'lime', 'green', 'black', 'gray', 'navy', 'olive', 'purple', 'silver', 'teal', 'yellow']
    kleur=0
    wydte = 60
    ind = np.arange(wydte)
    oubins = np.zeros(wydte)
    afDeltas = np.zeros(0)
    opDeltas = np.zeros(0)
    for lyn in lyneTye:
        lyneTye[lyn]['aftye'].sort()
        lyneTye[lyn]['optye'].sort()
        for a in range(len(lyneTye[lyn]['aftye'])-1):                
            lyneTye[lyn]['afdeltas'].append(lyneTye[lyn]['aftye'][a+1]- lyneTye[lyn]['aftye'][a])
            lyneTye[lyn]['opdeltas'].append(lyneTye[lyn]['optye'][a+1]- lyneTye[lyn]['optye'][a])
            
        binsAF = np.bincount(lyneTye[lyn]['afdeltas'],minlength=wydte)
        binsOP = np.bincount(lyneTye[lyn]['opdeltas'],minlength=wydte)
        len(lyneTye[lyn]['afdeltas'])
        afDeltas = np.append(afDeltas, lyneTye[lyn]['afdeltas'])
        opDeltas = np.append(opDeltas, lyneTye[lyn]['opdeltas'])
        
        plt.bar(ind, binsAF, width=1, hold=True, bottom=oubins, label=('%s af (Aantal treine: %d)' %(lyn, len(lyneTye[lyn]['afdeltas']))), color=kleure[kleur], align="center")
        oubins += binsAF
        kleur+=1
        plt.bar(ind, binsOP, width=1, hold=True, bottom=oubins, label=('%s op (Aantal treine: %d)' %(lyn, len(lyneTye[lyn]['opdeltas']))), color=kleure[kleur], align="center")
        oubins += binsOP
        kleur+=1                    
    
    print "Mediaan AF-volgtyd ", np.median(afDeltas), "~ Standaard afwyking AF-volgtyd ", np.around(np.std(afDeltas),1)
    print "Mediaan OP-volgtyd ", np.median(opDeltas), "~ Standaard afwyking OP-volgtyd ", np.around(np.std(opDeltas),1)
    plt.title("Volgtye", fontsize=40)
    plt.xlabel("Tyd", fontsize=30)
    
    plt.minorticks_on()
    plt.xticks(np.arange(0,wydte, step=1), fontsize=12)
    plt.xlim(0,40)
    maks = int(math.ceil(plt.axis()[3]/30.0))*30
    plt.yticks(np.arange(0,maks,step=maks/30, dtype=np.int))

    plt.ylabel("Aantal voorkomste", fontsize=30)
    plt.legend()
    print '\nMaak eers die Histogram toe alvorens die program verder gebruik word.'
    plt.show()

            
       
if __name__ == "__main__":
    BUPinit()
