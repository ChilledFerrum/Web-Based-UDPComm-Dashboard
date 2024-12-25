import socket
import time # Timer package
import numpy as np

from utils import progress_bar as pb
from utils.error_handling import kill_with_error, throw_error 


GREEN = "\033[0;32m"
WHITE = "\033[0;37m"

BUFFER_SIZE = 1024  # Maximum UDP payload size (minus headers)
PACKET_SIZE = 65507

PACKET_DELIMETER = ';'
total_bytes = 0
packets_sent = 1
owds_c2s = []
owds_s2c = []
results_log = {"Throughput": [],
               "Jitter Client": [],
               "Jitter Server": [],
               "Tail Latency Client": [],
               "Tail Latency Server": [],
               "OWD Client": [],
               "OWD Server": [],
               "Time": []}

import argparse
def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--a', type=str, default="127.0.0.1",
        help="Determine's the IP address of the network for the server")
    parser.add_argument('--p', type=str, default="8080", 
        help="Determine's the port the server will listen for new connections")
    
    parser.add_argument('--i', type=float, default=1,
        help="Time Interval to send requests")
    parser.add_argument('--c', type=bool, default=True,
        help="The program acts as a client")
    
    parser.add_argument('--l', type=int,
        help="UDP Package Size in bytes")
    parser.add_argument('--t', type=int, default=10,
        help="Experiment duration in seconds...")

    return parser.parse_args()

def prepare_large_packet(time_sent, delimiter, packet_size):
    base_data = f"{time_sent}{delimiter}"
    extra_data_size = packet_size - len(base_data.encode())
    if extra_data_size > 0:
        extra_data = "X" * extra_data_size
        return bytes(base_data + extra_data, encoding='utf-8')
    else:
        return bytes(base_data[:packet_size], encoding='utf-8')

def calculate_jitter(delays):
    jitter_values = [abs(delays[i] - delays[i - 1]) for i in range(1, len(delays))]
    avg_jitter = sum(jitter_values) / len(jitter_values) if jitter_values else 0.0
    return avg_jitter

def calculate_OWD(time_sent, time_rec):
    return (time_rec - time_sent)/ (10 ** 6) # Milliseconds


def calculate_tail_latency(delays, percentile=95):
    if not delays:
        return 0.0
    return np.percentile(delays, percentile)


def handle_server_packet(socket, t_interval, prev_time, start_time):
    global total_bytes, packets_sent, owds

    time_sent2serv = time.time_ns()
    sent_packet = prepare_large_packet(time_sent2serv, PACKET_DELIMETER, PACKET_SIZE)
    socket.send(sent_packet)
    elapsed_time = 0
    packets, _ = socket.recvfrom(1024)
    time_rec = time.time_ns()
    if not packets:
        print("No data received... Shutting down communication\n \
                Experiment Finished...")
        return -1, 0
    
    data = packets.decode()
    time_sent_serv = int(data.split(PACKET_DELIMETER)[0])
    
    total_bytes += len(sent_packet)
    
    elapsed_time = (time_rec - start_time) / (10 ** 9)
    throughput_MBps = (total_bytes / (1024 ** 2)) / elapsed_time
    
    delay = (time_rec - prev_time) / (10 ** 9)
    if delay >= t_interval:
        # One way Delay Server & Client
        OWD_ms_client2server = calculate_OWD(time_sent2serv, time_sent_serv)
        OWD_ms_server2client = calculate_OWD(time_sent_serv, time_rec)
        
        # Used to calculate Jitter
        owds_c2s.append(OWD_ms_client2server)
        owds_s2c.append(OWD_ms_server2client)
        
        # Jitter Calculation for Server & Client
        Jitter_ms_client2server = calculate_jitter(owds_c2s)
        Jitter_ms_server2client = calculate_jitter(owds_s2c)

        # Tail Latency of the 95th percentile for Server & Client
        tail_latency_client = calculate_tail_latency(owds_c2s, percentile=95)
        tail_latency_server = calculate_tail_latency(owds_s2c, percentile=95)

        print(f"Total Packets Sent: {GREEN}{packets_sent}{WHITE}\n" \
              f"Total Data Received: {GREEN}{total_bytes / (1024 ** 2):.2f} {WHITE}MegaBytes\n" \
              f"OWD Client2Server: OWD={GREEN}{OWD_ms_client2server:.3f} {WHITE}ms | Jitter={GREEN}{Jitter_ms_client2server:.3f}{WHITE}\n" \
              f"OWD Server2Client: OWD={GREEN}{OWD_ms_server2client:.3f} {WHITE}ms | Jitter={GREEN}{Jitter_ms_server2client:.3f}{WHITE}\n" \
              f"Throughput: {GREEN}{throughput_MBps:.3f} {WHITE}MBps \n" \
              f"Elapsed Time: {GREEN}{elapsed_time:.3f} {WHITE}Seconds\n")

        results_log['OWD Server'].append(OWD_ms_client2server)
        results_log['OWD Client'].append(OWD_ms_server2client)
        results_log['Throughput'].append(throughput_MBps)
        results_log["Jitter Client"].append(Jitter_ms_client2server)
        results_log["Jitter Server"].append(Jitter_ms_server2client)
        results_log["Tail Latency Client"].append(tail_latency_client)
        results_log["Tail Latency Server"].append(tail_latency_server)
        results_log['Time'].append(elapsed_time)
        prev_time = time_sent_serv

    return total_bytes, prev_time
def client_main(args):
    server_ip, port, = args.a, args.p
    t_interval, act_as_client, experiment_duration  = args.i, args.c, args.t
    udp_pkg_size = args.l
    global packets_sent

    try:
        server_port = int(port)
    except ValueError:
        kill_with_error("Invalid port number")

    try:
        # Create a socket
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as err:
        kill_with_error("Error when creating a new Socket", err.errno)

    try:
        # Connect to the server
        print(f"Connecting to {server_ip}:{server_port}...")
        client_sock.connect((server_ip, server_port))
        print(f"{GREEN}Connected...{WHITE}")
    except socket.error as err:
        kill_with_error("Connection Failed", err.errno)

    pb.setMaxLimit(experiment_duration * 10, set_msg="Experiment Progress")
    start_time = time.time_ns()
    prev_time = time.time_ns()
    
    while (time.time_ns() - start_time)/(10**9) < experiment_duration:
        try:
            # time_curr = time.time_ns()
            status, prev_time = handle_server_packet(client_sock, 
                                                     t_interval, 
                                                     prev_time, start_time)
            packets_sent += 1
            if status < 0:
                print("No packets found")
                break
            
        except socket.error as err:
            throw_error("Error during Communication", err.errno)
            client_sock.close()
            break



if __name__ == "__main__":
    client_main(get_args())