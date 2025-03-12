# Hinweis: das Szenarion, dass ein bereits freier Pfad während der Bewegung mit shortest_path blockiert werden kann (falls möglich) habe ich noch nicht berücksichtigt 
# für dieses Szenario fehlen auch die Nachrichten

#from movement import *
from types import coroutine
from communication import *
from movement import find_path
from moves import Moves
from planet import *
from to_ import *
from robot_interaction import *
from odometry import *

import time
import paho.mqtt.client as mqtt
from typing import List, Dict, Optional, Tuple

Node = Tuple[int,int]

class Robot:

    def __init__(self, planetx : Planet, talkx : Communication):
        self.planet : Planet = planetx
        self.talk : Communication = talkx
        self.robot_interaction : RobotInteraction = RobotInteraction()
        self.moves : Moves = Moves()

        self.target : Optional[Node] = None
        self.found_target : bool = False
        # self.done dient als Indikator, dass ein Planet vollständig erkundet wurde
        self.done = False 
        self.old_direction : int
        self.active_direction : int
        
        self.start : bool = True 
        self.old_node : Node
        self.active_node : Node
    
    def send_ready(self) -> None:
        # Diese Funktion soll die dem Mutterschiff sagen das der Roboter bereit ist
        # Außerdem erhält der Roboter damit die Startkoordinaten

        # self.talk.send_message_testPlanet("Anin") -> auskommentiert für Prüfung

        # Schicke an den Server die Nachricht das er bereit ist
        self.talk.send_message_ready()
        # Der Roboter soll 3 Sekunden warte, um sich zu sein, dass vom Mutterschiff eine Nachricht gekommen ist
        time.sleep(3)

        self.active_direction = self.talk.Ds
        self.active_node = (self.talk.Xs,self.talk.Ys)

    def path_unveiled(self) -> None:
        # Diese Funktion soll überprüfen ob es neue Pfade vom Mutterschiff gibt
        # Falls ja, dann werden diese in planet.paths gespeichert und danach wird die Liste mit den neuen Wege geleert

        # Sollte die Liste nicht leer sein, dann soll der Inhalt (also die Wege) gespeichert werden
        if self.talk.paths_unveiled != []:

            # Alle Wege in dieser Liste werden durchlaufen und gespeichert
            for path in self.talk.paths_unveiled:

                # Startknote und Startrichtung dieses Pfades
                found_start_node : Node = (path[0][0][0],path[0][0][1])
                found_start_direction : Direction = path[0][1]
                
                # Zielknoten und Zielrichtung dieses Pfades
                found_target_node : Node = (path[1][0][0],path[1][0][1])
                found_target_direction : Direction = path[1][1]

                # Gewichtung
                found_path_weight : Weight = path[2]

                print("Der Server hat einen " + path[3] + " Pfad am Knoten : " + str(found_start_node) + " mit der Himmelsrichtung " + str(found_target_direction) + " gefunden.")

                # Der Weg wird in planet.paths gespeichert
                self.planet.add_path((found_start_node,found_start_direction),(found_target_node,found_target_direction), found_path_weight)

            # Nachdem alle Wege gepseichert wurden, soll dieses Liste geleert werden
            self.talk.paths_unveiled = []

    def rotate(self) -> None:
        # Diese Funktion macht nichts anderes außer den Roboter in die gewünchte absolute Himmelsrichtung auszurichten
        # Wichtig: Wenn diese Funktion verwendet wird, dann muss häufig Ds den Wert von De erhalten

        print("Das ist die neue Himmelsrichtung : " + str(self.talk.Ds)) # Das muss self.talk.Ds bleiben, weil self.active_direction nicht vom Server oder dem Program aktualisiert wird
        print("Der ist die alte Himmelsrichtung : " + str(self.old_direction))

        # Berechne die neue Himmelsrichtung
        new_direction : int = ((self.talk.Ds - self.old_direction) % 360) # Das muss self.talk.Ds bleiben, weil self.active_direction nicht vom Server oder dem Program aktualisiert wird


        # Debug-Info
        print("Der Roboter muss sich um : " + str(new_direction) + " Grad drehen")

        # Der Roboter soll sich jetzt drehen
        if new_direction == 0:
            pass
        elif new_direction == 90:
            self.moves.turn90()
        elif new_direction == 180:
            self.moves.turn180()
        elif new_direction == 270:
            self.moves.turn270()

    def search_target(self, target : Node) -> bool:
        # Diese Funktion soll True zurück gegben, wenn es das Ziel gibt und der Roboter es erreicht kann, ansonsten false
        # Hinweis: Diese Funktion soll target als Parameter nehmen, weil diese Funktion auch für den Weg zum nächsten noch nicht vollständig untersuchten Knoten gehen soll 

        # Es soll der Weg berechnet werden
        path_to_target : Optional[List[Tuple[Node,Direction]]] = self.planet.shortest_path((self.talk.Xs,self.talk.Ys),target)

        # Falls es keinen Weg gibt, dann wird diese Funktion beendet und False zurückgegeben
        if path_to_target == None:
            
            return False
        
        # Falls es einen Weg gibt, dann soll der Roboter diesen Weg nehmen bzw. sich in diese Richtung ausrichten
        else:

            self.active_direction = direction_to_int(path_to_target[0][1])

            return True

    def update_target(self) -> bool:
        # Diese Funktion soll überprüfen, ob der Roboter vom Mutterschiff ein Ziel erhalten hat
        # Falls ja, dann soll auch überprüft werden, ob er es erreichen kann
        # Falls dies möglich ist, dann soll nur die erste Himmelsrichtung als neue Himmelsrichtung festgelegt werden
        # In jedem anderen Fall wird false zurückgegeben

        # Zu erst soll überprüft werden, ob der Roboter bereits an seinem Ziel ist
        if (self.talk.Xs,self.talk.Ys) == self.target:
            
            print("Das Ziel wurde erreicht")

            self.talk.send_message_targetReached("Der Ring wurde zerstört")
            self.robot_interaction.comm_finished()

            self.found_target = True
            return True
        
        # Falls der Roboter eine Ziele erhalten hat, dann soll dieses Ziel gespeichert werden
        # Dies kommt vor dem Überprüfen, ob er das Ziel erreichen kann, weil sich das Ziel auch ändern kann
        if self.talk.new_target == True:
              
                print("Der Roboter ist auf dem Weg zum Ziel")
                # Die Zielkoordinaten werden gespeichert
                self.target = (self.talk.Xt,self.talk.Yt)

                # Debug-Info
                print("Ziel des Roboters ist : " + str(self.target))

        # Falls der Roboter ein Ziel hat, dann soll überprüft werden, ob er es aktuell erreichen kann
        if self.target != None:

            # Falls es zu diesem Knoten einen Weg gibt, dann soll der Roboter sich in Himmelsrichtung des nächsten Knotens ausrichten
            if self.search_target(self.target) == True:

                # Die aktuelle Himmelsrichtung muss zwischen gespeichert werden
                #self.old_direction = self.talk.Ds

                # Die Zielhimmelsrichtung wird zur neuen Himmelsrichtung
                #self.talk.Ds = self.active_direction
                
                # Debug-Info
                #print("Der Roboter richtet sich vom Knoten : " + str(self.active_node))
                # Der Roboter soll sich in diese Himmelsrichtung ausrichten
                #self.rotate()
                
                # Der Roboter soll jetzt dieser Linie folgen
                #self.moves.follow_line()

                self.examine()
                    
                return True

        return False

    def rotate_and_scan(self) -> None:
        # Diese Funktion soll nach dem möglichen Wegen dises Knotens suchen und diese mit der absoluten Himmelsrichtung in knonw_but_not_examined_paths speichern
        
        # Falls der akutelle Knoten keinen Eintrag in den bereits bekannten Knoten hat, dann muss dieser Knoten erstmal gescannt werden
        # Wichtig: es kann sein das dieser Knoten bereits in planet.path oder in planet.block_paths steht, weil der Roboter diese Information vom Mutterschiff erhalten hat
        # Der Grund warum dies bei path_unveiled nicht auf für known_but_not_examined_path gemacht wurde ist der, dass man nicht sicher sein, dass dadurch alle Wege dieses Knotens bekannt sind
        if (self.talk.Xs,self.talk.Ys) not in self.planet.known_but_not_examined_paths.keys():
               
            # Nur eine Debug-Info
            print("Der Aktulle Knoten : " + str((self.talk.Xs,self.talk.Ys)) + " wurde noch nicht gescannt")
                

            # Der Roboter scan sein Umgebung nach Pfaden mit der jeweiligen relativen Himmelsrichtung
            found_paths : List[bool] = self.moves.scan_node()

            # Debug-Info
            print("Das sind die gefundenen relativen Himmelsrichtungen : " + str(found_paths))
       
            # Die Liste mit den möglichen Wegen wird durchlaufen
            # i ist dabei die relative Himmelsrichtung
            # i = 0 -> Norden
            # i = 1 -> Osten
            # i = 2 -> Süden
            # i = 3 -> Westen
            for i in range(4):

                # Falls in dieser Himmelsrichtung ein Weg gefundne wurde, dann soll dieser gespeichert werden
                if found_paths[i] == True:

                    # Es wird die absolute Himmelsrichtung berechnet
                    new_direction : int = (((i*90) + self.talk.Ds) % 360)
                
                    # Debug-Info
                    print("In diser absoluten Himmelsrichtung : " + str(new_direction) + " wurde ein Weg erkannt und als noch nicht untersucht gespeichert")
                
                    # Diese Himmelsrichtung wird als nocht nicht untersucht (False) in known_but_not_examined_paths gespeichet
                    self.planet.edit_not_examined_paths((self.talk.Xs,self.talk.Ys),int_to_direction(new_direction),False)

            # Debug-Info
            print("Die aktullen bekannten Knoten mit ihren Richtung sind : " + str(self.planet.known_but_not_examined_paths))

            # Debug-Info
            print("Es wird jetzt überprüft, ob der Roboter bereits vom Mutterschiff Pfade mit diesem Knoten erhalten hat")

            # Es soll jetzt überprüfe werden, ob das Mutterschiff bereits Wege zu diesem Knoten erhalten hat, falls ja, dann werden die entsprechenden Himmelsrichtungen als untersucht markiert
            # Die blockiert Pfade werden durchsucht
            if self.active_node in self.planet.paths.keys():

                # Falls für diesen Knoten bereits ein Eintrag existiert sollen alle Himmelsrichtunge als untersucht markiert werden
                for direction in self.planet.paths[self.active_node].keys():

                    # Diese Himmelsrichtung wird jetzt in known_but_not_examined_paths als untersucht (True) markiert
                    self.planet.edit_not_examined_paths(self.active_node,direction,True)

                    # Debug-Info
                    print("Die absolute Himmelsrichtung : " + str(direction_to_int(direction)) + " wurde als untersucht markiert")

    def examine(self) -> None:
        # Diese Funktion soll immer ein Weg absuchen und dann NICHT zurück gehen (außer es gab ein Hindernis)
        # Außerdem übermittelt diese Funktion die Path-Select und Path-Nachricht
        # Ebenfalls aktualisiert diese Funktion die neuen Koordinaten und himmelsrichtung

        # Das Gleiche für die Koordinaten
        self.old_node = self.active_node

        # Für die entgültige Ausrichtung soll die aktuelle bzw. dann alte Himmelsrichtung gespeichert werden
        # self.old_direction = self.tak.Ds muss vor rotate() kommen, weil self.rotate() diesen Wert braucht
        self.old_direction = self.talk.Ds
        
        # Weil pathSelect nicht immer antwortet soll self.talk.Ds auf self.talk.active_direction gesetzt werden
        self.talk.Ds = self.active_direction
        
        # Die neue ausgewählte Himmelsrichtung soll dem Mutterschiff gesendet werden
        self.talk.send_message_pathSelect(self.talk.planetName,self.talk.Xs,self.talk.Ys,self.active_direction)
        self.robot_interaction.comm_finished()
        
        # Der Roboter soll 3 Sekunden warten falls vom Mutterschiff eine Korrektur kommt
        time.sleep(3)

        # Die neue Himmelsrichtung vom alten/aktuellen Knoten zum nächsten Ziel soll als untersucht markiert werden
        self.planet.edit_not_examined_paths((self.talk.Xs,self.talk.Ys),int_to_direction(self.talk.Ds),True)
        
        # Der Roboter soll sich jetzt in diese Himmelsrichtung ausrichten
        self.rotate()
        
        # Der Roboter folgt der aktullen/neuen Himmelsrichtung, um herauszufinden ob es in diese Richtung einen Knoten gibt
        if self.moves.follow_line() == True:

            # Die Zieldaten werden hier festgelegt, weil die Speicherung und Aktualisierung auf diesen Werten aufbaut
            # Die Werte kommen von der Odometry
            self.talk.De = 0 
            self.talk.Xe = self.moves.x
            self.talk.Ye = self.moves.y
 
            # Der Roboter übermittelt die path-Nachricht
            self.talk.send_message_path(self.talk.planetName,self.talk.Xs,self.talk.Ys,self.talk.Ds,self.talk.Xe,self.talk.Ye,self.talk.De,"free")
            self.robot_interaction.comm_finished()

            # Der Roboter wartet 3 Sekunden um sich sicher zu sein, dass das Mutterschiff antwortet mit den korrigierten Zielkoordinaten und Zielhimmelsrichtung
            time.sleep(3)
            
            # Jetzt werden die Zielkoordinaten zu den neuen Startkoordianten und die Zielrichtung zur neuen Startrichtung
            self.talk.Xs = self.talk.Xe
            self.talk.Ys = self.talk.Ye
            self.talk.Ds = ((self.talk.De + 180) % 360)

        # Fall : es gab ein Hindernis
        else:
            
            # Der Roboter übermittelt die path-Nachricht
            self.talk.send_message_path(self.talk.planetName,self.talk.Xs,self.talk.Ys,self.talk.Ds,self.talk.Xs,self.talk.Ys,self.talk.Ds,"blocked")
            self.robot_interaction.comm_finished()
            
            # Der Roboter wartet 3 Sekunden um sich sicher zu sein, dass das Mutterschiff antwortet mit den korigierten Zielkoordinaten und Zielhimmelsrichtung
            time.sleep(3)
            
            # Falls es ein Hindernis gab, kommt der Roboter zu seinem Startknoten zurück und die neue Himmelsrichtung entspricht der alten Himmelrichtung + 180 Grad
            self.talk.Ds = ((self.talk.Ds + 180) % 360)
       
        # Die Koordinanten des neuen Knotens sollen gespeichert werden
        self.active_node = (self.talk.Xs,self.talk.Ys)

        print("Dieser Pfad wird gespeichert : " + str(((self.old_node,int_to_direction(self.old_direction)),(self.active_node,int_to_direction(self.talk.De)), self.talk.pathWeight)))

        # Der neue Pfad soll gespeichert werden
        self.planet.add_path((self.old_node,int_to_direction(self.old_direction)),(self.active_node,int_to_direction(self.talk.De)), self.talk.pathWeight)
        
        # Debug-Info
        print("Bekannte Wege : " + str(self.planet.paths))


    def go_to_closest_neighbour(self) -> None:
        # Das Ziel dieser Funktion ist es, dass der Roboter zum nächsten Knoten geht mit noch nicht untersuchten Wegen

        # Dient als Indiaktor, dass der entsprechende Knoten in der Schleife der Erste ist
        closest_node_weight : int = -2
        closest_node : Optional[Node] = None
        closest_node_path = None

        # Debug-Info 
        print("Das sind die aktuelle bekannten Knoten mit ihren Himmelsrichtungen (go_to_closest_neighbour) : " + str(self.planet.known_but_not_examined_paths))

        # Es wird jetzt die Liste der noch nicht untersuchten Wege nach den noch nicht untersuchten Wegen gesucht
        for nodes in self.planet.known_but_not_examined_paths.keys():

            # Es werden alle Himmelsrichtung dieses Knotens durchsucht
            for direction in self.planet.known_but_not_examined_paths[nodes].keys():
                
                # Falls diese Himmelsrichtung noch nicht untersucht wurde (False), dann ist dieser Knoten eine Option 
                if self.planet.known_but_not_examined_paths[nodes][direction] == False:

                    # Debug-Info
                    print("Es wurde ein noch nicht untersuchter Weg gefunden : " + str(nodes) + " " + str(self.active_node))
                    
                    # Es wird jetzt der Weg zu diesem Knoten bestimmt
                    path : Optional[List[Tuple[Node,Direction]]] = self.planet.shortest_path(self.active_node,nodes)
                    
                    # Debug-Info
                    print("Das ist der kürzeste Weg zu diesem Knoten : " + str(path))

                    # Dann wird die Entfernung zu diesem Knoten berechnet
                    distance : int = self.planet.calc_path_length(path)

                    # Falls es der erste Knoten oder die Distance kleiner ist, dann wird dieser Knoten gespeichert 
                    if (closest_node_weight == -2) or (distance < closest_node_weight and closest_node_weight != -2):
                       
                        # Die Werte dieses Weges werden übernommen
                        closest_node_weight = distance
                        closest_node = nodes
                        closest_node_path = path
                
                    # Ein Knoten soll nicht mehrmals untersucht werden, falls dieser Knoten mehrere nocht nicht untersuchten Pfade hat
                    # Es soll die direction Schleife unterbrechen
                    break

        # Es soll jetzt überprüft werden, ob es einen Knoten in planet.paths gibt, welcher noch nicht in known_but_not_examined_paths befindet      
        if closest_node == None and closest_node_path == None:

            # Es wird jetzt die Liste der Wege durchlaufen
            for nodes in self.planet.paths.keys():

                # Falls diese Himmelsrichtung noch nicht untersucht wurde (False), dann ist dieser Knoten eine Option 
                if nodes not in self.planet.known_but_not_examined_paths.keys():

                    # Indikator, dass der anliegende Knoten erreichbar bzw. bekannt ist
                    reachable : bool = False

                    # Jetzt soll überprüft werden dass der anliegende Knoten in Known_but_examined_paths liegt damit, der Knoten erreichbar ist
                    for direction in self.planet.paths[nodes].keys():

                        needed_node : Node = self.planet.paths[nodes][direction][0] 
                        needed_direction : Direction = self.planet.paths[nodes][direction][1] 

                        if needed_node not in self.planet.known_but_not_examined_paths.keys():

                            continue

                        # Falls einer der Himmelsrichtungen des Verbindungsknoten bereits untersucht wurden, dann ist dier der Knoten erreichbar und akzeptabel
                        # Ebenfalls soll der Verbindungsknoten erreichbarsein, weil währen der Erkundung der Weg zum Verbindungsknoten blockiert werden kann
                        if self.planet.known_but_not_examined_paths[needed_node][needed_direction] == True and (self.planet.shortest_path((self.talk.Xs,self.talk.Ys),nodes) != None):

                            reachable = True

                    # Falls der Indikator immer noch False ist, bedeutet dies dass es für diese Knoten keinen Verbindungsknoten gibt und dieser Durchgang wird übersprungen
                    if reachable == False:

                        continue

                    # Debug-Info
                    print("Es wurde ein noch nicht untersuchter Knoten gefunden : " + str(nodes) + " " + str(self.active_node))
               
                    # Es wird jetzt der Weg zu diesem Knoten bestimmt
                    path : Optional[List[Tuple[Node,Direction]]] = self.planet.shortest_path(self.active_node,nodes)
                    
                    # Debug-Info
                    print("Das ist der kürzeste Weg zu diesem Knoten : " + str(path))

                    # Dann wird die Entfernung zu diesem Knoten berechnet
                    distance : int = self.planet.calc_path_length(path)

                    # Falls es der erste Knoten oder die Distance kleiner ist, dann wird dieser Knoten gespeichert 
                    if (closest_node_weight == -2) or (distance < closest_node_weight and closest_node_weight != -2):
                       
                        # Die Werte dieses Weges werden übernommen
                        closest_node_weight = distance
                        closest_node = nodes
                        closest_node_path = path
                
                    # Ein Knoten soll nicht mehrmals untersucht werden, falls dieser Knoten mehrere nocht nicht untersuchten Pfade hat
                    # Es soll die direction Schleife unterbrechen
                    break
       
        # Debug-Info
        print("Das sind die bekannten Pfade:" + str(self.planet.paths))
        
        # Falls closest_node nicht None ist, bedeutet dies es gibt noch Knoten mit noch nicht untersuchten Wegen
        if closest_node != None and closest_node_path != None:

            # Der Roboter soll sich jetzt zum nächsten Nachbarn ausrichten, welcher laut dem kürzesten Weg als nächstes genommen werde soll
            # Hinweis: Die Aktualisierung der neuen Himmelsrichtung wird von search_target übernohmen
            self.search_target(closest_node)

        # Falls closest_node None ist, dann bedeutet es, es gibt keinen weiteren Knoten mehr, der untersucht werden muss
        # Dadurch ist der Planet vollständig untersucht
        else:
            
            # self.done dient als Indikator, dass ein Planet vollständig erkundet wurde
            self.done = True
            self.talk.send_message_explorationCompleted("Frodo hat Mordo erreicht")
            self.robot_interaction.comm_finished()

    def go_to_next_node(self) -> None:
        # Diese Funktion ist praktisch gesehen die Erkundung des Planeten
        # Diese Funktion soll überprüfen, ob es am akutuellen Knoten einen noch nicht untersuchten Pfad gibt
        # Falls ja, dann soll der Roboter diesen Weg dem Mutterschiff mitteilen und entlanggefahren werden
        # Falls nein, dann soll der Roboter zum nächsten bekannten Knoten gehen mit noch nicht untersuchten Wegen

        # Diese Himmelsrichtung wird jetzt in known_but_not_examined_paths als untersucht (True) markiert
        # Die soll erst hier geschehen, weil es zu Konflikten kommen kann, wenn es er ausgeführt wird
        self.planet.edit_not_examined_paths((self.talk.Xs,self.talk.Ys),int_to_direction(self.talk.De) ,True)

        if self.update_target() == True:

            return
        
        # Es soll überprüft werden ob der Roboter ein Ziel hat, und falls ja, dann ob er es erreichen kann
        # Falls ja, dann soll der Roboter sich zu dem Ziel bewegen
        if self.found_target == False:
        
            # Dieser Wert soll auf True gesetzt werden, wenn es an diesem Knoten einen noch nicht untersuchten Weg gibt
            found_not_examined_path : bool = False

            # Es werden jetzt alle Himmelsrichtungen durchlaufen, die dem Roboter für diesem Knoten bekannt sind 
            for direction in self.planet.known_but_not_examined_paths[self.active_node].keys():

                # Falls eine Himmelsrichtung gibt die nocht nicht untersucht wurde (also in known_but_not_examined_paths mit False markiert ist), dann soll dieser Weg ausgewählt werden
                if self.planet.known_but_not_examined_paths[self.active_node][direction] == False:

                    # Debug-Info
                    print("Diese Richtung wurde noch nicht untersucht und wurde vorerst ausgewählt : " + str(direction_to_int(direction)))

                    # Es wurde ein Weg gefunden, weshalb dieser Indikator auf True gesetzt weden muss
                    found_not_examined_path = True

                    # die aktuelle Himmelsrichtung self.talk.Ds wird bereits auf die gewählte Himmelsrichtung gesetzt, weil alle kommenden Befehle darauf aufbau müssen, wegen der möglichen Korigierung
                    self.active_direction = direction_to_int(direction)

                    # Das break ist notwendig, weil der aktuelle Knoten nicht mehr mit dem Ausgangsknoten für diese Schleife übereinstimmt und damit die Himmelsrichtungen nicht
                    break
            
            # Falls es an diesem Knoten keine Wege mehr gibt, dann soll der Roboter zum nächsten Knoten mit noch nicht untersuchten Wegen gehen
            # Allerdings immer bis zum Nachbarknoten
            if found_not_examined_path == False:

                # Debug-Info
                print("Es gibt am aktullen Knoten keine Pfade mehr die untersucht werden sollen")
       
                # Der Kürzsteste Weg und die entsprechende Himmelsrichtung des Nachbarknoten sollen bestimmt werden
                self.go_to_closest_neighbour()

        # Dies ist notwendig, weil nach go_to_closest_neighbour self.done == True  sein kann, aber self.examine noch ausgeführt werden würde
        # Der Roboter würde dann eine falsche Erkundung zu viel machen
        # Das sefl.found_target dient hier nur als Sicherheit und kann bislang theoretisch weggelassen werden
        if self.done == False and self.found_target == False:

            # Nachdem die nächsten Himmelsrichtung ausgwählt wurde, soll der Roboter sich ausrichten und diesem Pfad folgen
            self.examine()

            self.active_direction = ((self.talk.De + 180) % 360)

    def examine_planet(self) -> None:
        # Das ist die Hauptfunktion
        
        # Solange der Roboter kein Ziel gefunden hat oder es keine nicht erkundeten Wege gibt, soll er den Planeten weiter erkunden
        while self.found_target == False and self.done == False:

            # Zu erst soll der Roboter überprüfen ob er vom Mutterschiff neue Pfade erhalten hat
            self.path_unveiled()

            # Der Roboter soll jetzt herausfinden, welche Wege es in welche Himmelsrichtungen gibt (falls der Knoten noch nicht bekannt ist)
            self.rotate_and_scan()

            if self.start == True:
                
                self.planet.edit_not_examined_paths((self.talk.Xs,self.talk.Ys),int_to_direction((self.talk.Ds + 180) % 360),True)
                
                self.start = False

            # Der Roboter soll jetzt zu seinem nächsten Ziel fahren
            self.go_to_next_node()

            print("Das sind die aktuellen bekannte Knoten mit ihren Himmelsrichtungen : " + str(self.planet.known_but_not_examined_paths))
            print("Schleifenende erreicht")
