import subprocess
import shlex
import logging
import time
import re
import argparse
import time

args = argparse.ArgumentParser(
    'wifi-autoconnect.py', 'python3 wifi-autoconnect.py <interface>')
args.add_argument('interface', type=str)


def check_ping():
    r = run_program("ping -c 1 google.com")
    if "bytes from" in r:
        return True
    return False


def check_iface_has_got_ip(iface):
    r = run_program(f"ip addr show {iface}").strip()
    if "inet " in r:
        return True
    return False


def request_dhcp(iface):
    run_program(f"dhclient {iface}")


def run_program(rcmd):
    """
    Runs a program, and it's paramters (e.g. rcmd="ls -lh /var/www")
    Returns output if successful, or None and logs error if not.
    """

    cmd = shlex.split(rcmd)
    executable = cmd[0]
    executable_options = cmd[1:]

    try:
        proc = subprocess.Popen(([executable] + executable_options),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        response = proc.communicate()
        response_stdout, response_stderr = response[0], response[1]
    except OSError as e:
        if e.errno == 'ENOENT':
            logging.debug(
                f"Unable to locate the '{executable}' program. Is it in your path?")
        else:
            logging.error(
                f"O/S error occured when trying to run '{executable}': \"{e}")
    except ValueError as e:
        logging.debug("Value error occured. Check your parameters.")
    else:
        if proc.wait() != 0:
            logging.debug("Executable '%s' returned with the error: \"%s\"" % (
                executable, response_stderr))
            return response
        else:
            logging.debug("Executable {executable} returned successfully")
            return response_stdout.decode('utf-8')


def get_networks(iface, retry=10):
    """
    Grab a list of wireless networks within range, and return a list of dicts describing them.
    """
    while retry > 0:
        if 'OK' in run_program(f"wpa_cli -i {iface} scan"):
            networks = []
            r = run_program(f"wpa_cli -i {iface} scan_result").strip()
            if "bssid" in r and len(r.split("\n")) > 1:
                for line in r.split("\n")[1:]:
                    b, fr, s, f = line.split()[:4]
                    ss = " ".join(line.split()[4:])  # Hmm, dirty
                    networks.append(
                        {"bssid": b, "freq": fr, "sig": s, "ssid": ss, "flag": f})
                return list(
                    filter(lambda x: re.search(r'\bESS\b', x['flag'], re.IGNORECASE) and not re.search(r'\b(PSK|WEP|WPA|WPA2|EAP|SAE)\b', x['flag'], re.IGNORECASE), networks))
        retry -= 1
        logging.debug("Couldn't retrieve networks, retrying")
        time.sleep(0.5)
    logging.error("Failed to list networks")


def connect_to_network(iface, network):
    net_id = run_program(f"wpa_cli -i {iface} add_network").strip('\n')
    # run_program(
    #     f'wpa_cli -i {iface} set_network {network} ssid \'"{network[ssid]}"\'')
    run_program('wpa_cli -i {} set_network {} ssid \'"{}"\''.format(iface,
                                                                    net_id, network['ssid']))
    run_program(f"wpa_cli -i {iface} set_network {net_id} scan_ssid 1")
    run_program(
        f"wpa_cli -i {iface} set_network {net_id} bssid {network['bssid']}")
    run_program(
        f"wpa_cli -i {iface} set_network {net_id} key_mgmt NONE")
    run_program(f"wpa_cli -i {iface} enable_network {net_id}")
    run_program(f"wpa_cli -i {iface} select_network {net_id}")


def disconnect_from_network(iface):
    if 'OK' in run_program(f"wpa_cli -i {iface} disconnect"):
        return True


def check_current_connection(iface):
    r = run_program(f"wpa_cli -i {iface} status").strip()
    # check wpa state
    if "wpa_state=COMPLETED" in r:
        return True
    return False


if __name__ == "__main__":
    args = args.parse_args()

    if check_ping():
        logging.debug("Connected to internet")
    else:
        networks = get_networks(args.interface)
        for network in networks:
            if int(network['sig']) <= -75:
                continue
            connect_to_network(args.interface, network)
            time.sleep(3)
            if check_current_connection(args.interface):
                logging.debug("Connected to network")
                request_dhcp(args.interface)
                if check_iface_has_got_ip(args.interface):
                    logging.debug("Got IP")
                    time.sleep(5)
                    if check_ping():
                        logging.debug("Connected to internet")
                        exit()
                    else:
                        logging.debug("Not connected to internet")
                        disconnect_from_network(args.interface)
                else:
                    logging.debug("Not got IP")
                    disconnect_from_network(args.interface)
            else:
                logging.debug("Not connected to network")
                disconnect_from_network(args.interface)
