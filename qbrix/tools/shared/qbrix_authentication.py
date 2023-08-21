import hmac
import hashlib
import base64
import struct
import time

def generate_mfa_code(secret):
    # Convert the secret from base32 to bytes
    secret_bytes = base32_to_bytes(secret)

    # Calculate the number of 30-second periods since the epoch
    timestamp = int(time.time() / 30)
    timestamp_bytes = struct.pack(">Q", timestamp)

    # Compute HMAC-SHA1 of the timestamp using the secret as key
    hmac_result = hmac.new(secret_bytes, timestamp_bytes, hashlib.sha1).digest()

    # Extract a 4-byte dynamic binary code from the HMAC result
    offset = hmac_result[-1] & 0x0F
    dbc = struct.unpack(">L", hmac_result[offset:offset+4])[0] & 0x7FFFFFFF

    # Convert the dynamic binary code to a 6-digit number
    mfa_code = dbc % 1000000

    return "{:06d}".format(mfa_code)

def base32_to_bytes(base32_string):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
    padding = len(base32_string) % 8
    base32_string = base32_string + '=' * padding  # Add padding
    result = []

    for i in range(0, len(base32_string), 8):
        chunk = base32_string[i:i+8]
        acc = 0
        for j, char in enumerate(chunk):
            acc = acc | (alphabet.index(char.upper()) << (35 - 5*j))

        result.extend(struct.pack(">Q", acc)[(8 - (5 * len(chunk) + 3) // 8):])

    return bytes(result)

print("Running")
print(generate_mfa_code('2STM5SBBJ5GVM4IQUMKWOXWNF2AK57YU'))
