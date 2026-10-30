import argparse
import random
import socket

parser = argparse.ArgumentParser(description="UDP receiver with test loss")
parser.add_argument("--loss", type=float, default=0.2,
                    help="Probability of deliberately dropping a first attempt (0.0-1.0)")
args = parser.parse_args()
if not 0.0 <= args.loss <= 1.0:
    parser.error("--loss must be between 0.0 and 1.0")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("10.0.0.2", 5005))
sock.settimeout(1.0)

received = set()
dropped = 0
print("Receiver listening on 10.0.0.2:5005", flush=True)

while True:
    try:
        data, address = sock.recvfrom(2048)
    except socket.timeout:
        continue

    message = data.decode(errors="replace")
    if message == "STOP":
        break

    if message.startswith("DATA|"):
        try:
            seq = int(message.split("|", 2)[1])
        except (ValueError, IndexError):
            continue

        # Simulate loss only for packets not yet accepted.
        if seq not in received and random.random() < args.loss:
            dropped += 1
            print(f"Simulated loss: packet {seq}", flush=True)
            continue

        received.add(seq)
        sock.sendto(f"ACK|{seq}".encode(), address)
        print(f"Received packet {seq}", flush=True)

print(f"Unique packets received: {len(received)}")
print(f"Simulated drops: {dropped}")
sock.close()
