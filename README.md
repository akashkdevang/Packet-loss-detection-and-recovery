
# Packet Loss Detection and Recovery Using SDN

## 1. Project Overview
This project implements a packet loss detection and recovery system using Software Defined Networking (SDN), UDP socket programming, and Mininet.

The system detects simulated packet loss and uses acknowledgements and retransmissions to ensure reliable packet delivery. It also demonstrates automatic path recovery when the primary network link fails.

## 2. Objectives
- Detect packet loss during UDP communication.
- Implement packet acknowledgement and retransmission.
- Create an SDN-controlled network using Mininet.
- Demonstrate backup path recovery during link failure.
- Evaluate performance under different packet loss conditions.

## 3. Technologies Used
- Ubuntu 20.04
- Python 3
- Mininet
- Open vSwitch
- OS-Ken SDN Controller
- UDP Socket Programming
- OpenFlow 1.3

## 4. Network Architecture
The network contains two end hosts (h1 and h2) connected through SDN switches.

A backup path is provided through a third switch to maintain communication when the primary link fails.

## 5. Project Files
| File | Description |
|---|---|
| topology.py | Creates the Mininet network topology |
| sdn_controller.py | Controls routing and backup path recovery |
| udp_sender.py | Sends UDP packets and handles acknowledgements |
| udp_receiver.py | Receives packets and simulates packet loss |

## 6. Performance Testing
The system was tested using 50 packets under different simulated packet loss conditions.

| Packet Loss | Retransmissions | Delivery Rate |
|---|---:|---:|
| 0% | 0 | 100% |
| 20% | 13 | 100% |
| 40% | 27 | 100% |

All 50 unique packets were successfully delivered in the recorded tests.

## 7. SDN Recovery Testing
The primary link was intentionally disconnected to test the backup route. The SDN controller detected the link failure and installed forwarding rules through the backup path.

Communication was restored successfully without packet loss in the ping test.

## 8. How to Run

### Start the SDN Controller
```bash
sudo osken-manager sdn_controller.py --ofp-tcp-listen-port 6633
```

### Start Mininet
```bash
sudo mn --custom topology.py --topo packetloss --controller remote,ip=127.0.0.1,port=6633 --switch ovsk,protocols=OpenFlow13
```

### Start UDP Receiver
```bash
h2 python3 /home/mininet/packet-loss-project/udp_receiver.py --loss 0.2
```

### Run UDP Sender
```bash
h1 python3 /home/mininet/packet-loss-project/udp_sender.py --count 50 --timeout 0.5
```

## 9. Conclusion
The project demonstrates packet loss detection, retransmission-based recovery, and SDN-based backup path switching. The experimental results show that reliable packet delivery can be maintained under simulated packet loss conditions.

## 10. Authors
Developed as an academic mini project.
