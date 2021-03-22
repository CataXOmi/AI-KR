import time
import pygame, sys, statistics
import copy
import time
import os
import re

interfata = []
if len(sys.argv) == 2:
    interfata.append(sys.argv[1])

if len(sys.argv) > 2:
    print("Numar de argumente invalid")
    exit()

def deseneaza_grid(display, tabla, N, M, marcaj=None):  # tabla de exemplu este ["#","x","#","0",......]
    w_gr = h_gr = 80  # width-ul si height-ul unei celule din grid

    x_img = pygame.image.load('ics.png')
    x_img = pygame.transform.scale(x_img, (w_gr, h_gr))
    zero_img = pygame.image.load('zero.png')
    zero_img = pygame.transform.scale(zero_img, (w_gr, h_gr))
    drt = []  # este lista cu patratelele din grid
    for ind in range(len(tabla)):
        linie = ind // M  # // inseamna div
        coloana = ind % M
        patr = pygame.Rect(coloana * (w_gr + 1), linie * (h_gr + 1), w_gr, h_gr)
        # print(str(coloana*(w_gr+1)), str(linie*(h_gr+1)))
        drt.append(patr)
        '''
        if marcaj == ind:
            # daca am o patratica selectata, o desenez cu rosu
            culoare = (255, 0, 0)
        
        else:'''
        # altfel o desenez cu alb
        culoare = (255, 255, 255)
        pygame.draw.rect(display, culoare, patr)  # alb = (255,255,255)
        if tabla[ind] == 'x':
            display.blit(x_img, (coloana * (w_gr + 1), linie * (h_gr + 1)))
        elif tabla[ind] == '0':
            display.blit(zero_img, (coloana * (w_gr + 1), linie * (h_gr + 1)))
    pygame.display.flip()
    return drt


class Joc:
    """
    Clasa care defineste jocul. Se va schimba de la un joc la altul.
    """
    NR_LINII = None
    NR_COLOANE = None
    JMIN = None
    JMAX = None
    GOL = '#'
    l1 = []
    l1.append('x')
    l2 = []
    l2.append('0')

    def __init__(self, tabla=None, ult_mut_jmin_idxlist = None, ult_mut_jmax_idxlist = None):
        self.matr = tabla or ([self.__class__.GOL] * ((self.NR_LINII // 2)*self.NR_COLOANE + self.NR_COLOANE//2-1) + self.l1 + self.l2 +
                              [self.__class__.GOL] * ((self.NR_LINII // 2)*self.NR_COLOANE + self.NR_COLOANE//2-1))
        '''if (self.j_curent == Joc.JMIN and Joc.JMIN == 'x') or (self.j_curent == Joc.JMAX and Joc.JMAX == '0'):
            self.ult_mut_jmin_idxlist = ult_mut_jmin_idxlist or (Joc.NR_LINII // 2)*Joc.NR_COLOANE + Joc.NR_COLOANE//2
            self.ult_mut_jmax_idxlist = ult_mut_jmax_idxlist or (Joc.NR_LINII // 2)*Joc.NR_COLOANE + Joc.NR_COLOANE//2 + 1
        if (self.j_curent == Joc.JMIN and Joc.JMIN == '0') or (self.j_curent == Joc.JMAX and Joc.JMAX == 'x'):
            self.ult_mut_jmin_idxlist = ult_mut_jmin_idxlist or (Joc.NR_LINII // 2)*Joc.NR_COLOANE + Joc.NR_COLOANE//2 + 1
            self.ult_mut_jmax_idxlist = ult_mut_jmax_idxlist or (Joc.NR_LINII // 2)*Joc.NR_COLOANE + Joc.NR_COLOANE//2'''

    def final(self):
        '''rez = (elem_identice(self.matr[0:3])
               or elem_identice(self.matr[3:6])
               or elem_identice(self.matr[6:9])
               or elem_identice(self.matr[0:9:3])
               or elem_identice(self.matr[1:9:3])
               or elem_identice(self.matr[2:9:3])
               or elem_identice(self.matr[0:9:4])
               or elem_identice(self.matr[2:8:2]))
        if (rez):
            return rez
        elif self.__class__.GOL not in self.matr:
            return 'remiza'
        else:
            return False
        '''
    def validitate(self):
        return

    def mutari(self, jucator_opus):
        l_mutari = []
        for i in range(len(self.matr)):
            if self.matr[i] == self.__class__.GOL:
                matr_tabla_noua = copy.deepcopy(self.matr)
                matr_tabla_noua[i] = jucator_opus
                l_mutari.append(Joc(matr_tabla_noua))
        return l_mutari

    # linie deschisa inseamna linie pe care jucatorul mai poate forma o configuratie castigatoare

    def linie_deschisa(self, lista, jucator):
        # obtin multimea simbolurilor de pe linie
        mt = set(lista)
        # verific daca sunt maxim 2 simboluri
        if (len(mt) <= 2):
            # daca multimea simbolurilor nu are alte simboluri decat pentru cel de "gol" si jucatorul curent
            if mt <= {self.__class__.GOL, jucator}:
                # inseamna ca linia este deschisa
                return 1
            else:
                return 0
        else:
            return 0

    def linii_deschise(self, jucator):
        return (self.linie_deschisa(self.matr[0:3], jucator)
                + self.linie_deschisa(self.matr[3:6], jucator)
                + self.linie_deschisa(self.matr[6:9], jucator)
                + self.linie_deschisa(self.matr[0:9:3], jucator)
                + self.linie_deschisa(self.matr[1:9:3], jucator)
                + self.linie_deschisa(self.matr[2:9:3], jucator)
                + self.linie_deschisa(self.matr[0:9:4], jucator)  # prima diagonala
                + self.linie_deschisa(self.matr[2:8:2], jucator))  # a doua diagonala

    # linie deschisa inseamna linie pe care jucatorul mai poate forma o configuratie castigatoare
    def estimare_scor1(self, lista, jucator):
        # obtin multimea simbolurilor de pe linie
        mt = set(lista)
        # verific daca sunt maxim 2 simboluri
        if (len(mt) <= 2):
            # daca multimea simbolurilor nu are alte simboluri decat pentru cel de "gol" si jucatorul curent
            if mt <= {self.__class__.GOL, jucator}:
                # inseamna ca linia este deschisa
                return 1
            else:
                return 0
        else:
            return 0

    def estimare_scor2(self, jucator):

        return

    def estimeaza_scor(self, adancime):
        t_final = self.final()
        # if (adancime==0):
        if t_final == self.__class__.JMAX:
            return (99 + adancime)
        elif t_final == self.__class__.JMIN:
            return (-99 - adancime)
        elif t_final == 'remiza':
            return 0
        else:
            return (self.linii_deschise(self.__class__.JMAX) - self.linii_deschise(self.__class__.JMIN))

    def __str__(self):

        sir = "  |"
        for i in range(self.NR_COLOANE):
            sir += str(i) + " "
        sir += "\n"
        sir += "-" * (self.NR_COLOANE + 1) * 2 + "\n"
        for i in range(self.NR_LINII):  # itereaza prin linii
            sir += str(i) + " |" + " ".join([str(x) for x in self.matr[self.NR_COLOANE * i: self.NR_COLOANE * (i + 1)]]) + "\n"
        # [0,1,2,3,4,5,6,7,8]
        return sir



class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    Are ca proprietate tabla de joc
    Functioneaza cu conditia ca in cadrul clasei Joc sa fie definiti JMIN si JMAX (cei doi jucatori posibili)
    De asemenea cere ca in clasa Joc sa fie definita si o metoda numita mutari() care ofera lista cu configuratiile posibile in urma mutarii unui jucator
    """

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, estimare=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent


        # adancimea in arborele de stari
        self.adancime = adancime

        # estimarea favorabilitatii starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.estimare = estimare

        # lista de mutari posibile din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

    def jucator_opus(self):
        if self.j_curent == Joc.JMIN:
            return Joc.JMAX
        else:
            return Joc.JMIN

    def mutari(self):
        l_mutari = self.tabla_joc.mutari(self.j_curent)
        juc_opus = self.jucator_opus()
        l_stari_mutari = [Stare(mutare, juc_opus, self.adancime - 1, parinte=self) for mutare in l_mutari]

        return l_stari_mutari

    def __str__(self):
        sir = str(self.tabla_joc) + "(Jucator curent:" + self.j_curent + ")\n"
        return sir

""" Algoritmul MinMax """

def min_max(stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.estimare = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    # calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari()

    # aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutariCuEstimare = [min_max(mutare) for mutare in stare.mutari_posibile]

    if stare.j_curent == Joc.JMAX:
        # daca jucatorul e JMAX aleg starea-fiica cu estimarea maxima
        stare.stare_aleasa = max(mutariCuEstimare, key=lambda x: x.estimare)
    else:
        # daca jucatorul e JMIN aleg starea-fiica cu estimarea minima
        stare.stare_aleasa = min(mutariCuEstimare, key=lambda x: x.estimare)
    stare.estimare = stare.stare_aleasa.estimare
    return stare


def alpha_beta(alpha, beta, stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.estimare = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    if alpha > beta:
        return stare  # este intr-un interval invalid deci nu o mai procesez

    stare.mutari_posibile = stare.mutari()

    if stare.j_curent == Joc.JMAX:
        estimare_curenta = float('-inf')

        for mutare in stare.mutari_posibile:
            # calculeaza estimarea pentru starea noua, realizand subarborele
            stare_noua = alpha_beta(alpha, beta, mutare)

            if (estimare_curenta < stare_noua.estimare):
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare
            if (alpha < stare_noua.estimare):
                alpha = stare_noua.estimare
                if alpha >= beta:
                    break

    elif stare.j_curent == Joc.JMIN:
        estimare_curenta = float('inf')

        for mutare in stare.mutari_posibile:

            stare_noua = alpha_beta(alpha, beta, mutare)

            if (estimare_curenta > stare_noua.estimare):
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare

            if (beta > stare_noua.estimare):
                beta = stare_noua.estimare
                if alpha >= beta:
                    break
    stare.estimare = stare.stare_aleasa.estimare

    return stare


def afis_daca_final(stare_curenta):
    final = stare_curenta.tabla_joc.final()
    if (final):
        if (final == "remiza"):
            print("Remiza!")
        else:
            print("A castigat " + final)

        return True
    return False


def main():

    # specificare tip algoritm
    raspuns_valid = False
    while not raspuns_valid:
        tip_algoritm = input("Algoritmul folosit? (raspundeti cu 1 sau 2)\n 1.Minimax\n 2.Alpha-beta\n ")
        if tip_algoritm in ['1', '2']:
            raspuns_valid = True
        else:
            print("Nu ati ales o varianta corecta.")

    raspuns_valid = False
    while not raspuns_valid:
        tip_nivel = input("Ce nivel de dificultate doriti? (raspundeti cu 1, 2 sau 3)\n 1.Incepator\n 2.Mediu\n 3.Avansat\n ")
        if tip_nivel in ['1', '2', '3']:
            raspuns_valid = True
        else:
            print("Nu ati ales o varianta corecta.")

    raspuns_valid = False
    while not raspuns_valid:
        try:
            SCMAX = int(input("Dati scorul maxim dorit: "))
            if (type(SCMAX) is int):
                raspuns_valid = True
                break
        except Exception as exc:
            print("Valoarea data este invalida,", exc)

    # initializare jucatori
    raspuns_valid = False
    while not raspuns_valid:
        Joc.JMIN = input("Doriti sa jucati cu x sau cu 0? ").lower()
        if (Joc.JMIN in ['x', '0']):
            raspuns_valid = True
        else:
            print("Raspunsul trebuie sa fie x sau 0.")
    Joc.JMAX = '0' if Joc.JMIN == 'x' else 'x'

    #initializare dificultate nivel
    if tip_nivel == '1':
        raspuns_valid = False
        while not raspuns_valid:
            try:
                adancime = int(input("Dati adancimea dorita pentru nivelul incepator? "))
                if (type(adancime) is int and adancime>=1 and adancime<=5):
                    raspuns_valid = True
                    break
                print("Adancimea trebuie sa fie in intervalul [1;5]")
            except Exception as exc:
                print("Valoarea data este invalida,", exc)

    if tip_nivel == '2':
        raspuns_valid = False
        while not raspuns_valid:
            try:
                adancime = int(input("Dati adancimea dorita pentru nivelul mediu? "))
                if (type(adancime) is int and adancime>=6 and adancime<=10):
                    raspuns_valid = True
                    break
                print("Adancimea trebuie sa fie in intervalul [6;10]") # adancime foarte mare ca
            except Exception as exc:
                print("Valoarea data este invalida,", exc)

    if tip_nivel == '3':
        raspuns_valid = False
        while not raspuns_valid:
            try:
                adancime = int(input("Dati adancimea dorita pentru nivelul avansat? "))
                if (type(adancime) is int and adancime>=11):
                    raspuns_valid = True
                    break
                print("Adancimea trebuie sa fie in intervalul [11;inf]")
            except Exception as exc:
                print("Valoarea data este invalida,", exc)
    #specificarea dimensiunilor tablei de joc
    raspuns_valid = False
    while not raspuns_valid:
        try:
            N = int(input("Dati numarul de linii dorit "))
            if ((type(N) is int) and (N <= 10 and N >= 5 and N%2 != 0)):
                raspuns_valid = True
                break
            print("Numarul de linii trebuie sa fie impar si sa se afle in intervalul [5;10]")
        except Exception as exc:
            print("Valoarea data este invalida,", exc)

    raspuns_valid = False
    while not raspuns_valid:
        try:
            M = int(input("Dati numarul de coloane dorit "))
            if ((type(M) is int) and (M <= 10 and M >= 5 and M%2 == 0)):
                raspuns_valid = True
                break
            print("Numarul de coloane trebuie sa fie par si sa se afle in intervalul [5;10]")
        except Exception as exc:
            print("Valoarea data este invalida,", exc)

    #citire pentru interfata
    if len(interfata) != 1:
        raspuns_valid = False
        while not raspuns_valid:
            interface = input(
                "Doriti sa jucati din consola sau prin interfata grafica? (raspundeti cu 1 sau 2)\n 1.Consola\n 2.-gui\n ")
            if interface in ['1', '2']:
                raspuns_valid = True
            else:
                print("Nu ati ales o varianta corecta.")

    # initializare tabla
    Joc.NR_LINII = N
    Joc.NR_COLOANE = M
    tabla_curenta = Joc()
    nr_mut_calc = 0
    nr_mut_util = 0
    print("Tabla initiala")
    print(str(tabla_curenta))
    lista_timpi = []
    # creare stare initiala
    stare_curenta = Stare(tabla_curenta, 'x', adancime)

    if (len(interfata) == 1 or interface == '2'):
        # setari interf grafica
        time1_tot = int(round(time.time() * 1000))
        pygame.init()
        pygame.display.set_caption('x si 0')
        # dimensiunea ferestrei in pixeli
        ecran = pygame.display.set_mode(size=(M*81-1, N*81-1))  # Nrc*100+Nrc-1, Nrl*100+Nrl-1

        # de_mutat = False
        patratele = deseneaza_grid(ecran, tabla_curenta.matr, N, M)
        while True:

            if (stare_curenta.j_curent == Joc.JMIN):
                # muta jucatorul
                # preiau timpul in milisecunde de dinainte de mutare
                t_inainte = int(round(time.time() * 1000))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:

                        pos = pygame.mouse.get_pos()  # coordonatele clickului

                        for np in range(len(patratele)):

                            if patratele[np].collidepoint(pos):
                                linie = np // M
                                coloana = np % M
                                ###############################
                                '''
                                if stare_curenta.tabla_joc.matr[linie * N + coloana] == Joc.JMIN:
                                    
                                    if (de_mutat and linie == de_mutat[0] and coloana == de_mutat[1]):
                                        # daca am facut click chiar pe patratica selectata, o deselectez
                                        de_mutat = False
                                        deseneaza_grid(ecran, stare_curenta.tabla_joc.matr, N, M)
                                    else:
                                        de_mutat = (linie, coloana)
                                        # desenez gridul cu patratelul marcat
                                        deseneaza_grid(ecran, stare_curenta.tabla_joc.matr, N, M, np)
                                '''
                                if stare_curenta.tabla_joc.matr[linie * M + coloana] == Joc.GOL:
                                    '''
                                    if de_mutat:
                                        #### eventuale teste legate de mutarea simbolului
                                        stare_curenta.tabla_joc.matr[de_mutat[0] * M + de_mutat[1]] = Joc.GOL
                                        de_mutat = False
                                    '''
                                    # dupa iesirea din while sigur am valide atat linia cat si coloana
                                    # deci pot plasa simbolul pe "tabla de joc"
                                    stare_curenta.tabla_joc.matr[linie * M + coloana] = Joc.JMIN
                                    nr_mut_util += 1
                                    Joc.ult_mut_jmin_idxlist = linie * M + coloana
                                    # afisarea starii jocului in urma mutarii utilizatorului
                                    print("\nTabla dupa mutarea jucatorului")
                                    print(str(stare_curenta))
                                    # preiau timpul in milisecunde de dupa mutare
                                    t_dupa = int(round(time.time() * 1000))
                                    print("Utilizatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
                                    patratele = deseneaza_grid(ecran, stare_curenta.tabla_joc.matr, N, M)
                                    # testez daca jocul a ajuns intr-o stare finala
                                    # si afisez un mesaj corespunzator in caz ca da
                                    if (afis_daca_final(stare_curenta)):
                                        break

                                    # S-a realizat o mutare. Schimb jucatorul cu cel opus
                                    stare_curenta.j_curent = stare_curenta.jucator_opus()

            # --------------------------------
            else:  # jucatorul e JMAX (calculatorul)
                # Mutare calculator
                # preiau timpul in milisecunde de dinainte de mutare
                t_inainte = int(round(time.time() * 1000))

                if tip_algoritm == '1':
                    stare_actualizata = min_max(stare_curenta)
                else:  # tip_algoritm==2
                    stare_actualizata = alpha_beta(-500, 500, stare_curenta)

                poz_mut = 0
                for idx in range(len(stare_curenta.tabla_joc.matr)):
                    if stare_curenta.tabla_joc.matr[idx] != stare_actualizata.stare_aleasa.tabla_joc.matr[idx]:
                       poz_mut = idx
                       break
                stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
                nr_mut_calc += 1
                Joc.ult_mut_jmax_idxlist = poz_mut

                print("Tabla dupa mutarea calculatorului")
                print(str(stare_curenta))

                patratele = deseneaza_grid(ecran, stare_curenta.tabla_joc.matr, N, M)
                # preiau timpul in milisecunde de dupa mutare
                t_dupa = int(round(time.time() * 1000))
                print("Calculatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
                lista_timpi.append(t_dupa - t_inainte)
                if (afis_daca_final(stare_curenta)):
                    break

                # S-a realizat o mutare. Schimb jucatorul cu cel opus
                stare_curenta.j_curent = stare_curenta.jucator_opus()
        print("\nTimpul minim al calculatorului este ", min(lista_timpi), " milisecunde.\n")
        print("\nTimpul maxim al calculatorului este ", max(lista_timpi), " milisecunde.\n")
        print("\nMedia calculatorului este ", statistics.mean(lista_timpi), " milisecunde.\n")
        print("\nMediana calculatorului este ", statistics.median(lista_timpi), " milisecunde.\n")
        print("\nNumar mutari utilizator este ", nr_mut_util, "\n")
        print("\nNumar mutari calculator este ", nr_mut_calc, "\n")
        time2_tot = int(round(time.time() * 1000))
        print("\nJocul a durat in total " + str(time2_tot-time1_tot) + " milisecunde.")

    else:
        time1_tot = int(round(time.time() * 1000))
        while True:
            if (stare_curenta.j_curent == Joc.JMIN):
                # muta utilizatorul

                print("Acum muta utilizatorul cu simbolul", stare_curenta.j_curent)
                # preiau timpul in milisecunde de dinainte de mutare
                t_inainte = int(round(time.time() * 1000))
                raspuns_valid = False
                while not raspuns_valid:
                    try:
                        # utilizatorul poate opri jocul la orice mutare doreste
                        linie = input("linie=")
                        if linie.lower() == "exit":
                            sys.exit()
                        coloana = input("coloana=")
                        if coloana.lower() == "exit":
                            sys.exit()

                        linie = int(linie)
                        coloana = int(coloana)

                        if (linie in range(Joc.NR_COLOANE) and coloana in range(Joc.NR_COLOANE)):
                            if stare_curenta.tabla_joc.matr[linie * Joc.NR_COLOANE + coloana] == Joc.GOL:
                                raspuns_valid = True
                            else:
                                print("Exista deja un simbol in pozitia ceruta.")
                        else:
                            print("Linie sau coloana invalida (trebuie sa fie unul dintre numerele 0,1,2).")

                    except ValueError:
                        print("Linia si coloana trebuie sa fie numere intregi")

                # dupa iesirea din while sigur am valide atat linia cat si coloana
                # deci pot plasa simbolul pe "tabla de joc"
                stare_curenta.tabla_joc.matr[linie * Joc.NR_COLOANE + coloana] = Joc.JMIN
                nr_mut_util += 1
                Joc.ult_mut_jmin_idxlist = linie * Joc.NR_COLOANE + coloana
                # afisarea starii jocului in urma mutarii utilizatorului
                print("\nTabla dupa mutarea jucatorului")
                print(str(stare_curenta))
                # preiau timpul in milisecunde de dupa mutare
                t_dupa = int(round(time.time() * 1000))
                print("Utilizatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
                # testez daca jocul a ajuns intr-o stare finala
                # si afisez un mesaj corespunzator in caz ca da
                if (afis_daca_final(stare_curenta)):
                    break

                # S-a realizat o mutare. Schimb jucatorul cu cel opus
                stare_curenta.j_curent = stare_curenta.jucator_opus()

            # --------------------------------
            else:  # jucatorul e JMAX (calculatorul)
                # Mutare calculator

                print("Acum muta calculatorul cu simbolul", stare_curenta.j_curent)
                # preiau timpul in milisecunde de dinainte de mutare
                t_inainte = int(round(time.time() * 1000))

                # stare actualizata e starea mea curenta in care am setat stare_aleasa (mutarea urmatoare)
                if tip_algoritm == '1':
                    stare_actualizata = min_max(stare_curenta)
                else:  # tip_algoritm==2
                    stare_actualizata = alpha_beta(-500, 500, stare_curenta)

                poz_mut = 0
                for idx in range(len(stare_curenta.tabla_joc.matr)):
                    if stare_curenta.tabla_joc.matr[idx] != stare_actualizata.stare_aleasa.tabla_joc.matr[idx]:
                        poz_mut = idx
                        break
                stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
                nr_mut_calc += 1
                Joc.ult_mut_jmax_idxlist = poz_mut

                stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc  # aici se face de fapt mutarea

                print("Tabla dupa mutarea calculatorului")
                print(str(stare_curenta))

                # preiau timpul in milisecunde de dupa mutare
                t_dupa = int(round(time.time() * 1000))
                print("Calculatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
                lista_timpi.append(t_dupa - t_inainte)
                if (afis_daca_final(stare_curenta)):
                    break

                # S-a realizat o mutare.  jucatorul cu cel opus
                stare_curenta.j_curent = stare_curenta.jucator_opus()

        print("\nTimpul minim al calculatorului este ", min(lista_timpi), " milisecunde.\n")
        print("\nTimpul maxim al calculatorului este ", max(lista_timpi), " milisecunde.\n")
        print("\nMedia calculatorului este ", statistics.mean(lista_timpi), " milisecunde.\n")
        print("\nMediana calculatorului este ", statistics.median(lista_timpi), " milisecunde.\n")
        print("\nNumar mutari utilizator este ", nr_mut_util, "\n")
        print("\nNumar mutari calculator este ", nr_mut_calc, "\n")
        time2_tot = int(round(time.time() * 1000))
        print("\nJocul a durat in total " + str(time2_tot - time1_tot) + " milisecunde.")

if __name__ == "__main__":
    main()
    '''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    '''
##functie pentru indici in clasa joc
