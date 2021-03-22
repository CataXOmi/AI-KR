"""
Dati enter dupa fiecare solutie afisata.

Presupunem ca avem costul de mutare al unui bloc egal cu indicele in alfabet, cu indicii incepănd de la 1 (care se calculează prin 1+ diferenta dintre valoarea codului ascii al literei blocului de mutat si codul ascii al literei "a" ) . Astfel A* are trebui sa prefere drumurile in care se muta intai blocurile cu infomatie mai mica lexicografic pentru a ajunge la una dintre starile scop
input 4 blocheaza pe ucs, bf, A* neadmisibila, greedy neadmisibila, in rest functioneaza
"""

# h(c) <= cost_arc(c, e) + h(e), consistenta, oricare c, e doua noduri

# TODO OPTIMIZARE SA NU MAI APELEZ NIMIC DACA NU AM SOLUTIE
# TODO 10 sa nu se introduca porcarii de la tastatura, sa testam parametrii sau daca starea n are solutie sa nu mai apeleze(adica sfere inconjurate sau piramide in varfuri)
# TODO 11 comentarii in special pt genereaza succesori si euristici

import copy
import sys
import time
import stopit
import os
import re

N = 5

if len(sys.argv) == 5:
    inputdir = sys.argv[1]  # 1 deoarece primul argument este numele programului
    outputdir = sys.argv[2]
    if sys.argv[3] == re.sub(r'\D+', '', sys.argv[
        3]):  # folosesc re pentru a elimina toate caracterele care nu sunt cifre din cuvant
        nrsolutii = sys.argv[3]
    else:
        print("\nNumarul de solutii a fost introdus gresit\n")
        exit()
    if sys.argv[4] == re.sub(r'\D+', '', sys.argv[4]):
        timeout = int(sys.argv[4])  # este in secunde
    else:
        print("\nTimeout-ul a fost introdus gresit\n")
        exit()
elif len(sys.argv) == 4:
    inputdir = sys.argv[1]
    outputdir = sys.argv[2]
    if sys.argv[3] == re.sub(r'\D+', '', sys.argv[3]):
        nrsolutii = sys.argv[3]
    else:
        print("\nNumarul de solutii a fost introdus gresit\n")
        exit()
    timeout = 10
elif len(sys.argv) == 3:
    inputdir = sys.argv[1]
    outputdir = sys.argv[2]
    nrsolutii = N
    timeout = 10
elif len(sys.argv) == 2:
    inputdir = sys.argv[1]
    outputdir = 'output'
    nrsolutii = N
    timeout = 10
elif len(sys.argv) == 1:
    inputdir = 'input'
    outputdir = 'output'
    nrsolutii = N
    timeout = 10
elif len(sys.argv) > 5 or len(sys.argv) <= 0:
    print("\nNumarul de parametri nu se afla in limitele dorite\n")
    exit()
else:
    inputdir = 'input'
    outputdir = 'output'
    nrsolutii = N
    timeout = 10

listaFisiereInput = os.listdir(inputdir)
if not os.path.exists("output"):
    os.mkdir("output")
listaFisiereOutput = os.listdir(outputdir)


# informatii despre un nod din arborele de parcurgere (nu din graful initial)
class NodParcurgere:

    def __init__(self, info, parinte, cost=0, h=0):
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost  # consider cost=1 pentru o mutare
        self.h = h
        self.f = self.g + self.h

    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self, fisier, afisCost=False, afisLung=False):  # returneaza si lungimea drumului
        l = self.obtineDrum()
        for idx, nod in enumerate(l):
            fisier.write(str(idx + 1) + ")\n")
            fisier.write(str(nod))
        if afisCost:
            fisier.write("Cost: ")
            fisier.write(str(self.g))
        if afisLung:
            fisier.write("\nLungime: ")
            fisier.write(str(len(l)))
        return len(l)

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if (infoNodNou == nodDrum.info):
                return True
            nodDrum = nodDrum.parinte

        return False

    def __repr__(self):
        sir = ""
        sir += str(self.info)
        return sir

    # euristica banală: daca nu e stare scop, returnez 1, altfel 0

    def __str__(self):
        sir = ""
        maxInalt = max([len(stiva) for stiva in self.info])
        for inalt in range(maxInalt, 0, -1):
            for stiva in self.info:
                if len(stiva) < inalt:
                    # sir += "  ".rjust(5).ljust(8)
                    sir += "    "  # patru spatii deoarece, avem 3 caractere de afisat si spatiul dintre stive
                else:
                    # sir += "-".join(stiva[inalt - 1]).rjust(20).ljust(15)
                    if stiva[inalt - 1][0] == 'piramida':
                        sir += "/" + stiva[inalt - 1][1] + "\\" + " "
                    if stiva[inalt - 1][0] == 'cub':
                        sir += "[" + stiva[inalt - 1][1] + "]" + " "
                    if stiva[inalt - 1][0] == 'sfera':
                        sir += "(" + stiva[inalt - 1][1] + ")" + " "
            sir += "\n"
        sir += "#" * (len(self.info) * len(self.info) - 1)
        sir += '\n'
        return sir


class Graph:  # graful problemei

    K = None
    nrNoduri = 20

    def __init__(self, nume_fisier):

        def obtineStive(sir):

            stiveSiruri = sir.strip().split("\n")

            if stiveSiruri[0].isdecimal():
                self.K = int(stiveSiruri[0])
                listaStive = [sirStiva.strip().split(",") if sirStiva != "#" else [] for sirStiva in stiveSiruri[1:]]
            else:
                listaStive = [sirStiva.strip().split(",") if sirStiva != "#" else [] for sirStiva in stiveSiruri]
            listaSt1 = []
            for idx in range(len(listaStive)):
                listaSt2 = []
                for sirStiva in listaStive[idx]:
                    listaSt2.append(sirStiva.strip().replace("(", " ").replace(")", ""))
                listaSt1.append(listaSt2)
            listaStfin = []
            for idx in range(len(listaSt1)):
                listaSt3 = []
                for sirStiva in listaSt1[idx]:
                    listaSt3.append(sirStiva.split())
                listaStfin.append(listaSt3)
            return listaStfin

        f = open(nume_fisier, 'r')

        continutFisier = f.read()
        self.start = obtineStive(continutFisier)
        # verificam daca starea initiala este valida, deoarece nu dorim sa apelam functiile in cazul in care aceasta este invalida
        nr_stive = len(self.start)
        stare_init_valida = 1
        for idx in range(nr_stive):
            for elem in range(len(self.start[idx])):
                if self.start[idx][elem][0] == "sfera" and (idx == 0 or idx == nr_stive - 1 or
                                                            self.start[idx - 1][elem][0] not in ["cub", "sfera"] or
                                                            self.start[idx + 1][elem][0] not in ["cub", "sfera"]):
                    stare_init_valida = 0
                    break
                if self.start[idx][elem][0] == "piramida" and (len(self.start[idx]) - elem != 1):
                    stare_init_valida = 0
                    break

        if stare_init_valida == 0:
            print("Stare initiala din fisier este invalida")
            exit()
        nrstivegoale = 0
        nrstivefarapir = 0
        ok = 0
        nrpir = 0
        nrsfereincadrate = 0
        if stare_init_valida == 1:
            for idx in range(nr_stive):
                for elem in range(len(self.start[idx])):
                    if self.start[idx][elem][0] == "piramida" and (len(self.start[idx]) - elem != 1):
                        nrpir += 1
                        ok = 1
                    if self.start[idx][elem][0] == "sfera" and (idx != 0 and idx != nr_stive - 1 and
                                                                self.start[idx - 1][elem][0] in ["cub", "sfera"] and
                                                                self.start[idx + 1][elem][0] in ["cub", "sfera"]):
                        nrsfereincadrate += 1
                    if self.start[idx][elem][0] == " ":
                        nrstivegoale += 1
                    if ok == 0:
                        nrstivefarapir += 1

        # optimizari
        if self.K != 0 and (nrpir == nr_stive or nr_stive - 1) and (nrstivegoale + nrstivefarapir) < nrpir:
            print("Starea data nu are solutii")
            return
        '''if self.K != 0 and nrstivegoale < nrsfereincadrate:
            print("Starea data nu are solutii")
            return'''

        print("Stare Initiala:", self.start)
        print("Numar stive vide:", self.K)

        input()

    def testeaza_scop(self, nodCurent):
        # verific daca scopul este indeplinit
        nrv = 0
        for idx in range(len(nodCurent.info)):
            if len(nodCurent.info[idx]) == 0:
                nrv = nrv + 1
        if nrv == self.K:
            return True
        return False

    # va genera succesorii sub forma de noduri in arborele de parcurgere

    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica banala"):
        listaSuccesori = []
        stive_c = nodCurent.info  # stivele din nodul curent
        nr_stive = len(stive_c)
        for idx in range(nr_stive):
            copie_interm = copy.deepcopy(stive_c)
            if len(copie_interm[idx]) == 0:  # daca stiva e vida sa nu poata sa dea pop din ea
                continue
            # verific daca blocul respectiv este vecin cu o sfera
            if idx > 0 and len(copie_interm[idx - 1]) >= len(copie_interm[idx]) and \
                    copie_interm[idx - 1][len(copie_interm[idx]) - 1][0] == "sfera":
                continue
            if idx < nr_stive - 1 and len(copie_interm[idx + 1]) >= len(copie_interm[idx]) and \
                    copie_interm[idx + 1][len(copie_interm[idx]) - 1][0] == "sfera":
                continue
            bloc = copie_interm[idx].pop()

            for j in range(nr_stive):
                if idx == j:
                    continue
                stive_n = copy.deepcopy(copie_interm)  # lista noua de stive
                # verific daca pun piramida peste piramida
                if len(stive_n[j]) > 0 and stive_n[j][-1][0] == "piramida":
                    continue
                # verific unde pun o sfera
                if bloc[0] == "sfera":
                    if j in (0, nr_stive - 1):
                        continue
                    if not (len(stive_n[j - 1]) >= len(stive_n[j]) + 1 and stive_n[j - 1][len(stive_n[j])][0] in ["cub",
                                                                                                                  "sfera"]):
                        continue
                    if not (len(stive_n[j + 1]) >= len(stive_n[j]) + 1 and stive_n[j + 1][len(stive_n[j])][0] in ["cub",
                                                                                                                  "sfera"]):
                        continue

                stive_n[j].append(bloc)

                # if pentru cost mutare 1 pentru triunghi, 2 pentru cub și 3 pentru sferă.
                if bloc[0] == 'piramida':
                    costMutareBloc = 1
                elif bloc[0] == 'cub':
                    costMutareBloc = 2
                else:
                    costMutareBloc = 3

                nod_nou = NodParcurgere(stive_n, nodCurent, cost=nodCurent.g + costMutareBloc,
                                        h=self.calculeaza_h(stive_n, tip_euristica))
                if not nodCurent.contineInDrum(stive_n):
                    listaSuccesori.append(nod_nou)

        return listaSuccesori

    # euristici
    def calculeaza_h(self, infoNod, tip_euristica="euristica banala"):

        # Pentru euristica admisibila 1 am ales sa adun lungimea celor mai mici K stive, deoarece nu stim pe care vrem
        # sa le facem vide. La aceasta am adunat costul minim al unei mutari, deoarece, in functie de cate mutari este
        # necesar sa facem, costul real al drumului va depasi euristica.
        if tip_euristica == "euristica admisibila 1":
            euristici = []
            h = 0
            copy_stive = copy.deepcopy(infoNod)
            copy_stive = sorted(copy_stive, key=lambda stiva: len(stiva))
            for idx in range(self.K):
                h = h + len(copy_stive[idx])
            for idx in range(len(infoNod)):
                for idxel in range(len(infoNod[idx])):
                    h = h + min(1, 2, 3)  # adunam costul minim
                euristici.append(h)
            return min(euristici)

        # Pentru euristica admisibila 2 am ales sa adun lungimea celor mai mici K stive, deoarece nu stim pe care vrem
        # sa le facem vide. La aceasta am adunat costul real al unei mutari, deoarece, in functie de cate mutari este
        # necesar sa facem, costul real al drumului in cel mai rau caz va fi egal cu euristica.
        elif tip_euristica == "euristica admisibila 2":
            euristici = []
            h = 0
            copy_stive = copy.deepcopy(infoNod)
            copy_stive = sorted(copy_stive, key=lambda stiva: len(stiva))
            for idx in range(self.K):
                h = h + len(copy_stive[idx])
            for idx in range(len(infoNod)):
                for idxel in range(len(infoNod[idx])):
                    if infoNod[idx][idxel][0] == "piramida":
                        h = h + 1
                    elif infoNod[idx][idxel][0] == "cub":
                        h = h + 2
                    else:
                        h = h + 3
                euristici.append(h)
            return min(euristici)

        # Pentru euristica neadmisibila am ales sa adun lungimea celor mai mici K stive, deoarece nu stim pe care vrem
        # sa le facem vide, inmultite cu 3. Apoi, la acestea am adunat lungimea restului de stive inmultite cu 5, si
        # pentru a depinde de forma blocului, am adunat costul mutarii blocului respectiv si apoi am inmultit cu 5
        # pentru piramida, 10 pentru cub si 8 pentru sfera. Astfel, aceasta va fi mai mare decat costul real al drumului
        # si va fi neadmisibila.
        elif tip_euristica == "euristica neadmisibila":
            euristici = []
            h = 0
            copy_stive = copy.deepcopy(infoNod)
            copy_stive = sorted(copy_stive, key=lambda stiva: len(stiva))
            for idx in range(self.K):
                h = h + len(copy_stive[idx]) * 3
            for idx in range(len(infoNod) - self.K - 1, len(infoNod)):
                h = h + len(copy_stive[idx]) * 5
            for idx in range(len(infoNod)):
                for idxel in range(len(infoNod[idx])):
                    if infoNod[idx][idxel][0] == "piramida":
                        h = (h + 1) * 5
                    elif infoNod[idx][idxel][0] == "cub":
                        h = (h + 2) * 10
                    else:
                        h = (h + 3) * 8
                euristici.append(h)
            return min(euristici)

        # acest else este pus pentru ca in afara de A* si greedy, la restul functiilor nu avem euristici
        else:
            return 0

    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return (sir)


###########################################
@stopit.threading_timeoutable(default="a intrat in timeout")
def breadth_first(fisier, gr, nrSolutiiCautate):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    nr_nod = 0
    global time1
    nrSolInitiale = nrSolutiiCautate
    c = [NodParcurgere(gr.start, None)]

    if nrSolInitiale == 1:
        if gr.testeaza_scop(c[0]) == True:
            time_sol = time.time()
            fisier.write("\nSolutie:\n")
            c[0].afisDrum(fisier, afisCost=True, afisLung=True)
            fisier.write("\nNumarul de noduri este ")
            fisier.write(str(nr_nod))
            timp_rulare_sol = str(round(1000 * (time_sol - time1)))
            fisier.write("\nTimpul de rulare pe solutie este ")
            fisier.write(timp_rulare_sol)
            fisier.write(" milisecunde")
            fisier.write("\n=======================\n")

            return

    while len(c) > 0:
        # print("Coada actuala: " + str(c))
        # input()
        nodCurent = c.pop(0)

        if nrSolInitiale != 1:
            if gr.testeaza_scop(nodCurent):
                time_sol = time.time()
                fisier.write("\nSolutie:\n")
                nodCurent.afisDrum(fisier, afisCost=True, afisLung=True)
                fisier.write("\nNumarul de noduri este ")
                fisier.write(str(nr_nod))
                timp_rulare_sol = str(round(1000 * (time_sol - time1)))
                fisier.write("\nTimpul de rulare pe solutie este ")
                fisier.write(timp_rulare_sol)
                fisier.write(" milisecunde")
                fisier.write("\n=======================\n")
                # input()
                nrSolutiiCautate -= 1
                if nrSolutiiCautate == 0:
                    return

            lSuccesori = gr.genereazaSuccesori(nodCurent)
            nr_nod += len(lSuccesori)
            c.extend(lSuccesori)
        else:
            lSuccesori = gr.genereazaSuccesori(nodCurent)
            for succ in lSuccesori:
                if gr.testeaza_scop(succ) == True:
                    time_sol = time.time()
                    fisier.write("\nSolutie:\n")
                    succ.afisDrum(fisier, afisCost=True, afisLung=True)
                    fisier.write("\nNumarul de noduri este ")
                    fisier.write(str(nr_nod))
                    timp_rulare_sol = str(round(1000 * (time_sol - time1)))
                    fisier.write("\nTimpul de rulare pe solutie este ")
                    fisier.write(timp_rulare_sol)
                    fisier.write(" milisecunde")
                    fisier.write("\n=======================\n")

                    return
            nr_nod += len(lSuccesori)
            c.extend(lSuccesori)

        '''
        # codul initial
        nr_nod = 0
        global time1
        c = [NodParcurgere(gr.start, None)]
    
        while len(c) > 0:
            # print("Coada actuala: " + str(c))
            # input()
            nodCurent = c.pop(0)
    
            if gr.testeaza_scop(nodCurent):
                time_sol = time.time()
                fisier.write("\nSolutie:\n")
                nodCurent.afisDrum(fisier, afisCost=True, afisLung=True)
                fisier.write("\nNumarul de noduri este ")
                fisier.write(str(nr_nod))
                timp_rulare_sol = str(round(1000 * (time_sol - time1)))
                fisier.write("\nTimpul de rulare pe solutie este ")
                fisier.write(timp_rulare_sol)
                fisier.write(" milisecunde")
                fisier.write("\n=======================\n")
                #input()
                nrSolutiiCautate -= 1
                if nrSolutiiCautate == 0:
                    return
            lSuccesori = gr.genereazaSuccesori(nodCurent)
            nr_nod += len(lSuccesori)
            # print(lSuccesori)
            c.extend(lSuccesori)
        '''


#############################################
nr_nod_df = 0


@stopit.threading_timeoutable(default="a intrat in timeout")
def depth_first(fisier, gr, nrSolutiiCautate=1):
    # vom simula o stiva prin relatia de parinte a nodului curent
    global nr_nod_df
    nr_nod_df = 0
    df(fisier, gr, NodParcurgere(gr.start, None), nrSolutiiCautate)


def df(fisier, gr, nodCurent, nrSolutiiCautate):
    if nrSolutiiCautate == 0:  # testul acesta s-ar valida doar daca in apelul initial avem df(start,if nrSolutiiCautate=0)
        return nrSolutiiCautate
    # print("Stiva actuala: " + "->".join(nodCurent.obtineDrum()))
    # input()
    global time1, nr_nod_df
    if gr.testeaza_scop(nodCurent):
        time_sol = time.time()
        fisier.write("\nSolutie:\n")
        nodCurent.afisDrum(fisier, afisCost=True, afisLung=True)
        fisier.write("\nNumarul de noduri este ")
        fisier.write(str(nr_nod_df))
        timp_rulare_sol = str(round(1000 * (time_sol - time1)))
        fisier.write("\nTimpul de rulare pe solutie este ")
        fisier.write(timp_rulare_sol)
        fisier.write(" milisecunde")
        fisier.write("\n=======================\n")
        # input()
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return nrSolutiiCautate
    lSuccesori = gr.genereazaSuccesori(nodCurent)
    nr_nod_df += len(lSuccesori)
    for sc in lSuccesori:
        if nrSolutiiCautate != 0:
            nrSolutiiCautate = df(fisier, gr, sc, nrSolutiiCautate)
    return nrSolutiiCautate


#############################################
nr_nod_dfi = 0


def dfi(fisier, gr, nodCurent, adancime, nrSolutiiCautate):
    # print("Stiva actuala: " + "->".join(nodCurent.obtineDrum()))
    # input()
    global nr_nod_dfi, time1
    if adancime == 1 and gr.testeaza_scop(nodCurent):
        time_sol = time.time()
        fisier.write("\nSolutie:\n")
        nodCurent.afisDrum(fisier, afisCost=True, afisLung=True)
        fisier.write("\nNumarul de noduri este ")
        fisier.write(str(nr_nod_dfi))
        timp_rulare_sol = str(round(1000 * (time_sol - time1)))
        fisier.write("\nTimpul de rulare pe solutie este ")
        fisier.write(timp_rulare_sol)
        fisier.write(" milisecunde")
        fisier.write("\n=======================\n")
        # input()
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return nrSolutiiCautate
    if adancime > 1:
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        nr_nod_dfi += len(lSuccesori)
        for sc in lSuccesori:
            if nrSolutiiCautate != 0:
                nrSolutiiCautate = dfi(fisier, gr, sc, adancime - 1, nrSolutiiCautate)
    return nrSolutiiCautate


@stopit.threading_timeoutable(default="a intrat in timeout")
def depth_first_iterativ(fisier, gr, nrSolutiiCautate=1):
    global nr_nod_dfi
    nr_nod_dfi = 0
    for i in range(1, gr.nrNoduri + 1):
        if nrSolutiiCautate == 0:
            return
        # fisier.write("**************\nAdancime maxima: ")
        # fisier.write(str(i))
        nrSolutiiCautate = dfi(fisier, gr, NodParcurgere(gr.start, None), i, nrSolutiiCautate)


#########################################################
@stopit.threading_timeoutable(default="a intrat in timeout")
def uniform_cost(fisier, gr, nrSolutiiCautate=1):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    nr_nod = 0
    global time1
    c = [NodParcurgere(gr.start, None, 0)]

    while len(c) > 0:
        # fisier.write("Coada actuala: " + str(c))
        # input()
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            time_sol = time.time()
            fisier.write("\nSolutie:\n")
            nodCurent.afisDrum(fisier, afisCost=True, afisLung=True)
            fisier.write("\nNumarul de noduri este ")
            fisier.write(str(nr_nod))
            timp_rulare_sol = str(round(1000 * (time_sol - time1)))
            fisier.write("\nTimpul de rulare pe solutie este ")
            fisier.write(timp_rulare_sol)
            fisier.write(" milisecunde")
            fisier.write("\n=======================\n")
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return

        lSuccesori = gr.genereazaSuccesori(nodCurent)
        # optimizare
        idxsucc = 0
        while idxsucc < len(lSuccesori):
            elim = 0
            idxc = 0
            ok = 0
            while idxc < len(c):
                if lSuccesori[idxsucc].info == c[idxc].info:
                    if c[idxc].g > lSuccesori[idxsucc].g:  # daca costul succesorului este mai mic decat costul nodului din coada il elimin
                        c.pop(idxc)
                        elim += 1
                        ok = 1
                        idxc -= 1
                idxc += 1
            if ok == 0 or elim >= 1:  # daca succesorul nu era prezent in coada sau s-a eliminat cel putin un nod din coada inserez succesorul
                c.insert(idxc, lSuccesori[idxsucc])
                lSuccesori.pop(idxsucc)
            if idxsucc < len(lSuccesori):
                idxsucc += 1
        ######################
        nr_nod += len(lSuccesori)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # ordonez dupa cost(notat cu g aici și în desenele de pe site)
                if c[i].g > s.g:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


#######################################################
@stopit.threading_timeoutable(default="a intrat in timeout")
def a_star(fisier, gr, nrSolutiiCautate, tip_euristica):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    nr_nod = 0
    global time1
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, tip_euristica))]

    while len(c) > 0:
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            time_sol = time.time()
            fisier.write("\nSolutie:\n")
            nodCurent.afisDrum(fisier, afisCost=True, afisLung=True)
            fisier.write("\nNumarul de noduri este ")
            fisier.write(str(nr_nod))
            timp_rulare_sol = str(round(1000 * (time_sol - time1)))
            fisier.write("\nTimpul de rulare pe solutie este ")
            fisier.write(timp_rulare_sol)
            fisier.write(" milisecunde")
            fisier.write("\n=======================\n")
            # input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        # optimizare
        idxsucc = 0
        while idxsucc < len(lSuccesori):
            elim = 0
            idxc = 0
            ok = 0
            while idxc < len(c):
                if lSuccesori[idxsucc].info == c[idxc].info:
                    if c[idxc].g > lSuccesori[idxsucc].g:  # daca costul succesorului este mai mic decat costul nodului din coada il elimin
                        c.pop(idxc)
                        elim += 1
                        ok = 1
                        idxc -= 1
                idxc += 1
            if ok == 0 or elim >= 1:  # daca succesorul nu era prezent in coada sau s-a eliminat cel putin un nod din coada inserez succesorul
                c.insert(idxc, lSuccesori[idxsucc])
                lSuccesori.pop(idxsucc)
            if idxsucc < len(lSuccesori):
                idxsucc += 1

        ######################
        nr_nod += len(lSuccesori)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # diferenta fata de UCS e ca ordonez dupa f
                if c[i].f >= s.f:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


#######################################################
@stopit.threading_timeoutable(default="a intrat in timeout")
def greedy(fisier, gr, nrSolutiiCautate, tip_euristica):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    nr_nod = 0
    global time1
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, tip_euristica))]

    while len(c) > 0:
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            time_sol = time.time()
            fisier.write("\nSolutie:\n")
            nodCurent.afisDrum(fisier, afisCost=True, afisLung=True)
            fisier.write("\nNumarul de noduri este ")
            fisier.write(str(nr_nod))
            timp_rulare_sol = str(round(1000 * (time_sol - time1)))
            fisier.write("\nTimpul de rulare pe solutie este ")
            fisier.write(timp_rulare_sol)
            fisier.write(" milisecunde")
            fisier.write("\n=======================\n")
            # input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        nr_nod += len(lSuccesori)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # diferenta fata de A* e ca ordonez dupa h
                if c[i].h >= s.h:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


# aceste apeluri le puteam face cu for-uri

nrSolutiiCautate = int(nrsolutii)

# input1
gr1 = Graph("input/" + listaFisiereInput[0])

# pentru a determina indicii fisierelor de output
# for i in range(0, len(listaFisiereOutput)):
# print(listaFisiereOutput[i],i,"\n")

# BF
fiso = open("output/" + listaFisiereOutput[12], 'w')
fiso.write("Solutii obtinute cu breadth first:")
time1 = time.time()
if breadth_first(fiso, gr1, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nBreadth first a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru breadth first este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# DF
fiso = open("output/" + listaFisiereOutput[20], 'w')
fiso.write("Solutii obtinute cu depth first:")
time1 = time.time()
if depth_first(fiso, gr1, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nDepth first a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru de depth first este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# DFI
fiso = open("output/" + listaFisiereOutput[16], 'w')
fiso.write("Solutii obtinute cu depth first iterativ:")
time1 = time.time()
if depth_first_iterativ(fiso, gr1, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nDepth first iterativ a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru depth first iterativ este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# UCS
fiso = open("output/" + listaFisiereOutput[36], 'w')
fiso.write("Solutii obtinute cu uniform cost search:")
time1 = time.time()
if uniform_cost(fiso, gr1, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nUniform cost search a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru uniform cost search este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# A* admisibila 1
fiso = open("output/" + listaFisiereOutput[0], 'w')
fiso.write("Solutii obtinute cu A* cu euristica admisibila 1:")
time1 = time.time()
if a_star(fiso, gr1, nrSolutiiCautate, tip_euristica="euristica admisibila 1",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nA* cu euristica admisibila 1 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru breadth A* cu euristica admisibila 1 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# A* admisibila 2
fiso = open("output/" + listaFisiereOutput[4], 'w')
fiso.write("Solutii obtinute cu A* cu euristica admisibila 2:")
time1 = time.time()
if a_star(fiso, gr1, nrSolutiiCautate, tip_euristica="euristica admisibila 2",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nA* cu euristica admisibila 2 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru A* cu euristica admisibila 2 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# A* neadmisibila
fiso = open("output/" + listaFisiereOutput[8], 'w')
fiso.write("Solutii obtinute cu A* cu euristica neadmisibila:")
time1 = time.time()
if a_star(fiso, gr1, nrSolutiiCautate, tip_euristica="euristica neadmisibila",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nA* cu euristica neadmisibila a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru A* cu euristica neadmisibila este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# Greedy admisibila 1
fiso = open("output/" + listaFisiereOutput[24], 'w')
fiso.write("Solutii obtinute cu greedy cu euristica admisibila 1:")
time1 = time.time()
if greedy(fiso, gr1, nrSolutiiCautate, tip_euristica="euristica admisibila 1",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nGreedy cu euristica admisibila 1 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru greedy cu euristica admisibila 1 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# Greedy admisibila 2
fiso = open("output/" + listaFisiereOutput[28], 'w')
fiso.write("Solutii obtinute cu greedy cu euristica admisibila 2:")
time1 = time.time()
if greedy(fiso, gr1, nrSolutiiCautate, tip_euristica="euristica admisibila 2",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nGreedy cu euristica admisibila 2 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru euristica admisibila 2 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# Greedy neadmisibila
fiso = open("output/" + listaFisiereOutput[32], 'w')
fiso.write("Solutii obtinute cu greedy cu euristica neadmisibila:")
time1 = time.time()
if greedy(fiso, gr1, nrSolutiiCautate, tip_euristica="euristica neadmisibila",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nGreedy cu euristica neadmisibila a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru greedy cu euristica neadmisibila este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()

# input2
gr2 = Graph("input/" + listaFisiereInput[1])

# BF
fiso = open("output/" + listaFisiereOutput[13], 'w')
fiso.write("Solutii obtinute cu breadth first:")
time1 = time.time()
if breadth_first(fiso, gr2, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nBreadth first a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru breadth first ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# DF
fiso = open("output/" + listaFisiereOutput[21], 'w')
fiso.write("Solutii obtinute cu depth first:")
time1 = time.time()
if depth_first(fiso, gr2, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nDepth first a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru depth first este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# DFI
fiso = open("output/" + listaFisiereOutput[17], 'w')
fiso.write("Solutii obtinute cu depth first iterativ:")
time1 = time.time()
if depth_first_iterativ(fiso, gr2, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nDepth first iterativ a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru depth first iterativ este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# UCS
fiso = open("output/" + listaFisiereOutput[37], 'w')
fiso.write("Solutii obtinute cu uniform cost search:")
time1 = time.time()
if uniform_cost(fiso, gr2, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nUniform cost search a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru uniform cost search este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# A* admisibila 1
fiso = open("output/" + listaFisiereOutput[1], 'w')
fiso.write("Solutii obtinute cu A* cu euristica admisibila 1:")
time1 = time.time()
if a_star(fiso, gr2, nrSolutiiCautate, tip_euristica="euristica admisibila 1",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nA* cu euristica admisibila 1 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru A* cu euristica admisibila 1 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# A* admisibila 2
fiso = open("output/" + listaFisiereOutput[5], 'w')
fiso.write("Solutii obtinute cu A* cu euristica admisibila 2:")
time1 = time.time()
if a_star(fiso, gr2, nrSolutiiCautate, tip_euristica="euristica admisibila 2",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nA* cu euristica admisibila 2 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru A* cu euristica admisibila 2 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# A* neadmisibila
fiso = open("output/" + listaFisiereOutput[9], 'w')
fiso.write("Solutii obtinute cu A* cu euristica neadmisibila:")
time1 = time.time()
if a_star(fiso, gr2, nrSolutiiCautate, tip_euristica="euristica neadmisibila",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nA* cu euristica neadmisibila a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru A* cu euristica neadmisibila este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# Greedy admisibila 1
fiso = open("output/" + listaFisiereOutput[25], 'w')
fiso.write("Solutii obtinute cu greedy cu euristica admisibila 1:")
time1 = time.time()
if greedy(fiso, gr2, nrSolutiiCautate, tip_euristica="euristica admisibila 1",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nGreedy cu euristica admisibila 1 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru greedy cu euristica admisibila 1 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# Greedy admisibila 2
fiso = open("output/" + listaFisiereOutput[29], 'w')
fiso.write("Solutii obtinute cu greedy cu euristica admisibila 2:")
time1 = time.time()
if greedy(fiso, gr2, nrSolutiiCautate, tip_euristica="euristica admisibila 2",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nGreedy cu euristica admisibila 2 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru greedy cu euristica admisibila 2 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# Greedy neadmisibila
fiso = open("output/" + listaFisiereOutput[33], 'w')
fiso.write("Solutii obtinute cu greedy cu euristica neadmisibila:")
time1 = time.time()
if greedy(fiso, gr2, nrSolutiiCautate, tip_euristica="euristica neadmisibila",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nGreedy cu euristica neadmisibila a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru greedy cu euristica neadmisibila este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()

# input3
gr3 = Graph("input/" + listaFisiereInput[2])

# BF
fiso = open("output/" + listaFisiereOutput[14], 'w')
fiso.write("Solutii obtinute cu breadth first:")
time1 = time.time()
if breadth_first(fiso, gr3, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nBreadth first a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru breadth first este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# DF
fiso = open("output/" + listaFisiereOutput[22], 'w')
fiso.write("Solutii obtinute cu depth first:")
time1 = time.time()
if depth_first(fiso, gr3, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nDepth first a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru depth first este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# DFI
fiso = open("output/" + listaFisiereOutput[18], 'w')
fiso.write("Solutii obtinute cu depth first iterativ:")
time1 = time.time()
if depth_first_iterativ(fiso, gr3, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nDepth first iterativ a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru depth first iterativ este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# UCS
fiso = open("output/" + listaFisiereOutput[38], 'w')
fiso.write("Solutii obtinute cu uniform cost search:")
time1 = time.time()
if uniform_cost(fiso, gr3, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nUniform cost search a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru uniform cost search este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# A* admisibila 1
fiso = open("output/" + listaFisiereOutput[2], 'w')
fiso.write("Solutii obtinute cu A* cu euristica admisibila 1:")
time1 = time.time()
if a_star(fiso, gr3, nrSolutiiCautate, tip_euristica="euristica admisibila 1",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nA* cu euristica admisibila 1 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru A* cu euristica admisibila 1 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# A* admisibila 2
fiso = open("output/" + listaFisiereOutput[6], 'w')
fiso.write("Solutii obtinute cu A* cu euristica admisibila 2:")
time1 = time.time()
if a_star(fiso, gr3, nrSolutiiCautate, tip_euristica="euristica admisibila 2",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nA* cu euristica admisibila 2 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru A* cu euristica admisibila 2 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# A* neadmisibila
fiso = open("output/" + listaFisiereOutput[10], 'w')
fiso.write("Solutii obtinute cu A* cu euristica neadmisibila:")
time1 = time.time()
if a_star(fiso, gr3, nrSolutiiCautate, tip_euristica="euristica neadmisibila",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nA* cu euristica neadmisibila a intrat in timeout este de ")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru A* cu euristica neadmisibila este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# Greedy admisibila 1
fiso = open("output/" + listaFisiereOutput[26], 'w')
fiso.write("Solutii obtinute cu greedy cu euristica admisibila 1:")
time1 = time.time()
if greedy(fiso, gr3, nrSolutiiCautate, tip_euristica="euristica admisibila 1",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nGreedy cu euristica admisibila 1 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru greedy cu euristica admisibila 1 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# Greedy admisibila 2
fiso = open("output/" + listaFisiereOutput[30], 'w')
fiso.write("Solutii obtinute cu greedy cu euristica admisibila 2:")
time1 = time.time()
if greedy(fiso, gr3, nrSolutiiCautate, tip_euristica="euristica admisibila 2",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nGreedy cu euristica admisibila 2 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru greedy cu euristica admisibila 2 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# Greedy neadmisibila
fiso = open("output/" + listaFisiereOutput[34], 'w')
fiso.write("Solutii obtinute cu greedy cu euristica neadmisibila:")
time1 = time.time()
if greedy(fiso, gr3, nrSolutiiCautate, tip_euristica="euristica neadmisibila",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nGreedy cu euristica neadmisibila a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru greedy cu euristica neadmisibila este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()

# input4
gr4 = Graph("input/" + listaFisiereInput[3])

# BF
fiso = open("output/" + listaFisiereOutput[15], 'w')
fiso.write("Solutii obtinute cu breadth first:")
time1 = time.time()
if breadth_first(fiso, gr4, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nBreadth first a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru breadth first este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# DF
fiso = open("output/" + listaFisiereOutput[23], 'w')
fiso.write("Solutii obtinute cu depth first:")
time1 = time.time()
if depth_first(fiso, gr4, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nDepth first a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru depth first este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# DFI
fiso = open("output/" + listaFisiereOutput[19], 'w')
fiso.write("Solutii obtinute cu depth first iterativ:")
time1 = time.time()
if depth_first_iterativ(fiso, gr4, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nDepth first iterativ a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru depth first iterativ este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# UCS
fiso = open("output/" + listaFisiereOutput[39], 'w')
fiso.write("Solutii obtinute cu uniform cost search:")
time1 = time.time()
if uniform_cost(fiso, gr4, nrSolutiiCautate, timeout=timeout) == "a intrat in timeout":
    fiso.write("\nUniform cost search a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru uniform cost search este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# A* admisibila 1
fiso = open("output/" + listaFisiereOutput[3], 'w')
fiso.write("Solutii obtinute cu A* cu euristica admisibila 1:")
time1 = time.time()
if a_star(fiso, gr4, nrSolutiiCautate, tip_euristica="euristica admisibila 1",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nA* cu euristica admisibila 1 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru A* cu euristica admisibila 1 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# A* admisibila 2
fiso = open("output/" + listaFisiereOutput[7], 'w')
fiso.write("Solutii obtinute cu A* cu euristica admisibila 2:")
time1 = time.time()
if a_star(fiso, gr4, nrSolutiiCautate, tip_euristica="euristica admisibila 2",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nA* cu euristica admisibila 2 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru A* cu euristica admisibila 2 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# A* neadmisibila
fiso = open("output/" + listaFisiereOutput[11], 'w')
fiso.write("Solutii obtinute cu A* cu euristica neadmisibila:")
time1 = time.time()
if a_star(fiso, gr4, nrSolutiiCautate, tip_euristica="euristica neadmisibila",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nA* cu euristica neadmisibila a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru A* cu euristica neadmisibila este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# Greedy admisibila 1
fiso = open("output/" + listaFisiereOutput[27], 'w')
fiso.write("Solutii obtinute cu greedy cu euristica admisibila 1:")
time1 = time.time()
if greedy(fiso, gr4, nrSolutiiCautate, tip_euristica="euristica admisibila 1",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nGreedy cu euristica admisibila 1 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru greedy cu euristica admisibila 1 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# Greedy admisibila 2
fiso = open("output/" + listaFisiereOutput[31], 'w')
fiso.write("Solutii obtinute cu greedy cu euristica admisibila 2:")
time1 = time.time()
if greedy(fiso, gr4, nrSolutiiCautate, tip_euristica="euristica admisibila 2",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nGreedy cu euristica admisibila 2 a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru greedy cu euristica admisibila 2 este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
# Greedy neadmisibila
fiso = open("output/" + listaFisiereOutput[35], 'w')
fiso.write("Solutii obtinute cu greedy cu euristica neadmisibila:")
time1 = time.time()
if greedy(fiso, gr4, nrSolutiiCautate, tip_euristica="euristica neadmisibila",
          timeout=timeout) == "a intrat in timeout":
    fiso.write("\nGreedy cu euristica neadmisibila a intrat in timeout")
time2 = time.time()
timp_rulare = str(round(1000 * (time2 - time1)))
fiso.write("\nTimpul total de rulare pentru greedy cu euristica neadmisibila este de ")
fiso.write(timp_rulare)
fiso.write(" milisecunde")
fiso.close()
