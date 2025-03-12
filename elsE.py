# Dateien
from shutil import Error
from movement import * 
from communication import *
#from main import *
from move import *

# Packages
import paho.mqtt.client as mqtt
from typing import List, Dict, Optional, Tuple

Node = Tuple[int,int]

def get_ready(talk: Communication) -> Node:
    # Ziel dieser Funktion ist, dass der Roboter am Ende die send_message_ready Nachricht an das Mutterschiff schickt und vom gefundenen Knoten startet
    
    # Umgebung abfragen
    env : int = check_environment() 
    active_node : Node

    # Der Roboter befindet sich auf einem Knoten -> Scanne Wege
    if env == 1 :
        # schicke an den Server die Nachricht das er bereit ist
        talk.send_message_ready()
        time.sleep(3)
        active_node = (talk.Xs,talk.Ys) # Fehlermeldung kann ignoriert werden
        rotate_and_scan(int_to_direction(talk.Ds)) # Umdrehung und Wege scannen
    
        return active_node
    # Der Roboter befindet sich auf einem Weg -> Linefollowing
    elif env == 2 :
        linefollow()
        
        # schicke an den Server die Nachricht das er bereit ist
        talk.send_message_ready()
        time.sleep(3)

        # Jetzt hat der Roboter Informationen über seinen Standpunkt
        active_node = (talk.Xs,talk.Ys) # Fehlermeldung kann ignoriert werden
        rotate_and_scan(int_to_direction(talk.Ds)) # Umdrehung und Wege scannen
    
        return active_node
    # Der Roboter hat keine Ahnung was er machen soll -> Teile es dem Team mit
    else:
        print("Ich komme zu keinem eindeutigen Ergebniss")
        # Warnton
        raise Error

def depth_first_search(talk: Communication, planet : Planet, active_node : Node) -> None:
    # Tiefensuche

    # Zu erst sollen nach möglichen Wegen gesucht werden
    # Hinwesi: Schließe den Weg aus, ausdem du gekommen bist
    directions : List[Direction] = rotate_and_scan(talk.Ds)
    print(talk.Ds)
    print(directions)
    print(talk.planetName)
    # Jetzt werden auf allen Wegen ebenfalls die Tiefensuche angewendete
    for direction in directions:
        # Der Roboter soll sich in diese Himmelsrichtung ausrichten
        if direction_to_int(direction) + talk.Ds == talk.Ds:
            continue
        else:
            rel_rotation(direction,talk)
        # follge erstmal die Himmelsrichtung, um herauszufinden ob es in diese Richtung einen Knoten gibt
        found_node : Optional[Tuple[Tuple[int,int],Direction,Weight]] = linefollow(talk,planet,(active_node,direction))
        # Falls ein Knoten gefunden wurde soll ebenfalls auf diesem Knoten die Teifensuche angewendet werden, nach dem der Eingtrag im planet gemacht wurde
        if found_node != None: 
            
            line_weight : int = found_node[2]
            node_coordinates : Tuple[int,int] = found_node[0]
            direction_from_which_the_robot_came : Direction = found_node[1]

            # Gefundener Weg soll gespeichert werden
            planet.add_path((active_node,direction),(node_coordinates,direction_from_which_the_robot_came),line_weight)
            
            depth_first_search(talk, planet,node_coordinates)
        else:
            # Wenn kein Knoten gefunden wurde dann mache nichts
            pass
        # jetzt soll er zu dem Knoten zurückgehen von dem er gekommen ist

def breadth_first_search(talk : Communication, planet : Planet, active_node : Tuple[int,int],examined_nodes : Dict[Tuple[int,int],bool] = {}) -> None:
    # Breitensuche

    # Zu erst soll nach möglichen Wegen gesucht werden
    directions : List[Direction] = rotate_and_scan(talk.Ds)

    # Auf allen gefunden Wegen soll jetzt abgelaufen werden
    for direction in directions:
        # Der Roboter soll sich in diesen Himmelsrichtung ausrichten
        rel_rotation(direction)
        # gehe in die Himmelsrichtung, um herauszufinden ob es in diese Richtung einen Knoten gibt
        found_node : Optional[Tuple[Tuple[int,int],Direction,Weight]] = linefollow()
        if found_node != None:
            
            line_weight : int = found_node[2]
            node_coordinates : Tuple[int,int] = found_node[0]
            direction_from_which_the_robot_came : Direction = found_node[1]
            examined_nodes[node_coordinates] = False
            
            # Gefundener Weg soll gespeichert werden
            planet.add_path((active_node,direction),(node_coordinates,direction_from_which_the_robot_came),line_weight)
            # jetzt soll der Roboter wieder zum active_node zurück gehen
        else:
            # Wenn kein Knoten gefunden wurde dann mache nichts
            pass

    # Hinweis: Der Roboter sollte sich jetzt auf dem active_node befinden
    # Der Roboter wendet jetzt auf alle Knoten in examined_nodes die Breitensuche an, die noch nicht untersucht wurden
    for node in examined_nodes.keys():
        if examined_nodes[node] == True:
            breadth_first_search(talk,planet,node,examined_nodes)

# def sendMessage(planet: Planet, talk: Communication, msg : str):
#    # diese gesamte Funktion kann theoretisch unbrauchbwar werden, wenn sich das Prblem mit dem Deplay bzw. mit dem zurückgegeben der Infos anders lösten lässt
#
#    if msg == "send_message_ready":
#        talk.send_message_ready()
#        time.sleep(3) # Das Warten kann vielleicht in communication Klasse ausgelagert werden
#        try:
#            (talk.planetName,talk.Xs,talk.Ys,talk.Ds) 
#        except:    
#            # Warnton
#           pass
#
#    elif msg == "pathSelect":
#        talk.send_message_pathSelect()
#        time.sleep(3)
#        try:
#            (talk.planetName,talk.Xs,talk.Ys,talk.Ds) 
#        except:    
#            # Warnton
#            pass

def go_to_node(start : Node, target : Node) -> Optional[bool]: 
    pass
