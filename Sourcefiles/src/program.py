import sys
import os
sys.path.append("/usr/share/pyshared")
sys.path.append("/usr/local/lib/python2.7/dist-packages")
sys.path.append("/usr/local/lib/python2.7/site-packages/")

# import CPLEXoplosser
import dataVerwerk as dv

def clear():
    os.system('cls' if os.name=='nt' else 'clear')
    
    
if __name__ == "__main__":
    dv.BUPinit()
    clear()
    print 'Welkom'
    while(1):
        while True:
            try:                
                por = """Kieslys
                1: Los wiskundige model op (slegs indien CPLEX geinstalleer is)
                2: Brei die BUP uit tot 'n volle dag
                3: Stip die rooster as 'n Marvey-diagram
                4: Voer die dag-rooster uit na 'n CSV-file
                5: Lees 'n dag-rooster in vanaf 'n CSV-file
                6: Gee opsomming van omdraai-tye
                7: Gee opsomming van volg-tye
                8: Gaan uit
                Kies asseblief een van die bg opsies: """
                keuse = input(por)
                break
            except SyntaxError:
                print "Tik slegs die funksie-nommer. Bv 1 en dan <ENTER>\n"
        
        if(keuse==1):            
            prompt = """Enter the path to a file with .lp extension
            The path must be entered as a string; e.g. "my_model.lp"\n """
            fname = input(prompt)
            CPLEXoplosser.CPLEXoplosser(fname)
        elif(keuse==2):
            clear()
            treine = dv.dataVerwerk('solution.sol')
            dv.dagDict(treine)            
        elif(keuse==3):
            clear()
            dagTreine = dv.leesDag() 
            print "Verskaf asseblief die treinseries en kleurkodes wat vertoon moet word\n Gee in die vorm {'serie1':'kleur1','serie2':'kleur2'...} \n bv. {'34':'c', '32':'m'} <ENTER>"
            por1 = """Beskikbare kleure: 'b': blue, 'g': green, 'r': red, 'c': cyan,\n\t\t'm': magenta, 'y': yellow, 'k': black\n"""
            while True:
                try:
                    series = input(por1)
                    break
                except SyntaxError:
                    print "Stadig nou! Verskaf asseblief die treinseries en kleurkodes in die gegewe formaat.\n Bv. {'34':'c', '32':'m'} <ENTER>"                           
                except NameError:
                    print "Stadig nou! Verskaf asseblief die treinseries en kleurkodes in die gegewe formaat.\n Bv. {'34':'c', '32':'m'} <ENTER>"
            
            while True:
                try:
                    por2 = """\nVerskaf asseblief die beginuur van die Marvey-diagram.\n Bv vir 6vm, tik 6 <ENTER>, vir 3nm, tik 15 <ENTER>\n"""
                    begin = int(input(por2))
                    break
                except TypeError:
                    print "Stadig nou! Sleutel SLEGS die GETAL in wat die uur voorstel tussen 0 en 23"
                except NameError:
                    print "Stadig nou! Sleutel SLEGS die GETAL in wat die uur voorstel tussen 0 en 23"
            while True:
                try:
                    por3 = """Verskaf asseblief die eind-uur van die Marvey-diagram.\n Bv vir 9vm, tik 9 <ENTER>, vir 6nm, tik 18 <ENTER>\n"""
                    einde = int(input(por3))
                    break
                except TypeError:
                    print "Stadig nou! Sleutel SLEGS die getal in wat die uur voorstel tussen 0 en 23"
                except NameError:
                    print "Stadig nou! Sleutel SLEGS die GETAL in wat die uur voorstel tussen 0 en 23"
                    
            
            while True:
                try:
                    dv.stipLeesData(dagTreine, series,begin, einde)#,'01':'r','90':'b', '05':'g', '94':'c', '95':'m', '99':'y', '28':'r'})'34':'c', '32':'m', '35':'y', '23':'k'
                    break
                except AttributeError:
                    print "Stadig nou! Die formaat vir treinseries en kleurkodes is ongeldig.\n Verskaf asseblief die treinseries en kleurkodes in die gegewe formaat.\n Bv. {'34':'c', '32':'m'} <ENTER>"
                    series = input(por1)
            clear()
        elif(keuse==4):
            clear()
            dagTreine = dv.leesDag() 
            dv.dagNaCSV(dagTreine, 'rooster.csv')
            print 'Geskryf na rooster.csv'
        elif(keuse==5):
            print 'Deel van 6 en 7 se programvloei'
        elif(keuse==6):
            clear()
            while True:
                try:                            
                    print "Volgtyd: Verskaf asseblief die file-naam en uitbreiding van die rooster wat verwerk moet word."
                    por = """Dit moet in die vorm wees 'rooster.csv'\n"""
                    roosterNaam = input(por)
                    tydTrein, inleesTreine = dv.leesRooster(roosterNaam)
                    break
                except NameError:
                    print "Stadig nou! Daar was fout met die file-naam wat verskaf is.\n Maak seker dit bevat die uitbreiding aanhalingstekens.\n"
                except SyntaxError:
                    print "Stadig nou! Daar was fout met die file-naam wat verskaf is.\n Maak seker dit bevat die uitbreiding aanhalingstekens.\n"
            print "Rooster ", roosterNaam, " is suksesvol gelaai."
            
            while True:
                try:                    
                    print "Verskaf asseblief die file-naam en uitbreiding wat die lyne wat stelle deel definieer."
                    por = """Dit moet in die vorm wees 'omdraaie.csv'
                    Die file-inhoud moet 'n reel vir elke groep lyne bevat
                    en al die treinseries wat stelle deel
                    in die vorm: Naam,serie1,serie2. Byvoorbeeld: 
                    SUID,01,02,03
                    VLAKTE,05,06\n"""
                    series = input(por)
                    dv.omdraaie(series, tydTrein, inleesTreine)
                    break
                except NameError:
                    print "Stadig nou! Daar was fout met die file-naam wat verskaf is.\n Maak seker dit bevat die uitbreiding aanhalingstekens.\n"
                except SyntaxError:
                    print "Stadig nou! Daar was fout met die file-naam wat verskaf is.\n Maak seker dit bevat die uitbreiding aanhalingstekens.\n"

        elif(keuse==7):
            clear()
            while True:
                try:                            
                    print "Volgtyd: Verskaf asseblief die file-naam en uitbreiding van die rooster wat verwerk moet word."
                    por = """Dit moet in die vorm wees 'rooster.csv'\n"""
                    roosterNaam = input(por)
                    inleesTreine = dv.leesRooster(roosterNaam)[1]
                    break
                except NameError:
                    print "Stadig nou! Daar was fout met die file-naam wat verskaf is.\n Maak seker dit bevat die uitbreiding aanhalingstekens.\n"
                except SyntaxError:
                    print "Stadig nou! Daar was fout met die file-naam wat verskaf is.\n Maak seker dit bevat die uitbreiding aanhalingstekens.\n"
            print "Rooster ", roosterNaam, " is suksesvol gelaai."
            
            while True:
                try:                    
                    print "Verskaf asseblief die file-naam en uitbreiding wat die trajekte definieer."
                    por = """Dit moet in die vorm wees 'serieslyne.csv'
                    Die file-inhoud moet 'n reel vir elke trajek bevat
                    en al die treinseries wat oor daardie trajek beweeg
                    in die vorm: Naam,serie1,serie2. Byvoorbeeld: 
                    Noord,23,32,34
                    Suid,01,02,03\n"""
                    series = input(por)
                    dv.volgTyd(series, inleesTreine)
                    break
                except NameError:
                    print "Stadig nou! Daar was fout met die file-naam wat verskaf is.\n Maak seker dit bevat die uitbreiding aanhalingstekens.\n"
                except SyntaxError:
                    print "Stadig nou! Daar was fout met die file-naam wat verskaf is.\n Maak seker dit bevat die uitbreiding aanhalingstekens.\n"
            clear()
                    
        elif(keuse==8):
            sys.exit(-1)
        else:
            print 'totsiens'
        
# sudo mv python pythonSTOP
# python path vir cplex: /opt/ibm/ILOG/CPLEX_Studio1251/cplex/python/x86-64_sles10_4.1
# installeeer alles: sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose

# matplotlib:  sudo apt-get install python-matplotlib
#sudo apt-get install python-matplotlib
#luca@ubuntu:~/workspace/CPLEXtut/src$ python program.py
# Traceback (most recent call last):
#   File "program.py", line 2, in <module>
#     import dataVerwerk as dv
#   File "/home/luca/workspace/CPLEXtut/src/dataVerwerk.py", line 3, in <module>
#     import matplotlib.pyplot as plt
