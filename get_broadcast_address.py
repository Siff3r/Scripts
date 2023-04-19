import ipaddress
import socket
import netifaces

def get_first_ipv4_interface():
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = ipaddress.IPv4Address(addr['addr'])
                if not ip.is_loopback:
                    return interface, addr['addr'], addr['netmask']
    raise Exception('No suitable network interface found.')

def get_broadcast_address(ip_address, netmask):
    network = ipaddress.IPv4Network(f"{ip_address}/{netmask}", strict=False)
    return network.broadcast_address

# Example usage
interface, ip_address, netmask = get_first_ipv4_interface()
broadcast_address = get_broadcast_address(ip_address, netmask)

print(f"Interface: {interface}")
print(f"IP Address: {ip_address}")
print(f"Netmask: {netmask}")
print(f"Broadcast Address: {broadcast_address}")

