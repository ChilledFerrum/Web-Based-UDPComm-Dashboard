import socket
import time # Timer package
from utils import progress_bar as pb
from utils.error_handling import kill_with_error, throw_error 


GREEN = "\033[0;32m"
WHITE = "\033[0;37m"

PACKET_DELIMETER = ';'


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

def main(args):
    server_ip, port, = args.a, args.p
    t_interval, act_as_client, experiment_duration  = args.i, args.c, args.t
    udp_pkg_size = args.l

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

    packets_sent = 1
    pb.setMaxLimit(experiment_duration * 10, set_msg="Experiment Progress")
    start_time = time.time()

    prev_time = start_time
    while True:
        try:
            time_curr = time.time()
            
            input_s = str(time.time_ns() / (10 ** 9)) + PACKET_DELIMETER
            
            client_sock.sendto(bytes(input_s, encoding='utf-8'), 
                            (str(server_ip), int(server_port)))
            packets_sent += 1
            delay = time_curr - prev_time
            if delay >= t_interval:
                pb.progressBar(int((time_curr - start_time) * 10))
                prev_time = time.time()
            
            if time_curr - start_time > experiment_duration:
                print("Experiment Finished...")
                print(f"Total Packets Sent: {packets_sent}")
                client_sock.close()
                break
            
            
        except socket.error as err:
            throw_error("Error during Communication", err.errno)
            client_sock.close()
            break


if __name__ == "__main__":
    main(get_args())

