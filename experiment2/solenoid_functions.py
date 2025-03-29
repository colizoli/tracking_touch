"""
Solenoid functions
Python 3.9

H. Elmas & O.Colizoli 2025
"""

def define_serial_port():
    # Set up port
    serial_port = serial.Serial("COM3", 115200, timeout=10)
    time.sleep(5)
    return serial_port

def send_solnenoid_pulses(solenoid_id, serial_port, n_pulses=3, rise_time=0.1):
    """
    Activates a solenoid connected to a serial port, a number of pulses.
 
    Parameters:
    solenoid_id (int): The ID of the solenoid to activate.
    serial_port (Serial): The serial port object to communicate with. Default is 3 seconds.
    rise_time (float, optional): The time in seconds for the solenoid to rise. Default is 0.1 seconds.
    """
    currBits = 2**solenoid_id
    for _ in range(n_pulses):
        serial_port.write(serial.to_bytes([currBits]))
        core.wait(rise_time)
 
    serial_port.write(serial.to_bytes([0]))

#
# def activate_solnenoid_n_pulses(solenoid_id, serial_port, n_pulses, rise_time=0.1):
#     """
#     Activates a solenoid connected to a serial port, a number of pulses.
#
#     Parameters:
#     solenoid_id (int): The ID of the solenoid to activate.
#     serial_port (Serial): The serial port object to communicate with.
#     rise_time (float, optional): The time in seconds for the solenoid to rise. Default is 0.1 seconds.
#     """
#     currBits = 2**solenoid_id
#     for _ in range(n_pulses):
#         serial_port.write(serial.to_bytes([currBits]))
#         core.wait(rise_time)
#
#     serial_port.write(serial.to_bytes([0]))
#
# # I used it like,here the solenoid id is just the number indicating which slot it is connected to in the box
#
# def solenoid_test():
#
#     # Set up port
#     serial_port = serial.Serial("COM3", 115200, timeout=10)
#     time.sleep(5)
#
#     finger_to_sol_id = {"ring": 3, "middle": 2, "index": 1}
#     fingers = list(finger_to_sol_id.keys())
#     trials_per_solenoid = 3
#     trial_sequence = np.tile(fingers, trials_per_solenoid)
#
#     logging.debug(trial_sequence)
#     for finger in trial_sequence:
#         print(f"Activating Solenoid {finger}")
#         activate_solnenoid_n_pulses(
#             finger_to_sol_id[finger], serial_port, n_pulses=3
#         )
#         core.wait(2)
#
#     serial_port.write(serial.to_bytes([0]))
