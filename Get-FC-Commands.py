import binascii
import serial
import time

# MSP Command Dictionary
MSP_COMMANDS = {
    0x00: "MSP_NULL",
    0x01: "MSP_API_VERSION",
    0x02: "MSP_FC_VARIANT",
    0x03: "MSP_FC_VERSION",
    0x04: "MSP_BOARD_INFO",
    0x05: "MSP_BUILD_INFO",
    0x10: "MSP_FEATURE",
    0x11: "MSP_BOARD_ALIGNMENT_CONFIG",
    0x12: "MSP_CURRENT_METER_CONFIG",
    0x13: "MSP_MIXER_CONFIG",
    0x14: "MSP_RX_CONFIG",
    0x1A: "MSP_PID",
    0x1B: "MSP_PIDNAMES",
    0x1C: "MSP_SET_PID",
    0x30: "MSP_STATUS",
    0x31: "MSP_RAW_IMU",
    0x32: "MSP_SERVO",
    0x33: "MSP_MOTOR",
    0x34: "MSP_RC",
    0x35: "MSP_RAW_GPS",
    0x36: "MSP_COMP_GPS",
    0x37: "MSP_ATTITUDE",
    0x38: "MSP_ALTITUDE",
    0x39: "MSP_ANALOG",
    0x3A: "MSP_RC_TUNING",
    0x64: "MSP_ACC_TRIM",
    0x65: "MSP_SET_ACC_TRIM",
    0xA0: "MSP_OSD_CONFIG",
    0xA1: "MSP_SET_OSD_CONFIG",
    0xB0: "MSP_VTX_CONFIG",
    0xB1: "MSP_SET_VTX_CONFIG",
}

# Function to create MSP packet
def msp_packet(command, payload=b''):
    header = b'$M<'
    size = len(payload).to_bytes(1, 'little')
    cmd = command.to_bytes(1, 'little')
    checksum = int.from_bytes(size, 'little') ^ int.from_bytes(cmd, 'little')
    for byte in payload:
        checksum ^= byte
    return header + size + cmd + payload + checksum.to_bytes(1, 'little')

# Function to parse MSP response
def parse_msp_response(data_hex):
    data = binascii.unhexlify(data_hex)  # Convert hex string to bytes
    index = 0

    while index < len(data):
        if data[index:index+3] != b'$M>':  # Look for MSP response header
            index += 1
            continue

        size = data[index+3]  # Payload size
        command = data[index+4]  # MSP command ID
        payload = data[index+5:index+5+size]  # Extract payload
        checksum = data[index+5+size]  # Extract checksum
        index += 5 + size  # Move to the next MSP response

        print(f"✅ MSP Response Found!")
        print(f"Command: {command} (0x{command:02X}) - {MSP_COMMANDS.get(command, 'Unknown Command')}")
        print(f"Payload Size: {size}")
        print(f"Payload: {payload.hex()}")
        print(f"Checksum: {checksum}")
        print("-" * 40)

# Expose Port
ser = serial.Serial('/dev/ttyAMA0', 57600, timeout=1)
time.sleep(2)

# Send commands
for key in MSP_COMMANDS:
    packet = msp_packet(key)  # FC commands
    ser.write(packet)
    response = ser.read(64)  
    print("Received:", response.hex()) 
    parse_msp_response(response.hex())  
