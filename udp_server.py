import socket 
import random
import string

import time # Timer Package
import streamlit as st

# Utilities
from utils.error_handling import kill_with_error, throw_error


# ANSI escape codes for colored output
RED = "\033[0;31m"
ORANGE = "\033[0;202m"
GREEN = "\033[0;32m"
WHITE = "\033[0;37m"

BUFFER_SIZE = 1024  # Maximum UDP payload size (minus headers)
PACKET_SIZE = 65507
PACKET_DELIMETER = ';'

import argparse
def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--a', type=str, default="127.0.0.1",
        help="Determine's the IP address of the network for the server")
    parser.add_argument('--p', type=str, default="8080",
        help="Determine's the port the server will listen for new connections")
    
    parser.add_argument('--i', type=int, default=2,
        help="Time Interval to send requests")
    parser.add_argument('--s', type=bool, default=True,
        help="The program acts as a server")

    return parser.parse_args()

def calculate_OWD(time_sent, time_rec):
    return (time_rec - time_sent)/ (10 ** 6) # Milliseconds

def prepare_large_packet(time_sent, delimiter, packet_size):
    base_data = f"{time_sent}{delimiter}"
    extra_data_size = packet_size - len(base_data.encode())
    if extra_data_size > 0:
        extra_data = "X" * extra_data_size
        return bytes(base_data + extra_data, encoding='utf-8')
    else:
        return bytes(base_data[:packet_size], encoding='utf-8')



def handle_client_packet(server_sock, total_bytes, t_interval, prev_time):
    packets = server_sock.recvfrom(BUFFER_SIZE)
    time_rec = time.time_ns()

    elapsed_time = 0
    if not packets:
        print("No data received... Shutting down communication\n \
                Experiment Finished...")
        elapsed_time = (time_rec - int(data_msg)) / (10 ** 9)
        throughput = (total_bytes * 8) / elapsed_time
        throughput_Mbps = throughput /1e6
        print(f"Total Bytes Transferred: {total_bytes} bytes")
        print(f"Elapsed Time: {elapsed_time:.3f} seconds")
        print(f"Throughput: {throughput_Mbps:.3f} Mbps")
        return -1, time_rec
    
    data_msg = packets[0].decode()
    data_head = packets[1]

    packet_values = data_msg.split(PACKET_DELIMETER)
    time_sent = int(packet_values[0])
    server_sock.sendto(prepare_large_packet(time_rec, PACKET_DELIMETER, PACKET_SIZE), data_head)
    total_bytes += len(packets)
    
    time_sent = time.time_ns()
    delay = (time_rec - prev_time) / (10 ** 9)
    if delay >= t_interval:
        OWD_ms = calculate_OWD(time_rec, time_sent)
        print(f"Total Data Received (MB): {total_bytes / (1024 ** 2):.2f} - " \
              f"OWD (ms): {OWD_ms} - " \
              f"Elapsed Time: {elapsed_time}")
        
        prev_time = time_rec

    return 0, prev_time

def server_main(args):
    server_ip, port, t_interval, act_as_server = args.a, args.p, args.i, args.s

    try:
        server_port = int(port)
    except ValueError:
        kill_with_error("Invalid port number")

    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as err:
        kill_with_error("Failed to create a new Socket", err.errno)

    server_address = (server_ip, server_port)

    try:
        server_sock.bind(server_address)
    except socket.error as err:
        kill_with_error("Failed to bind server address", err.errno)

    print(f"Server binded to {server_ip}:{server_port}")

    total_bytes = 0
    while True:
        print("Server is listening...")

        start_time = time.time_ns() # High precision
        prev_time = time.time_ns()
        communication_log = {}
        while True:
            try:
                status, prev_time = handle_client_packet(server_sock, total_bytes, t_interval, prev_time)
                if status < 0:
                    break
                prev_time = prev_time
                # transf_time = float(data_msg)
                # total_bytes += len(data_rec)
                # # OWD_ms = calculate_OWD(transf_time, time_rec)
                # elapsed_time = (time_rec - start_time) / (10**9)
                # throughput = (total_bytes * 8) / elapsed_time
                # throughput_Mbps = throughput /1e6


            except socket.error as err:
                throw_error("Error during Communication", error_code=err.errno)


# if __name__ == "__main__":
#     server_main(get_args())