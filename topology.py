from mininet.topo import Topo

class PacketLossTopo(Topo):
    def build(self):
        h1 = self.addHost("h1", ip="10.0.0.1/24")
        h2 = self.addHost("h2", ip="10.0.0.2/24")

        s1 = self.addSwitch("s1", dpid="0000000000000001")
        s2 = self.addSwitch("s2", dpid="0000000000000002")
        s3 = self.addSwitch("s3", dpid="0000000000000003")

        self.addLink(h1, s1)       # s1 port 1
        self.addLink(s1, s2)       # s1 port 2, s2 port 1 (primary)
        self.addLink(s1, s3)       # s1 port 3, s3 port 1 (backup)
        self.addLink(s3, s2)       # s3 port 2, s2 port 2 (backup)
        self.addLink(s2, h2)       # s2 port 3

topos = {"packetloss": PacketLossTopo}
