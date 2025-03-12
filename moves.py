# import ev3dev.core
import ev3dev.core
import time
from robot_interaction import *
from odometry import *

# Motoren
motor_left = ev3.LargeMotor("outB")
motor_right = ev3.LargeMotor("outC")
# Ultraschallsensor
us_sensor = ev3.UltrasonicSensor()
us_sensor.mode = 'US-DIST-CM'
# Soundausgabe
sound = ev3dev.core.Sound


# Initialisieren der nötigen Klassen
currentColors:  RobotInteraction = RobotInteraction()
obstacle: RobotInteraction = RobotInteraction()


class Moves:
    def __init__(self):
        self.color_value = cs_sensor.value()
        self.odometry: Odometry = Odometry()
        self.x: int = 0
        self.y: int = 0
        self.alpha: int = 0
        # self.list_ticks_left: List = []  -> werden in der Odometrie initialisiert
        # self.list_ticks_right : List = [] -> werden in der Odometrie initialisiert

# LINE FOLLOWING
    def follow_line(self) -> bool: #tuple[List, List]:
        kp = 2.8  # Variablen für Fehlerberechnung
        ki = 0.1
        kd = 0.7
        offset = 55  # Durchschnittserrechnung von Anteilen an Schwarz und Weiß
        tp = 150  # Power der Motoren
        last_error = 0   # Fehleranpassung für PID-Regler
        derivative = 0
        integral = 0
        while True:
            color_value = cs_sensor.value()
            error = color_value - offset  # Fehlerberechnung: wie weit ist er vom optimalen Wert schwarz/weiß entfernt
            integral = error - last_error
            integral = (2 / 3) * integral + error
            derivative = error - last_error
            turn = kp * error + kd * derivative + ki * integral
            powerA = tp + turn  # Zuordnung der Geschwindigkeit: Target Power + Variablen
            powerB = tp - turn
            motor_left.speed_sp = powerA
            motor_right.speed_sp = powerB
            last_error = error   # Aktualisierung des Fehlers
            motor_left.command = motor_right.command = "run-forever"
            obstacle.measure_distance()  # Distanzmessen für Hinderniserkennung
            self.odometry.listl.append(motor_left.position)  # Füllen der Listen für Odometrie
            self.odometry.listr.append(motor_right.position)
            if currentColors.blue_node() or currentColors.red_node():  # Überprüft, ob er sich am Knoten befindet
                self.forward()
                self.stop()
                self.x, self.y, self.alpha = self.odometry.summe()  # Odometrieberechnung und Übergeben der Werte
                self.x = round(abs(self.x))  # abs, falls der Wert negativ ist und round für volle Integer
                self.y = round(abs(self.y))
                self.alpha = round(abs(self.alpha))
                self.odometry.list_leeren()  # Listen müssen nach berechnung geleert werden für nächsten Abschnitt
                return True
            elif obstacle.find_obstacle():  # Überprüft, ob ein Hindernis vorhanden ist
                motor_left.reset()
                motor_right.reset()
                # self.backward()  -> fährt sonst rückwärts
                self.stop()
                obstacle.alarm_sound()
                self.turn_obstacle()  # zum Knoten zurückkehren
                self.x, self.y, self.alpha = self.odometry.summe()  # Odometrieberechnung und Übergeben der Werte
                self.x = round(abs(self.x))  # abs, falls der Wert negativ ist und round für volle Integer
                self.y = round(abs(self.y))
                self.alpha = round(abs(self.alpha))
                self.odometry.list_leeren()  # Listen müssen nach berechnung geleert werden für nächsten Abschnitt
                return False

    def scan_node(self) -> List:
        # Idee: der Roboter soll sich zuerst etwa 45 Grad in die eine und dann 90 in die andere drehen, um einen etwaigen Raum nach einem vorhandenen Pfad abzuprüfen
        list_available_paths = [False, False, False, False]  # an [2] müsste standardmäßig True sein, da Herkunftspfad
        for i in range(4):
            # 45 Grad winkel zur einen Seite
            motor_left.speed_sp = -90
            motor_right.speed_sp = 90
            motor_right.command = motor_left.command = "run-forever"
            start_time = time.time()
            while (time.time() - start_time) < 0.5:
                control = cs_sensor.value()
                if control < 50:
                    list_available_paths[i] = True  # in der Liste soll er True ausgeben -> ein Pfad ist vorhanden
                    time.sleep(1.2)  # solange soll er nach keinen weiteren Pfaden suchen
                else:
                    pass
            self.stop()
            # 90 Grad zur anderen Seite: checken, ob in dem 45 Grad Umkreis ein Pfad ist
            motor_left.reset()
            motor_right.reset()
            motor_left.speed_sp = 90
            motor_right.speed_sp = -90
            motor_right.command = motor_left.command = "run-forever"
            start_time = time.time()  # notwendig, um die Zeit für die Ausführung zu messen
            while (time.time() - start_time) < 1.3:
                control = cs_sensor.value()
                if control < 50:
                    list_available_paths[i] = True  # in der Liste soll er True ausgeben -> ein Pfad ist vorhanden
                    time.sleep(1.3)  # solange soll er nach keinen weiteren Pfaden suchen
                else:
                    pass
            self.stop()
        # für neuen Pfad am Raster nochmal 45 Grad ausrichten und dann durch den Loop wiederholen, damit der Roboter zentriert ist
            motor_left.speed_sp = 90
            motor_right.speed_sp = -90
            motor_right.command = motor_left.command = "run-forever"
            time.sleep(0.8)  # für bessere Ausrichtung am Ende
        self.stop()
        # Roboter bleibt manchmal rechts von der Linie stehen und kann dann nicht mehr drehen: hierfür kleine Korrektur nach links, damit er trotzdem die wenigen Drehungen schafft
        motor_left.speed_sp = -90
        motor_right.speed_sp = 90
        motor_right.command = motor_left.command = "run-forever"
        time.sleep(0.2)
        self.stop()
        print(list_available_paths) # in der Steuerschleife geprinted
        return list_available_paths

    def forward(self) -> None:
        motor_left.reset()
        motor_right.reset()
        motor_left.speed_sp = motor_right.speed_sp = 130
        motor_left.command = motor_right.command = "run-forever"
        time.sleep(1)

    def backward(self) -> None:
        motor_left.reset()
        motor_right.reset()
        motor_left.speed_sp = motor_right.speed_sp = -130
        motor_left.command = motor_right.command = "run-forever"
        time.sleep(1)

    def stop(self) -> None:
        motor_left.stop()
        motor_right.stop()

    def turn_left(self) -> None:
        while True:
            find_line = currentColors.color()
            motor_left.speed_sp = -100
            motor_right.speed_sp = 100
            motor_right.command = motor_left.command = "run-forever"
            # stoppt, wenn er eine Linie erkennt und korrigiert, damit er auf der richtigen Seite der Linie ist
            if find_line < 100:
                motor_left.stop()
                motor_left.time_sp = motor_right.time_sp = 100
                motor_right.command = "run-timed"
                break

    def turn_right(self) -> None:
        while True:
            find_line = currentColors.color()
            motor_left.speed_sp = 100
            motor_right.speed_sp = -100
            motor_left.command = motor_right.command = "run-forever"
            # gleiche Korrektur wie links
            if find_line < 100:
                motor_left.run_timed()
                motor_right.run_timed()
                motor_left.time_sp = motor_right.time_sp = 150
                motor_left.speed_sp = -100
                motor_right.speed_sp = 100
                self.stop()
                break

    def turn_obstacle(self) -> None:
        motor_left.speed_sp = -100
        motor_right.speed_sp = 100
        motor_right.time_sp = motor_left.time_sp = 100
        motor_left.command = motor_right.command = "run-forever"
        self.turn_left()
        motor_left.speed_sp = -100
        motor_right.speed_sp = 100
        motor_right.time_sp = motor_left.time_sp = 100
        motor_left.command = motor_right.command = "run-timed"
        # Rückkehr zum Knoten
        self.follow_line()

    # die Graddrehungen werden aufgerufen, nachdem die Richtung des nächsten Weges bestimmt ist
    def turn90(self) -> None:
        motor_left.speed_sp = 90
        motor_right.speed_sp = -90
        motor_right.command = motor_left.command = "run-forever"
        time.sleep(1.4)

    def turn180(self) -> None:
        motor_left.speed_sp = 90
        motor_right.speed_sp = -90
        motor_right.command = motor_left.command = "run-forever"
        time.sleep(3.7)
        self.turn_right()

    def turn270(self) -> None:
        motor_left.speed_sp = 90
        motor_right.speed_sp = -90
        motor_right.command = motor_left.command = "run-forever"
        time.sleep(5.3)

    def turn360(self) -> None:
        motor_left.speed_sp = 90
        motor_right.speed_sp = -90
        motor_right.command = motor_left.command = "run-forever"
        time.sleep(7.9)
        self.turn_right()
