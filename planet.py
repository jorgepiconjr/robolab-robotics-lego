from enum import IntEnum, unique
import sys as sys 
from typing import Optional, List, Tuple, Dict

@unique
class Direction(IntEnum):
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270

Weight = int
Node = Tuple[int,int]

class Planet:

    def __init__(self):
        # Aufbau: { (x,y) : { gehe_in_Himmelsrichtung : ((x_Nachbar,y_Nachbar), komme_aus_Himmelrichtung, Gewicht) } }
        self.paths: Dict[Tuple[int,int],Dict[Direction,Tuple[Tuple[int,int],Direction, Weight]]] = {}
        
        # Dieses Dictornary speichert den Status der Himmelsrichtungen aller Knoten
        # True = blockiert
        # False = frei
        self.blocked_paths : Dict[Node,Dict[Direction, bool]] = {}
        
        # Dieses Dictonary soll alle Knoten speichern, mit den Himmelsrichtungen die bekannt sind, aber nicht untersucht wurden
        # True = untersucht
        # False = bekannt, aber noch nicht untersucht
        self.known_but_not_examined_paths : Dict[Node,Dict[Direction,bool]] = {}

    def add_path(self, me: Tuple[Tuple[int, int], Direction], neighbour: Tuple[Tuple[int, int], Direction], weight: Weight):

        # Falls dieser Knoten noch keinen Eintrag hat, dann kann er in path so gespeichert werden
        if me[0] not in self.paths.keys():
            self.paths[me[0]] = { me[1] : (neighbour[0],neighbour[1], weight) }

        # Falls der Startknoten bereits in planet.paths vorhanden ist, dann soll der Eintrag so gespeichert werden, 
        # weil der alte Wert sonst überschrieben werden würde
        else:
            self.paths[me[0]][me[1]] = (neighbour[0],neighbour[1], weight)
 
        # Das Gleich wie oben, allerdings mit dem Zielknoten, damit dieser Weg in beide Richtung gespeichert wird
        if neighbour[0] not in self.paths.keys():
            self.paths[neighbour[0]] = { neighbour[1] : (me[0],me[1], weight) }
        else:
            self.paths[neighbour[0]][neighbour[1]] = (me[0],me[1], weight)

#    def remove_path(self, me: Tuple[Tuple[int, int], Direction], neighbour: Tuple[Tuple[int, int], Direction]):
#
#        # Entferne den Weg vom Startknoten in dieser Himmelsrichtung
#        self.paths[me[0]].pop(me[1])
#
#        # Entferne den Weg vom Zielknoten in dieser Himmelsrichtung
#        self.paths[neighbour[0]].pop(neighbour[1])
    
    def edit_not_examined_paths(self, node : Node, direction : Direction, examined : bool) -> None:
        # Diese Funktion soll eine es möglich machen mit dem Dict known_but_not_examined_paths zu arbeiten

        # Falls der Knoten nicht in der Liste steht soll der Eintrag einfach so gespeichert werden
        if node not in self.known_but_not_examined_paths.keys():
            
            self.known_but_not_examined_paths[node] = { direction : examined }
       
        # Falls der Knoten bereits vorhanden ist, dann soll nur der Wert überschrieben werden
        else:
            
            self.known_but_not_examined_paths[node][direction] = examined

#    def edit_blocked_paths(self, node : Node, direction : Direction, blocked : bool) -> None:
#
#        if node not in self.blocked_paths.keys():
#            self.blocked_paths[node] = { direction : blocked }
#        else:
#            self.blocked_paths[node][direction] = blocked

    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:
        # Diese Funktion soll einfach alle Wege zurück gegeben

        return self.paths

    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Optional[List[Tuple[Tuple[int, int], Direction]]]:
        # Diese Funktion bestimmt den kürzesten Weg zwischen zwei Knoten, falls der Weg unmöglich ist oder die Länge 0 hat, dann soll None zurück gegeben werden

        active_node: Tuple[int,int] = start # der aktuelle Knoten der untersucht wird
        found_nodes : Dict[Tuple[int,int],Weight] = {} # der akutelle mindeste Wert, um zu diesen Knoten zu kommen
        nodes_with_predecessor : Dict[Tuple[int,int],Tuple[int,int]] = {}
        final_path : List[Tuple[Tuple[int,int],Direction]] = [] # die Liste wird am Ende zurück gegeben
        examined_nodes : Dict[Tuple[int,int],Weight] = {} # liste an Knoten, die bereits untersucht wurden und nicht mehr angefasst werden sollen
        
        # der start-Knoten muss zu examined_nodes hinzugefügt werden, damit die Gewichtsberechnung im ersten Durchlauf funktioniert
        examined_nodes[start] = 0

        # man muss nur soviele Knoten untersuchen, wieviel auch Informationen über Himmelsrichtungen haben
        for i in range(len(self.paths.keys())):
            
            # es sollen die Eingträge aktualiesiert, wenn dieser Knoten vom aktuellen Knoten erreichbar ist
            for directions in self.paths[active_node].keys():
                # Gesamtgewichtung bis zu dem Nachbar
                directions_weight: Weight = self.paths[active_node][directions][2] + examined_nodes[active_node]
                # Falls der Weg ein Gewicht von -1 hat, dann soll dieser Pfad ignoriert werden
                if self.paths[active_node][directions][2] == -1:
                    # Diese Schleife soll dann übersprungen werden
                    continue
                # Der besagte Nachbar in diese Himmelsrichtung
                neighbour : Tuple[int,int] = self.paths[active_node][directions][0]
                # Aktualisiere die Informationen über diesen Nachbarn,wenn
                # (1) dieser Knoten noch keinen Eingtrag hat
                # (2) Wenn die neue Gewichtung (directions_weight) kleiner ist als die bereits vorhandene
                # Dieser Nachbar kann ignoriert werden, wenn er bereits untersucht wurde
                # Die Stuktur ist (...) and (...) , weil es sein kann dieser Knoten bereits untersucht wurde und das deshalb sein Eintrag in found_nodes gelöscht wurde
                if ((neighbour not in found_nodes.keys()) or (directions_weight < found_nodes[neighbour])) and (neighbour not in examined_nodes.keys()):
                    found_nodes[neighbour] = directions_weight
                    # der Knoten mit dem kleinsten Gewicht soll den aktiven Knoten jetzt als seinen Vorgänger erhalten
                    nodes_with_predecessor[neighbour] = active_node

            # Von allen jetzt bekannten Wegen soll jetzt der mit der geringsten Gewichtung gefunden werden
            lightest_weight: Weight = -1 # das kleinste Gewicht
            coordinates_of_node_with_lightest_weight : Tuple[int,int] = active_node # Koordinanten des Knoten mit dem kleinsten Gewicht, welcher dannach auch der neue aktive Knoten werden soll
            
            for nodes in found_nodes:
                # ein Knoten soll dann als Knoten mit dem kleinsten Gewicht gewertet werden, wenn
                # (1) lightest_weight = -1 , weil dieser Wert als Hinweis dient, dass es ein neuer Durchlauf ist
                # (2) sein Gewichtung in found_nodes kleiner ist, als der akutuelle kleinste Wert
                if (lightest_weight == -1) or (found_nodes[nodes] < lightest_weight):
                    lightest_weight = found_nodes[nodes]
                    coordinates_of_node_with_lightest_weight = nodes

            # der Knoten coordinates_of_node_with_lighstest_weight wird jetzt zum neuen aktiven Knoten
            # dafür wird erhält dieser Knoten einen eigenen Eintrag in examined_nodes
            active_node = coordinates_of_node_with_lightest_weight
            examined_nodes[active_node] = lightest_weight
            # außerdem muss der neue aktive Knoten jetzt aus found_nodes entfernt werden
            if active_node in found_nodes:
                found_nodes.pop(active_node)

        # Jetzt haben wir eine List mit der kleinsten Gewichtung um diesen Knoten zu erreichen
        # Wir wissen jetzt nicht, ob das Ziel in dieser Liste ist
        # Sollte target nicht erreicht worden sein, dann wird None zurückgegeben
        if target not in nodes_with_predecessor.keys():
            return None
        # Sollte target erreicht worden sein, dann muss jetzt final_path erstellt werden
        else:
            # wir gehen jetzt nodes_with_predecessor rückwerts durch, beginnend bei target
            back_node : Tuple[int,int] = target
            # wir gehen solange rückwerts bis der nächste Knoten von dem man den Vorgänger erhalten möchte, der Start-Knoten ist
            while back_node != start:
                # wir brauchen für final_path die Himmelsrichtung
                predecessor : Tuple[int,int] = nodes_with_predecessor[back_node]
                # wir gehen jetzt alle Himmelsrichtungen vom Vorgänger durch, um herauszufinden in welche Richtung der back_node sich befinden
                # der Vorgänger (predecessor) und die Himmelsrichtung wird dann in final path als Tupel angespeichert
                for directions in self.paths[predecessor].keys():
                    if self.paths[predecessor][directions][0] == back_node:
                        final_path.append((predecessor,directions))
                        # falls es mehrere Wege gibt mit der selben gewichtung von predecessor zum back_node, sollte dieser break dafür sorgen das nicht mehrere Optionen in final_path stehen
                        break
                back_node = predecessor
            # am Ende soll die fertige Liste zurückgegeben werden - und zwar rückwerts
            return final_path[::-1]

    def calc_path_length(self, path : Optional[List[Tuple[Node,Direction]]]) -> int:
        # Diese Funktion soll die gesamte Distanz eines Weges berechnen, welcher durch shortest_path berechnet wurde


        summ : int = 0

        # Falls die Liste None ist bedeutet dies das die Liste eine Länge von 0 hat, was zurückgegeben werden soll
        if path == None:
            
            return 0

        # Falls die Liste nicht leer ist sollen alle Elemente dieser Liste durchlaufen werden und die Distans zwischen diesem Knoten und den Nachbarknoten berechnet werden, 
        # welcher laut planet.path sich in dieser Himmelsrichtung befindet
        else:
            
            # Die Liste path wird durchlaufen
            for node in path:

                # Der Wert für diesen Weg in dieser Richtung wird zum gesamt Wert addiert
                summ = summ + self.paths[node[0]][node[1]][2]

            return summ
