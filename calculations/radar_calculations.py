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
            
        air_distance_max_level_mm: Abstand bei leerem Becken (Montageposition bis Beckenboden)
        max_water_level_mm: Maximaler sicherer Wasserstand (Alarm-Grenze)
        normal_water_level_mm: Normaler Betriebswasserstand
        """
        self.config = config

    def calculate_water_level(self, measured_air_distance):
        """
        Berechnet den aktuellen Wasserstand in mm.
        
        Der Sensor misst von seiner Montageposition:
        - Großer Luftabstand = niedriger Wasserstand
        - Kleiner Luftabstand = hoher Wasserstand
        
        measured_air_distance enthält bereits den Montage-Offset
        """
        return max(0, self.config['air_distance_max_level_mm'] - measured_air_distance)

    def calculate_volume(self, actual_water_level):
        """
        Berechnet das aktuelle Wasservolumen in m³.
        Volumen = Grundfläche × Höhe / 1.000.000.000 (mm³ → m³)
        
        Erlaubt auch Volumina über dem normalen Maximum für Überlaufbereich.
        """
        return max(0, (self.config['width_mm'] * 
                      self.config['length_mm'] * 
                      actual_water_level) / 1_000_000_000)

    def calculate_volume_percentage(self, actual_volume):
        """
        Berechnet den Füllstand in Prozent.
        Kann über 100% gehen für den Überlaufbereich.
        Verhindert nur negative Prozente.
        """
        return max(0, (actual_volume / self.config['max_volume_m3']) * 100)

    def check_water_level_alarm(self, actual_water_level):
        """
        Überprüft ob der Wasserstand den maximalen sicheren Wasserstand überschreitet.
        
        Der Alarm basiert auf dem absoluten Wasserstand (max_water_level_mm),
        nicht auf dem prozentualen Füllstand, da der Überlaufbereich 
        berücksichtigt werden muss.
        """
        return actual_water_level > self.config['max_water_level_mm']

    def calculate_level_above_normal(self, actual_water_level):
        """
        Berechnet die Abweichung vom normalen Wasserstand in mm.
        Positive Werte bedeuten höheren Wasserstand als normal.
        Negative Werte bedeuten niedrigeren Wasserstand als normal.
        """
        return actual_water_level - self.config['normal_water_level_mm'] 