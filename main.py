import logging
from sensors.sensor_manager import SensorManager

def main():
    sensor_manager = SensorManager()
    
    try:
        sensor_manager.connect_to_server()
        sensor_manager.run()
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        sensor_manager.stop()
    except Exception as e:
        logging.error(f"Error: {e}")
        sensor_manager.stop()

if __name__ == "__main__":
    main()