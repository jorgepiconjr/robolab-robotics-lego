import ev3dev.core
import ev3dev.ev3 as ev3
from typing import Tuple, List

# Farbsensor
cs_sensor = ev3.ColorSensor()
cs_sensor.mode = 'RGB-RAW'
# Ultraschallsensor
us_sensor = ev3.UltrasonicSensor()
us_sensor.mode = 'US-DIST-CM'
# Soundausgabe
sound = ev3dev.core.Sound


class RobotInteraction:
    def __init__(self):
        # Grundsatzwerte, die bei der Kalibrierung überschrieben werden
        self.white = (104, 175, 111, 666)
        self.black = (17, 44, 19, 648)
        self.red = (71, 18, 14, 649)
        self.blue = (17, 66, 61, 652)
        self.color_range: int = 15  # die Toleranz für die Erkennung der Knoten: in +- 15 zu den Attributen sollen Knoten gefunden werden

# Methoden: Zusammenfassung Kalibrierung
    def new_calibration(self):
        self.calibrate_red()
        self.calibrate_blue()
        self.calibrate_white()
        self.calibrate_black()

    def calibrate_white(self) -> Tuple:
        input("set white: ")
        self.white = cs_sensor.bin_data("hhhh")
        print(self.white)
        return self.white

    def calibrate_black(self) -> Tuple:
        input("set black: ")
        self.black = cs_sensor.bin_data("hhhh")
        print(self.black)
        return self.black

    def calibrate_blue(self) -> Tuple:
        input("set blue: ")
        self.blue = cs_sensor.bin_data("hhhh")
        print(self.blue)
        return self.blue

    def calibrate_red(self) -> Tuple:
        input("set red: ")
        self.red = cs_sensor.bin_data("hhhh")
        print(self.red)
        return self.red

    # Knotenerkennung : hier werden alle Werte (rot, grün und blau) mit den in dem Attribut hinterlegtem Wert verglichen. Der Wert des Attributs bekommt dabei eine Toleranz von 15 in beide Richtungen
    def red_node(self) -> bool:
        control = cs_sensor.bin_data("hhhh")
        if (control[0] >= (self.red[0] - self.color_range) and control[0] <= (self.red[0] + self.color_range))\
            and (control[1] >= (self.red[1] - self.color_range) and control[1] <= (self.red[1] + self.color_range))\
                and (control[2] >= (self.red[2] - self.color_range) and control[2] <= (self.red[2] + self.color_range)):
            return True
        else:
            return False

    def blue_node(self) -> bool:
        control = cs_sensor.bin_data("hhhh")
        if (control[0] >= (self.blue[0] - self.color_range) and control[0] <= (self.blue[0] + self.color_range))\
            and (control[1] >= (self.blue[1] - self.color_range) and control[1] <= (self.blue[1] + self.color_range))\
                and (control[2] >= (self.blue[2] - self.color_range) and control[2] <= (self.blue[2] + self.color_range)):
            return True
        else:
            return False

    # Pfaderkennung: gibt True zurück wenn er einen Pfad entdeckt
    def find_path(self) -> bool:
        control = self.color()
        if control < 100:
            return True
        else:
            return False

# FARBE: lest das RGB Tupel ein, rechnet werte zusammen und dividiert durch 3 für Endwert
    def color(self) -> int:
        value: int = 0
        for color_value in range(3):
            value = value + cs_sensor.bin_data("hhhh")[color_value]
        return int(value/3)

# DISTANZ
    def measure_distance(self) -> int:
        return us_sensor.distance_centimeters

    def find_obstacle(self) -> bool:
        while self.measure_distance() < 18:
            return True
        return False

# SOUND
    # bei Hindernis
    def alarm_sound(self) -> None:
        # sound.beep(2) -> müssten auch wie comm_finished angepasst werden, aber brauchen wir nicht mehr
        sound.speak('You shall not pass!')

    # kurzes Beepen, wenn die Kommunikation an einem Knoten beendet ist
    def comm_finished(self) -> None:
        sound.beep(" -f 300.7 -r 2 -d 100 -l 400 ")

    # bei unvorhergesehenem Fehler
    def error_sound(self):
        # sound.beep(2) -> müssten auch wie comm_finished angepasst werden, aber brauchen wir nicht mehr
        sound.speak('Error!')

    # Melodie für Beginn und Ende der Planeterkundung
    def tour_sound(self):
        sound.play_song((
            ('D4', 'q'),
            ('E4', 'q'),
            ('F#4', 'q'),
            ('A4', 'q'),
            ('F#4', 'q'),
            ('E4', 'q'),
            ('D4', 'h'),
        ))
