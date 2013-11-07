def stipLeesDatafensie(dagTreine, serieStipDict,xMin,xMax):
    minTyd = xMin/24.0+726709
    minTydObjek = mpl.dates.num2date(minTyd)
    maksTyd = xMax/24.0+726709
    maksTydObjek = mpl.dates.num2date(maksTyd)
    fig = plt.figure(figsize=(23, 12))
    ax = [0, fig.add_subplot(311), fig.add_subplot(312), fig.add_subplot(313)]
    fig.subplots_adjust(left=0.04, right=0.96, bottom=0.04, top=0.96)
    y=320.0/80
    x=1840.0/(maksTyd-minTyd)
    # Stap deur die treine wat volgens treinnommer gesorteer is (begin dus by 0101 en eindig by 9999)
    for trein in sorted(dagTreine):
        # Verwerk eers die treine wat nie volgens die BUP bedryf word nie
        if(serieStipDict.has_key(trein[0:2])):
            tye = mpl.dates.num2date(dagTreine[trein]['tyd'])
            # minuteLys word gebruik om die minute op die grafiek te stip.
            minuteLys = timeListToMinuteList(tye)
            
            print dagTreine[trein]['trajek']
            trajekte = np.bincount(dagTreine[trein]['trajek'], minlength=5)
            print trajekte
                            
#             ax.plot_date(tye[:groter1], dagTreine[trein]['kmPunt'][:groter1], drawstyle = 'default', linestyle = '-', color = serieStipDict[trein[0:2]])
#             ax2.plot_date(tye[groter1:50], dagTreine[trein]['kmPunt'][groter1:50], drawstyle = 'default', linestyle = '-', color = serieStipDict[trein[0:2]])
#             ax3.plot_date(tye, dagTreine[trein]['kmPunt'], drawstyle = 'default', linestyle = '-', color = serieStipDict[trein[0:2]])
            # As treinnommer onewe is, is dit 'n AF-trein en moet die treinnommer by die eindbestemming gesit word
            if(int(trein)%2 == 1):
                ax[1].plot_date(tye[:trajekte[1]], dagTreine[trein]['kmPunt'][:trajekte[1]], drawstyle = 'default', linestyle = '-', color = serieStipDict[trein[0:2]])
                ax[2].plot_date(tye[trajekte[1]-1:trajekte[1]+trajekte[2]], dagTreine[trein]['kmPunt'][trajekte[1]-1:trajekte[1]+trajekte[2]], drawstyle = 'default', linestyle = '-', color = serieStipDict[trein[0:2]])
                ax[3].plot_date(tye[trajekte[1]-1:trajekte[1]+trajekte[3]], dagTreine[trein]['kmPunt'][trajekte[1]-1:trajekte[1]+trajekte[3]], drawstyle = 'default', linestyle = '-', color = serieStipDict[trein[0:2]])
                if(tye[-1] > minTydObjek and tye[-1] < maksTydObjek):
                    ya = dagTreine[trein]['kmPunt'][-1] - dagTreine[trein]['kmPunt'][-2]
                    xa = mpl.dates.date2num(tye[-1])-mpl.dates.date2num(tye[-2])
                    hoek = atan2(ya*y, xa*x)*180/pi 
    #                 print xa, ya, hoek               
                    ax[dagTreine[trein]['trajek'][-1]].text(tye[-1], dagTreine[trein]['kmPunt'][-1]-0.5, trein, horizontalalignment='right', verticalalignment='bottom', rotation=360-hoek)
            # As die treinnommer ewe is, is dit 'n OP-trein en moet die treinnommer by die oorsprongstasie gesit word
            elif(int(trein)%2 == 0):
                ax[1].plot_date(tye[-trajekte[1]:], dagTreine[trein]['kmPunt'][-trajekte[1]:], drawstyle = 'default', linestyle = '-', color = serieStipDict[trein[0:2]])
                ax[2].plot_date(tye[:trajekte[2]+1], dagTreine[trein]['kmPunt'][:trajekte[2]+1], drawstyle = 'default', linestyle = '-', color = serieStipDict[trein[0:2]])
                ax[3].plot_date(tye[:trajekte[3]+1], dagTreine[trein]['kmPunt'][:trajekte[3]+1], drawstyle = 'default', linestyle = '-', color = serieStipDict[trein[0:2]])
                if(tye[0] > minTydObjek and tye[0] < maksTydObjek):
                    ya = dagTreine[trein]['kmPunt'][0] - dagTreine[trein]['kmPunt'][1]
                    xa = mpl.dates.date2num(tye[1])-mpl.dates.date2num(tye[0])
                    hoek = atan2(ya*y, xa*x)*180/pi             
                    ax[dagTreine[trein]['trajek'][0]].text(tye[0], dagTreine[trein]['kmPunt'][0]-0.5, trein, horizontalalignment = 'left', verticalalignment = 'bottom', rotation=hoek)
            for a in range(dagTreine[trein]['kmPunt'].__len__()):
                # Sit die stasie waar dit plaasvind links
                ax[dagTreine[trein]['trajek'][a]].text(minTydObjek, dagTreine[trein]['kmPunt'][a], dagTreine[trein]['stasieKode'][a], horizontalalignment = 'right')
                if(tye[a]>minTydObjek and tye[a]< maksTydObjek):
                    # sit die minute waarop die gebeurtenis plaasvind op die grafiek
                    ax[dagTreine[trein]['trajek'][a]].text(tye[a], dagTreine[trein]['kmPunt'][a]+0.75, minuteLys[a], horizontalalignment = 'right', rotation=90, fontsize=7)
      
        elif(serieStipDict.has_key(trein[0:2])):
            print 'FOUT: Treinserie ', trein, ' kom in die CPLEX-afvoer voor, maar die periode is nie bekend nie! \nGaan die leers BUPseries.csv en nieBUPseries.csv na.'
        else:
            pass
    
    ax[1].set_xlim(minTyd, maksTyd)
    ax[2].set_xlim(minTyd, maksTyd)
    ax[3].set_xlim(minTyd, maksTyd)
    ax[1].invert_yaxis()
    ax[2].invert_yaxis()
    ax[3].invert_yaxis()
    ax[1].grid()
    ax[2].grid()
    ax[3].grid()
    # retrieve the pixel information:
#     xy_pixels = ax.transData.transform(np.vstack([x,y]).T)
#     xpix, ypix = xy_pixels.T
#     print xpix, ypix
#     print fig.canvas.get_width_height()
#     plt.grid()
    #plt.show()
    
    # def volgTydHist(seriesLyneFileName):
#     nieBUPure = int(nieBUPseries.values()[0]/(60.0-nieBUPseries.values()[0]))
#     # lyneTye word gebruik om vir elkeen van die lyne wat die gebruiker gespesifiseer het die aankoms- en vertrektye te stoor.
#     # Die gebruiker gee in die seriesLyneFileName-file 'n lys van die netwerk se lyne en watter series oor elke lyn loop        
#     lyneTye = {}
#     
#     with open(seriesLyneFileName, "rb") as csvfile:
#         lyneSeriesReader = csv.reader(csvfile, delimiter=',')
#         for lyn in lyneSeriesReader:
#             if(lyn.__len__()!=0):
#                 lyneTye[lyn[0]] = {'series':lyn[1:10],'optye':[],'aftye':[], 'afdeltas':[],'opdeltas':[]}
# 
#     # Die program gaan deur die treine wat vanaf die .csv-file ingelees is om die aankoms- en vertrektye te kry vir 'n enkele basisuur of nie-basisuur (bv drie ure)
#     # Hierdie tye word dan gebruik om die delta-verskille te bereken.
#     for trein in sorted(inleesTreine):
#         series = trein[0:2]
#         for lyn in lyneTye:            
#             if(series in lyneTye[lyn]['series']):                
#                 if(nieBUPseries.has_key(lyneTye[lyn]['series'][0])):
#                     hoogsteTrein = 2*(nieBUPure+1)                    
#                     if(int(trein[2:4]) <= hoogsteTrein):
#                         if(int(trein)%2 == 1):
#                             # af trein (vergelyk begintye)
#                             lyneTye[lyn]['aftye'].append(inleesTreine[trein][0].hour*60 + inleesTreine[trein][0].minute)
#                         else:
#                             # op trein (vergelyk eindtye)
#                             lyneTye[lyn]['optye'].append(inleesTreine[trein][-1].hour*60 + inleesTreine[trein][-1].minute)
#                 else:
#                     hoogsteTrein = 2*(60/BUPseries[series])
#                     if(int(trein[2:4]) <= hoogsteTrein):
#                         if(int(trein)%2 == 1):
#                             # af trein (vergelyk begintye)
#                             lyneTye[lyn]['aftye'].append(inleesTreine[trein][0].minute)
#                         else:
#                             # op trein (vergelyk eindtye)
#                             lyneTye[lyn]['optye'].append(inleesTreine[trein][-1].minute)
#     
#     for lyn in lyneTye:
#         lyneTye[lyn]['aftye'].sort()
#         lyneTye[lyn]['optye'].sort()
#         if(nieBUPseries.has_key(lyneTye[lyn]['series'][0])):
#             # Kopieer ook die eerste trein se tyd na die heel einde toe (omdat die rooster siklies is, moet daardie volgtyd ook in ag geneem word...)
#             lyneTye[lyn]['aftye'].append(lyneTye[lyn]['aftye'][0]+nieBUPure*60)
#             lyneTye[lyn]['optye'].append(lyneTye[lyn]['optye'][1]+nieBUPure*60)
#             lyneTye[lyn]['optye'][0] += nieBUPure*60
#             lyneTye[lyn]['optye'].sort()
#             for a in range(len(lyneTye[lyn]['aftye'])-1):                
#                 lyneTye[lyn]['afdeltas'].append(lyneTye[lyn]['aftye'][a+1]- lyneTye[lyn]['aftye'][a])
#                 lyneTye[lyn]['opdeltas'].append(lyneTye[lyn]['optye'][a+1]- lyneTye[lyn]['optye'][a])
# #             print lyneTye[lyn]['afdeltas']
# #             print lyneTye[lyn]['opdeltas']
#             plt.hist(lyneTye[lyn]['afdeltas'],bins=len(lyneTye[lyn]['afdeltas']), normed=False,alpha=0.5, label=lyn)
#             
#         else:
#             # Kopieer ook die eerste trein se tyd na die heel einde toe (omdat die rooster siklies is, moet daardie volgtyd ook in ag geneem word...)
#             lyneTye[lyn]['aftye'].append(lyneTye[lyn]['aftye'][0]+60)
#             lyneTye[lyn]['optye'].append(lyneTye[lyn]['optye'][0]+60)
#             for a in range(len(lyneTye[lyn]['aftye'])-1):
#                 lyneTye[lyn]['afdeltas'].append(lyneTye[lyn]['aftye'][a+1]- lyneTye[lyn]['aftye'][a])
#                 lyneTye[lyn]['opdeltas'].append(lyneTye[lyn]['optye'][a+1]- lyneTye[lyn]['optye'][a])
# #             print lyneTye[lyn]['afdeltas']
#             
#             plt.hist(lyneTye[lyn]['afdeltas'],bins=len(lyneTye[lyn]['afdeltas']), normed=False,alpha=0.5, label=lyn, hold=True)
# #             plt.hist(lyneTye[lyn]['afdeltas'],bins=25, normed=False, label=lyn, hold=True)
# #             print lyneTye[lyn]['opdeltas']
#     plt.title("Volgtye")
#     plt.xlabel("Tyd")
#     plt.xlim(0,25)
#     plt.minorticks_on()
#     plt.grid(which='minor', axis='x')
#     plt.ylabel("Aantal voorkomste")
#     plt.legend()
#     print 'Maak eers die Marvey-diagram toe alvorens die program verder gebruik word.'
#     plt.show()   