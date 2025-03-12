### Probleme ###
# (1) Wie gehen wir bei der Erkundung vor? Die Teilfunktionen soll dann nur aufgerufen werden.
# (2) Ich bin mir noch nicht sicher, wann ich wie die Kommunikation mit dem Server einbinden soll. Deshalb hoffe ich auf die gute Wiki.
# (3) Ähnliches gilt für die Bewegungsfunktionen

# Dateien
from communication import Communication
from odometry import Odometry
from planet import Direction, Planet, Weight
from robot import *

# Packages
import paho.mqtt.client as mqtt
import uuid
import signal
import movement
import os
import time
import logging
from typing import List, Dict, Optional, Tuple

client = None
Node = Tuple[int,int]

def run():
    # DO NOT CHANGE THESE VARIABLES
    #
    # The deploy-script uses the variable "client" to stop the mqtt-client after your program stops or crashes.
    # Your script isn't able to close the client after crashing.
    global client
    
    # Im folgenden Dictornary sollen alle Wege gespichert werden die untersucht worden, aber blockiert sind (was sich ändern kann)
    # Diese Wege sollen/können nicht im planet gespeichert werden
    #global blocked_paths
    #blocked_paths : Dict[Node,Direction] = {}

    client_id = '20-' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
    client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                         clean_session=True,  # We want a clean session after disconnect or abort/crash
                         protocol=mqtt.MQTTv311  # Define MQTT protocol version
                         )
    # Setup logging directory and file
    curr_dir = os.path.abspath(os.getcwd())
    if not os.path.exists(curr_dir + '/../logs'):
        os.makedirs(curr_dir + '/../logs')
    log_file = curr_dir + '/../logs/project.log'
    logging.basicConfig(filename=log_file,  # Define log file
                        level=logging.DEBUG,  # Define default mode
                        format='%(asctime)s: %(message)s'  # Define default logging format
                        )
    logger = logging.getLogger('RoboLab')

    # THE EXECUTION OF ALL CODE SHALL BE STARTED FROM WITHIN THIS FUNCTION.
    # ADD YOUR OWN IMPLEMENTATION HEREAFTER.
    planet : Planet = Planet()
    talk : Communication = Communication(client,logger)
    frodo : Robot = Robot(planet, talk)

    # Farbkalibrierung
    frodo.robot_interaction.new_calibration()
    # Startsound
    frodo.robot_interaction.tour_sound()
    # Der Roboter folgt der ersten Linie zum Startknoten
    frodo.moves.follow_line()
    # Der Roboter soll die ready-Nachricht senden
    frodo.send_ready()
    # Startprogram - scane Umgebung und entscheide wie es losgehen soll
    frodo.examine_planet()
    # Endsound
    frodo.robot_interaction.tour_sound()

# DO NOT EDIT
def signal_handler(sig=None, frame=None, raise_interrupt=True):
    if client and client.is_connected():
        client.disconnect()
    if raise_interrupt:
        raise KeyboardInterrupt()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    try:
        run()
        signal_handler(raise_interrupt=False)
    except Exception as e:
        signal_handler(raise_interrupt=False)
        raise e
