import argparse
import socket
import time

parser = argparse.ArgumentParser(description="Reliable stop-and-wait UDP sender")
parser.add_argument("--count", type=int, default=30)
parser.add_argument("--timeout", type=float, default=0.5)
parser.add_argument("--max-retries", type=int, default=10)
args = parser.parse_args()

if args.count < 1 or args.timeout <= 0 or args.max_retries < 1:
    parser.error("count, timeout, and max-retries must be positive")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(args.timeout)
receiver = ("10.0.0.2", 5005)
retransmissions = 0
failed = []
start = time.time()

for seq in range(1, args.count + 1):
    message = f"DATA|{seq}|Packet {seq}".encode()
    acknowledged = False

    for attempt in range(args.max_retries):
        sock.sendto(message, receiver)
        try:
            while True:
                data, _ = sock.recvfrom(2048)
                if data.decode(errors="replace") == f"ACK|{seq}":
                    acknowledged = True
                    print(f"ACK received for packet {seq}")
                    break
            if acknowledged:
                break
        except socket.timeout:
            if attempt < args.max_retries - 1:
                retransmissions += 1
                print(f"Timeout: retransmitting packet {seq}")
    if not acknowledged:
        failed.append(seq)
        print(f"Packet {seq} failed after {args.max_retries} attempts")

sock.sendto(b"STOP", receiver)
elapsed = time.time() - start
print("\\n--- RESULTS ---")
print(f"Packets attempted: {args.count}")
print(f"Packets not acknowledged: {len(failed)}")
print(f"Retransmissions: {retransmissions}")
print(f"Elapsed time: {elapsed:.3f} seconds")
sock.close()
