# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2024 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Radar Calculations
# Description: Berechnungslogik für Radar-Sensoren
# -----------------------------------------------------------------------------

class RadarCalculations:
    def __init__(self, config):
        """
        Initialisiert die Berechnungsklasse mit der Sensor-Konfiguration
        
        Args:
            config (dict): Container-Konfiguration aus der sensors.json
        """
        self.config = config

    def calculate_water_level(self, measured_air_distance):
        """Berechnet den aktuellen Wasserstand in mm."""
        return self.config['air_distance_max_level_mm'] - measured_air_distance

    def calculate_volume(self, actual_water_level):
        """Berechnet das aktuelle Wasservolumen in m³."""
        return (self.config['width_mm'] * 
                self.config['length_mm'] * 
                actual_water_level) / 1_000_000_000

    def calculate_volume_percentage(self, actual_volume):
        """Berechnet den Füllstand in Prozent."""
        return (actual_volume / self.config['max_volume_m3']) * 100

    def check_water_level_alarm(self, actual_water_level):
        """Überprüft ob der Wasserstand den Grenzwert überschreitet."""
        return actual_water_level > self.config['max_water_level_mm']

    def calculate_level_above_normal(self, actual_water_level):
        """Berechnet die Abweichung vom normalen Wasserstand in mm."""
        return actual_water_level - self.config['normal_water_level_mm'] 