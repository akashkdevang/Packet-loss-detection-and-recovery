from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from os_ken.ofproto import ofproto_v1_3


class PacketLossController(app_manager.OSKenApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datapaths = {}
        self.backup = False

    def add_flow(self, dp, priority, match, actions):
        parser = dp.ofproto_parser
        instructions = [parser.OFPInstructionActions(
            dp.ofproto.OFPIT_APPLY_ACTIONS, actions
        )]
        dp.send_msg(parser.OFPFlowMod(
            datapath=dp, priority=priority, match=match,
            instructions=instructions
        ))

    def install_routes(self, dp):
        p = dp.ofproto_parser
        if dp.id == 1:
            # h1 is on port 1; primary s2 on port 2; backup s3 on port 3.
            out_port = 3 if self.backup else 2
            self.add_flow(dp, 20, p.OFPMatch(
                eth_type=0x0800, ipv4_dst="10.0.0.2"
            ), [p.OFPActionOutput(out_port)])
            self.add_flow(dp, 20, p.OFPMatch(
                eth_type=0x0800, ipv4_dst="10.0.0.1"
            ), [p.OFPActionOutput(1)])

        elif dp.id == 2:
            # s2 port 1 leads to s1, port 2 to s3, port 3 to h2.
            out_port = 2 if self.backup else 1
            self.add_flow(dp, 20, p.OFPMatch(
                eth_type=0x0800, ipv4_dst="10.0.0.1"
            ), [p.OFPActionOutput(out_port)])
            self.add_flow(dp, 20, p.OFPMatch(
                eth_type=0x0800, ipv4_dst="10.0.0.2"
            ), [p.OFPActionOutput(3)])

        elif dp.id == 3:
            self.add_flow(dp, 20, p.OFPMatch(
                eth_type=0x0800, ipv4_dst="10.0.0.1"
            ), [p.OFPActionOutput(1)])
            self.add_flow(dp, 20, p.OFPMatch(
                eth_type=0x0800, ipv4_dst="10.0.0.2"
            ), [p.OFPActionOutput(2)])

        self.logger.info("Routes installed on switch %s; backup=%s",
                         dp.id, self.backup)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_ready(self, ev):
        dp = ev.msg.datapath
        self.datapaths[dp.id] = dp
        p = dp.ofproto_parser
        ofp = dp.ofproto

        # Flood ARP so hosts can resolve each other's MAC addresses.
        self.add_flow(dp, 10, p.OFPMatch(eth_type=0x0806),
                      [p.OFPActionOutput(ofp.OFPP_FLOOD)])

        # Send unmatched traffic to the controller.
        self.add_flow(dp, 0, p.OFPMatch(),
                      [p.OFPActionOutput(ofp.OFPP_CONTROLLER,
                                         ofp.OFPCML_NO_BUFFER)])
        self.install_routes(dp)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_changed(self, ev):
        msg = ev.msg
        dp = msg.datapath
        if dp.id not in (1, 2):
            return

        # Detect either end of the primary s1-s2 link.
        primary_port = 2 if dp.id == 1 else 1
        if msg.desc.port_no != primary_port:
            return

        down = bool(msg.desc.state & dp.ofproto.OFPPS_LINK_DOWN)
        if down != self.backup:
            self.backup = down
            self.logger.warning("Primary link state changed; backup=%s",
                                self.backup)
            for switch_dp in list(self.datapaths.values()):
                self.install_routes(switch_dp)
