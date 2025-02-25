import RPi.GPIO as GPIO
import time
import serial

# Flight Controller Serial Connection (Modify Port if Needed)
FC_PORT = "/dev/ttyAMA0"
FC_BAUD = 57600

ser = serial.Serial(FC_PORT, FC_BAUD, timeout=1)

# GPIO Setup for Ultrasonic Sensor
TRIG = 23
ECHO = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Function to get distance from ultrasonic sensor
def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO) == 0:
        start_time = time.time()

    while GPIO.input(ECHO) == 1:
        stop_time = time.time()

    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2  # cm
    return round(distance, 2)

def send_msp_command(command, payload=b''):
    header = b'$M<'
    size = len(payload).to_bytes(1, 'little')
    cmd = command.to_bytes(1, 'little')
    checksum = int.from_bytes(size, 'little') ^ int.from_bytes(cmd, 'little')

    for byte in payload:
        checksum ^= byte

    packet = header + size + cmd + payload + checksum.to_bytes(1, 'little')
    ser.write(packet)

# Main Loop for Obstacle Avoidance
try:
    while True:
        distance = get_distance()
        print(f"Distance: {distance} cm")

        if distance < 70:  #  70cm
            print("🚨 Obstacle detected! Sending avoidance command.")
            send_msp_command(0x38, b'\x00\x00\x00\x00')  # Modify payload based on FC needs

        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
    ser.close()
