#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import ssl
from typing import Optional, List

class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    # DO NOT EDIT THE METHOD SIGNATURE
    def __init__(self, mqtt_client, logger):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """
        # DO NOT CHANGE THE SETUP HERE
        self.client = mqtt_client
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.on_message = self.safe_on_message_handler
        # Add your client setup here

        # Aufbau einer mqtt-Verbindung, Broker-Zuweisung (TUD-Server)
        self.logger = logger
        self.client.username_pw_set('020', password='19wer609EM')
        self.client.connect('mothership.inf.tu-dresden.de', port=8883)

        # Explorer Handler Abonnement
        self.client.subscribe('explorer/020', qos=2)

        # Initiierung des Nachrichten-/Kommunikationszyklus
        self.client.loop_start()

        # Variablen zur Entgegennahme eingehender Daten und zum Senden
        self.planetName: Optional[str] = None
        self.Xs: int = 0
        self.Ys: int = 0
        self.Ds: int = 0
        self.Xe: int = 0
        self.Ye: int = 0
        self.De: int = 0
        self.msg: Optional[str] = None
        self.pathStatus: Optional[str] = None
        self.pathWeight: int = 0
        self.Xt: int = 0
        self.Yt: int = 0
        self.paths_unveiled: List = []
        self.new_target: bool = False

    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        # Zuordnung in "Payload" der vollständigen empfangenen Nachricht
        payload = json.loads(message.payload.decode('utf-8'))
        self.logger.debug(json.dumps(payload, indent=2))

        # YOUR CODE FOLLOWS (remove pass, please!)

        # Variable, um jede Nachricht nach Typ zu registrieren
        type_message = payload["type"]

        # Rückgabe von Nachrichten des Typs Client wird ignoriert
        if payload["from"] == "client":
            return
        # Debug-Meldungen sind für die Prüfung nicht relevant und werden daher ignoriert.
        if payload["from"] == "debug":
            return
        # Nur Server-Nachrichten werden entsprechend ihrem Typ gelesen.
        elif type_message == "planet":
        # Die Nachricht über den Planetentyp enthält Informationen über den aktuellen Planeten und die Startkoordinaten.

            # Lesen von Nachrichtendaten
            planet_Name = payload["payload"]["planetName"]
            start_X = payload["payload"]["startX"]
            start_Y = payload["payload"]["startY"]
            start_Orientation = payload["payload"]["startOrientation"]

            #Abonnement für das zweite Topic
            self.client.subscribe(f'planet/{planet_Name}/020', qos=2)

            # Erhebung von Daten über öffentliche Variablen
            self.planetName = planet_Name
            self.Xs = start_X
            self.Ys = start_Y
            self.Ds = start_Orientation

        elif type_message == "done":
        # Bei Erreichen eines Ziels erhält der Roboter eine solche Gratulationsnachricht

            # Lesen von Nachrichtendaten
            mensaje = payload["payload"]["message"]

            # Erhebung von Daten über öffentliche Variablen
            self.msg = mensaje

        elif type_message == "pathSelect":
        # Informationen zur ursprünglichen "Direction" im Falle einer Korrektur

            # Lesen von Nachrichtendaten
            start_Direction = payload["payload"]["startDirection"]

            # Erhebung von Daten über öffentliche Variablen
            self.Ds = start_Direction


        elif type_message == "path":
        # Erhält Informationen über den zuletzt gewählten Weg, d. h. die Größe zusammen mit den
        # korrekten Endkoordinaten und im Falle von Blocked ein -1

            # Lesen von Nachrichtendaten
            start_X = payload["payload"]["startX"]
            start_Y = payload["payload"]["startY"]
            start_Direction = payload["payload"]["startDirection"]
            endX = payload["payload"]["endX"]
            endY = payload["payload"]["endY"]
            endDirection = payload["payload"]["endDirection"]
            path_Status = payload["payload"]["pathStatus"]
            path_Weight = payload["payload"]["pathWeight"]

            # Erhebung von Daten über öffentliche Variablen
            self.Xs = start_X
            self.Ys = start_Y
            self.Ds = start_Direction
            self.Xe = endX
            self.Ye = endY
            self.De = endDirection
            self.pathStatus = path_Status
            self.pathWeight = path_Weight


        elif type_message == "pathUnveiled":
        # Enthält Informationen über einen Pfad, der noch nicht befahren wurde.

            # Lesen von Nachrichtendaten
            start_X = payload["payload"]["startX"]
            start_Y = payload["payload"]["startY"]
            start_Direction = payload["payload"]["startDirection"]
            endX = payload["payload"]["endX"]
            endY = payload["payload"]["endY"]
            endDirection = payload["payload"]["endDirection"]
            path_Status = payload["payload"]["pathStatus"]
            path_Weight = payload["payload"]["pathWeight"]

            # Erhebung von Daten über öffentliche Variablen
            self.paths_unveiled.append((((start_X, start_Y), start_Direction), ((endX, endY), endDirection), path_Weight, path_Status))


        elif type_message == "target":
        # Informationen über den Zielpunkt erhalten werden

            # Lesen von Nachrichtendaten
            targetX = payload["payload"]["targetX"]
            targetY = payload["payload"]["targetY"]

            # Erhebung von Daten über öffentliche Variablen
            self.new_target = True
            self.Xt = targetX
            self.Yt = targetY

    # DO NOT EDIT THE METHOD SIGNATURE
    #
    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.
    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """
        self.logger.debug('Send to: ' + topic)
        self.logger.debug(json.dumps(message, indent=2))

        # YOUR CODE FOLLOWS (remove pass, please!)

        # Eine Nachricht im Topic hinzufügen
        self.client.publish(topic, payload=json.dumps(message), qos=2)


    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"
    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        try:
            self.on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise



    # Funktionen zum Senden von Nachrichten nach ihrem jeweiligen Typ
    def send_message_testPlanet(self, planetName): # must be deactivated in the test
    # Übersendung des aktuellen Planeten an Mutterschiff

        # Nachricht
        payload = {"from": "client", "type": "testPlanet", "payload": {"planetName": planetName}}
        # Versendung/Veröffentlichung der Nachricht im jeweiligen Topic
        self.send_message("explorer/020", payload)

    def send_message_ready(self):
    # Von Roboter gesendete nachricht zur erkennung des ersten punktes auf dem planeten

        # Nachricht
        payload = {"from": "client", "type": "ready"}
        # Versendung/Veröffentlichung der Nachricht im jeweiligen Topic
        self.send_message("explorer/020", payload)

    def send_message_path(self, planetName, Xs, Ys, Ds, Xe, Ye, De, status):
    # Senden des aktuell durchfahrenen Weges

        # Nachricht
        payload = {"from": "client",
                   "type": "path",
                   "payload": {"startX": Xs, "startY": Ys, "startDirection": Ds, "endX": Xe, "endY": Ye, "endDirection": De, "pathStatus": status}}

        topic = f'planet/{planetName}/020'

        # Versendung/Veröffentlichung der Nachricht im jeweiligen Topic
        self.send_message(topic, payload)

    def send_message_pathSelect(self, planetName, Xs, Ys, Ds):
    # Übermittlung von Informationen über den vom Roboter gewählten Weg

        # Nachricht
        payload = {"from": "client",
                   "type": "pathSelect",
                   "payload": {"startX": Xs, "startY": Ys, "startDirection": Ds}}

        topic = f'planet/{planetName}/020'

        # Versendung/Veröffentlichung der Nachricht im jeweiligen Topic
        self.send_message(topic, payload)

    def send_message_targetReached(self, text):
    # Gesendet bei Entdeckung des Zielpunktes

        # Nachricht
        payload = {"from": "client",
                   "type": "targetReached",
                   "payload": {"message": text}}

        # Versendung/Veröffentlichung der Nachricht im jeweiligen Topic
        self.send_message("explorer/020", payload)

    def send_message_explorationCompleted(self, text):
    # Gesendet bei Entdeckung des Planeten

        # Nachricht
        payload = {"from": "client",
                   "type": "explorationCompleted",
                   "payload": {"message": text}}

        # Versendung/Veröffentlichung der Nachricht im jeweiligen Topic
        self.send_message("explorer/020", payload)


