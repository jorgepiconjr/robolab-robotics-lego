# !/usr/bin/env python3
import math

class Odometry:
    def __init__(self):
        """
        Initializes odometry module
        """

        # YOUR CODE FOLLOWS (remove pass, please!)

        # Liste der Triebwerksticks nach dem Rad
        self.listl = []
        self.listr = []


    def distance_lr_berechnung(self, l_ticks, r_ticks):
    # Berechnung des Weges für jedes Rad(link, recht) in jedem Intervall, in cm
    # 5,5 Raddurchmesser
    # 1 Umdrehung des Rades entspricht 360 Ticks

        dl = (5.5 * math.pi * l_ticks) / 360
        dr = (5.5 * math.pi * r_ticks) / 360

        return dl, dr


    def alpha_berechnung(self, l_ticks, r_ticks):
    # Berechnung des Alphawinkels nach Intervallen
    # 9 (in cm) Abstand zwischen beiden Rädern

        dl, dr = self.distance_lr_berechnung(l_ticks, r_ticks)

        alpha = (dr - dl) / 9

        # alpha wird im Bogenmaß zurückgegeben
        return alpha

    def distance_s_berechnung(self, l_ticks, r_ticks):
    # Berechnung der geraden Strecke, die unter dem Bogen der Differenz des
    # linken und rechten Radweges gebildet wird

        # Berechnung von Alpha für dieses Intervall
        alpha = self.alpha_berechnung(l_ticks, r_ticks)

        # Im Falle von Alpha 0 gibt es keine Wegdifferenz, also auch kein S.
        # Der Weg würde als durch das linke = rechte Rad gegeben angenommen werden.
        if alpha == 0:
            s, s_aux = self.distance_lr_berechnung(l_ticks, r_ticks)
            return s
        #Wenn es einen Unterschied zwischen den beiden Rädern gibt, berechnen wir S
        else:
            dl, dr = self.distance_lr_berechnung(l_ticks, r_ticks)
            s = (dr + dl) / alpha * math.sin(alpha/2)
            return s

    def dif_X(self, l_ticks, r_ticks, alte_alpha):
    # Wegdifferenz in cm entlang der x-Achse. Unter dem Intervall S

        # Berechnung von Alpha für dieses Intervall in Bezug auf die Strecke s
        alpha = self.alpha_berechnung(l_ticks, r_ticks) / 2
        # Berechnung der Entfernung s in cm
        s = self.distance_s_berechnung(l_ticks, r_ticks)
        # Berechnung des angrenzenden Katheters, da er die Differenz der Strecke der x-Achse berechnet.
        Angrenzende_Kathete = math.sin(alpha + alte_alpha) * s

        return Angrenzende_Kathete

    def dif_Y(self, l_ticks, r_ticks, alte_alpha):
    # Wegdifferenz in cm entlang der y-Achse. Unter dem Intervall S

        # Berechnung von Alpha für dieses Intervall in Bezug auf die Strecke s
        alpha = self.alpha_berechnung(l_ticks, r_ticks) / 2
        # Berechnung der Entfernung s in cm
        s = self.distance_s_berechnung(l_ticks, r_ticks)
        # Berechnung des anligenden Katheters, da er die Differenz der Strecke der y-Achse berechnet.
        Anliegende_Kathete = math.cos(alpha + alte_alpha) * s

        return Anliegende_Kathete

    def summe(self):
    # Gesamtberechnung aller Variablen, alle Intervalle werden addiert

        # Initialisierung mit 0, da sie für jeden einzelnen Pfad ausgewertet werden.
        l_ticks = 0
        r_ticks = 0
        dif_X_total = 0
        dif_Y_total = 0
        dif_alpha = 0
        alte_alpha = 0

        # Tick"-Datenerhebungszyklus
        for i in range(1, len(self.listl)):

            # Lesen von Ticks aus der Liste entsprechend dem aktuellen Zeitintervall
            l_ticks = self.listl[i] - self.listl[i-1]
            r_ticks = self.listr[i] - self.listr[i-1]
            # wird die Pfaddifferenz in X und Y mit dem vorherigen Ergebnis addiert, da ein Delta (d. h. die Summe aller Ergebnisse) gesucht wird.
            dif_X_total = dif_X_total + self.dif_X(l_ticks, r_ticks, alte_alpha)
            dif_Y_total = dif_Y_total + self.dif_Y(l_ticks, r_ticks, alte_alpha)
            #Das Delta-Alpha ist die Summe der vorherigen Alphas plus dem aktuellen Alpha des Intervalls.
            dif_alpha = self.alpha_berechnung(l_ticks, r_ticks) + alte_alpha
            # Unterstützung des aktuellen Gesamtalphas zur Verwendung in einem zukünftigen Intervall
            alte_alpha = dif_alpha

        # print(f"\nList L: {self.listl} \n")  -> für Performance auskommentiert
        # print(f"\nList R: {self.listr} \n")  -> für Performance auskommentiert
        #print(f"\nODOMETRIE:  difX:{dif_X_total} , difY:{dif_Y_total} , difAlpha{dif_alpha}\n")

        #Korrektur von Alpha, so dass der Alpha-Wert zwischen 0 und 2pi liegt
        # dif_alpha = self.dif_alpha_in_direction(dif_alpha)

        # werden die endgültigen Berechnungen des Deltas X,Y und das endgültige Alpha, d. h. die Richtung des Roboters, zurückgegeben.
        return dif_X_total, dif_Y_total, dif_alpha


    def list_leeren(self):
    #Funktion, um die Ticks-Listen der einzelnen Motoren zu leeren, da jeder Wert nach dem Pfad von 0, d.h. initial, geparst wird.

        self.listl = []
        self.listr = []


    def dif_alpha_in_direction(self, dif_alpha):
    # Richtungsberechnung anhand der aus dem Gesamtalpha-Differential gewonnenen Daten

        direction = 0

        # der Winkel muss zwischen 0 und 2pi liegen, sonst wird er angepasst.
        while dif_alpha <= 0:
            dif_alpha = dif_alpha + 2 * math.pi
        while dif_alpha >= 2 * math.pi:
            dif_alpha = dif_alpha - 2 * math.pi

        # je nach Ergebnis wird die Richtung angepasst, da der Roboter nur mit 4 Richtungen arbeitet (0,90,180,270)
        '''if 7 * math.pi / 4 < dif_alpha <= 2 * math.pi or 0 <= dif_alpha <= math.pi / 4: # NORD
            direction = 0
        elif math.pi / 4 < dif_alpha <= 3 * math.pi / 4: # WEST
            direction = math.pi / 2
        elif 3 * math.pi / 4 < dif_alpha <= 5 * math.pi / 4: # SÜD
            direction = math.pi
        elif 5 * math.pi / 4 < dif_alpha <= 7 * math.pi / 4: # OST
            direction = 3 * math.pi / 2
        '''
        return direction
