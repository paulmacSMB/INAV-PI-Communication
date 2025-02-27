import serial
import time
import binascii

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
    print("data in parse method:", data)
    while index < len(data):
        if data[index:index+3] != b'$M>':  # Look for MSP response header
            index += 1
            continue

        if index + 5 > len(data):  # Ensure we have enough bytes for header + size + command
            print("❌ Incomplete MSP response (missing header or command ID). Skipping...")
            break

        size = data[index+3]  # Payload size

        if index + 5 + size >= len(data):  # Check if payload + checksum fits in data
            print(f"❌ Incomplete MSP response (expected {size} bytes, but data is too short). Skipping...")
            break
        command = data[index+4]  # MSP command ID
        payload = data[index+5:index+5+size]  # Extract payload
        checksum = data[index+5+size]  # Extract checksum
        index += 5 + size  # Move to the next MSP response

        print(f"✅ MSP Response Found!")
        print(f"Command: {command} (0x{command:02X})")
        print(f"Payload Size: {size}")
        print(f"Payload: {payload.hex()}")
        print(f"Checksum: {checksum}")
        print("-" * 40)

# Open Serial Port
ser = serial.Serial('/dev/ttyAMA0', 57600, timeout=1)
time.sleep(2)

# HC-SR04 Distance in mm (Example: 100cm = 1000mm)
distance_mm = 1000  # Adjust based on actual sensor reading
payload = distance_mm.to_bytes(4, 'little', signed=True)

# Send MSP_ALTITUDE command with HC-SR04 distance data
packet = msp_packet(0x38, payload)
ser.write(packet)

# Read response from FC
response = ser.read(32)
print("Received:", response.hex())
parse_msp_response(response.hex())

