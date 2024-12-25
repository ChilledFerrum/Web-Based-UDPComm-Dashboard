import socket 
import time # Timer Package
import streamlit as st

# Utilities
from utils.error_handling import kill_with_error, throw_error

BUFFER_SIZE = 2048
PACKET_DELIMETER = ';'

# ANSI escape codes for colored output
RED = "\033[0;31m"
ORANGE = "\033[0;202m"
GREEN = "\033[0;32m"
WHITE = "\033[0;37m"


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

def calculate_OWD(data_time, curr_time):
    return (curr_time - data_time)*1000


def main(args):
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

    # try:
    #     server_sock.listen(3)
    # except socket.error as err:
    #     kill_with_error("Error when listening", err.errno)

    print("Server Listening...")

    st.title("Real-Time Network Tracking Dashboard")
    owd_chart = st.line_chart([], use_container_width=True)
    throughput_chart = st.line_chart([], use_container_width=True)
    data_chart = st.line_chart([], use_container_width=True)

    while True:
        print("Waiting for a connection...")
        
        # try:
        #     client_sock, client_addr = server_sock.accept()
        #     print(f"{GREEN}Connected to {client_addr}{WHITE}")
        # except socket.error as err:
        #     throw_error("Failed to Accept Connection", err.errno)
        #     continue

        owd_data = []  # Store OWD values
        throughput_data = []  # Store throughput values
        total_mb_data = []  # Store total data in MB
        timestamps = []  # Store timestamps
        total_bytes = 0
        start_time = time.time_ns() # High precision
        packets_received = 1
        # communication_log = {"mean_OWD":}
        mean_OWD = 0.0
        prev_time = time.time_ns()
        while True:
            try:
                data = server_sock.recvfrom(BUFFER_SIZE)
                curr_time = time.time_ns()
                if not data:
                    print("No data received... Shutting down communication\n \
                          Experiment Finished...")
                    elapsed_time = (curr_time - start_time) / (10**9)
                    throughput = (total_bytes * 8) / elapsed_time
                    throughput_Mbps = throughput /1e6
                    print(f"Total Bytes Transferred: {total_bytes} bytes")
                    print(f"Elapsed Time: {elapsed_time:.3f} seconds")
                    print(f"Throughput: {throughput_Mbps:.3f} Mbps")
                    break
                packets = data[0].decode().split(PACKET_DELIMETER)
                for packet in packets:
                    if not packet:
                        continue # Skip empty packets
                    else:
                        transf_time = packet
                        transf_time = float(transf_time)
                        total_bytes += len(packet)
                OWD_ms = calculate_OWD(transf_time, curr_time / (10 ** 9))
                elapsed_time = (curr_time - start_time) / (10**9)
                throughput = (total_bytes * 8) / elapsed_time
                throughput_Mbps = throughput /1e6

                delay = (curr_time - prev_time) / (10 ** 9)
                if delay >= t_interval:
                    print(f"Received Data - OWD: {OWD_ms:.3f}ms - "
                            f"Throughput: {throughput_Mbps:.2f} Mbps - "
                            f"Data: {total_bytes / (1024 ** 2):.2f} MB - "
                            f"Elapsed Time: {elapsed_time}")

                    owd_data.append(OWD_ms)
                    throughput_data.append(throughput_Mbps)
                    total_mb_data.append(total_bytes / (1024 ** 2))

                    # Update Streamlit charts
                    owd_chart.line_chart({"OWD (ms)": owd_data[-50:]}, use_container_width=True)
                    throughput_chart.line_chart({"Throughput (Mbps)": throughput_data[-50:]},
                                                use_container_width=True)
                    data_chart.line_chart({"Data Transferred (MB)": total_mb_data[-50:]},
                                            use_container_width=True)

                    prev_time = curr_time

            except socket.error as err:
                throw_error("Error during Communication", error_code=err.errno)


if __name__ == "__main__":
    main(get_args())