import os
import matplotlib.pyplot as plt
import streamlit as st
from utils.class_args import args_client, args_server
import threading
import time
import udp_server
import udp_client


class DashboardController:
    def __init__(self):
        st.set_page_config(page_title="UDP Dashboard Controller", layout="wide")
        self.results_log = {
            "Throughput": [],
            "Jitter Client": [],
            "Jitter Server": [],
            "Tail Latency Client": [],
            "Tail Latency Server": [],
            "OWD Client": [],
            "OWD Server": [],
            "Time": []
        }

        self.results.log = {
            "Throughput": [],
            "Jitter Client": [],
            "Jitter Server": [],
            "Tail Latency Client": [],
            "Tail Latency Server": [],
            "OWD Client": [],
            "OWD Server": [],
            "Time": []
        }

        self.server_ip = None
        self.server_port = None
        self.client_ip = None
        self.client_port = None
        self.packet_size_client = None
        self.experiment_duration = None
        self.experiment_interval_client = None
        self.run_experiment = False

        self.init_page()
        self.chart_placeholders = self.create_chart_placeholders()

    def init_page(self):
        st.title("🌐 UDP Dashboard Controller")
        st.write("Monitor and control UDP-based experiments in real time.")
        
        col1, col2 = st.columns(2)

        with col1:
            st.header("Controls 🔧")
            st.markdown("#### Network Parameters")
            self.server_ip = st.text_input("Server IP", "127.0.0.1")
            self.server_port = st.text_input("Server Port", "8080")
            self.client_ip = st.text_input("Client IP", "127.0.0.1")
            self.client_port = st.text_input("Client Port", "8080")
            self.packet_size_client = st.slider("Client Packet Size (Bytes)", 1024, 65507, 1024)
            self.experiment_duration = st.slider("Experiment Duration (s)", 5, 120, 10)
            self.experiment_interval_client = st.slider("Client Update Interval (s)", 1, 10, 1)

            self.run_experiment = st.button("Run Experiment 🔷")

        with col2:
            st.header("Live Metrics 📈")
            self.col2 = col2  # Save reference to col2 for charts

    def create_chart_placeholders(self):
        """Create chart placeholders in col2."""
        with self.col2:
            throughput_chart = st.empty()
            jitter_chart = st.empty()
            owd_chart = st.empty()
            tail_latency_chart = st.empty()
        return {
            "Throughput": throughput_chart,
            "Jitter": jitter_chart,
            "OWD": owd_chart,
            "Tail Latency": tail_latency_chart,
        }

    def start_experiment(self):
        """Run the experiment, update charts, and reset results after completion."""
        self.reset_log_results()

        # Start server and client threads
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        client_thread = threading.Thread(target=self.start_client, daemon=True)
        server_thread.start()
        time.sleep(1)  # Allow server to initialize
        client_thread.start()

        # Update charts dynamically during the experiment
        for _ in range(self.experiment_duration):
            self.update_charts()
            time.sleep(1)

        # Save charts to figures folder before resetting
        self.save_charts()

        # Reset for the next experiment
        self.reset_log_results()

    def save_charts(self):
        """Save the charts as .jpg files with X/Y labels, legends, and custom colors."""
        os.makedirs("figures", exist_ok=True)
        time_axis = self.results.log["Time"]

        def plot_and_save_chart(data, labels, filename, xlabel, ylabel, title):
            plt.figure(figsize=(10, 6))
            for series, label, color in zip(data, labels, ["lightblue", "lightcoral"]):
                plt.plot(time_axis, series, label=label, color=color)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.legend()
            plt.title(title)
            plt.grid(alpha=0.5)
            plt.tight_layout()
            plt.savefig(f"figures/{filename}.jpg", format="jpg", dpi=300)
            plt.close()

        # Throughput chart
        if self.results.log["Throughput"]:
            plot_and_save_chart(
                [self.results.log["Throughput"]],
                ["Throughput (Mbps)"],
                "throughput_chart",
                "Time (s)",
                "Throughput (Mbps)",
                "Throughput Over Time"
            )

        # Jitter chart
        if self.results.log["Jitter Client"] and self.results.log["Jitter Server"]:
            plot_and_save_chart(
                [self.results.log["Jitter Client"], self.results.log["Jitter Server"]],
                ["Jitter Client (ms)", "Jitter Server (ms)"],
                "jitter_chart",
                "Time (s)",
                "Jitter (ms)",
                "Jitter Over Time"
            )

        # OWD chart
        if self.results.log["OWD Client"] and self.results.log["OWD Server"]:
            plot_and_save_chart(
                [self.results.log["OWD Client"], self.results.log["OWD Server"]],
                ["OWD Client (ms)", "OWD Server (ms)"],
                "owd_chart",
                "Time (s)",
                "OWD (ms)",
                "One-Way Delay Over Time"
            )

        # Tail Latency chart
        if self.results.log["Tail Latency Client"] and self.results.log["Tail Latency Server"]:
            plot_and_save_chart(
                [self.results.log["Tail Latency Client"], self.results.log["Tail Latency Server"]],
                ["Tail Latency Client (ms)", "Tail Latency Server (ms)"],
                "tail_latency_chart",
                "Time (s)",
                "Tail Latency (ms)",
                "Tail Latency Over Time"
            )

    def update_charts(self):
        """Update charts with the latest data."""
        results = udp_client.results_log

        if results["Time"]:
            time_axis = results["Time"]

            # Update persistent log
            for key in self.results.log.keys():
                self.results.log[key] = results[key]  # Copy results to persistent log

            # Update throughput chart
            if len(results["Throughput"]) == len(time_axis):
                self.chart_placeholders["Throughput"].line_chart(
                    {"Throughput (Mbps)": self.results.log["Throughput"]}, use_container_width=True
                )

            # Update jitter chart
            if len(results["Jitter Client"]) == len(time_axis) and len(results["Jitter Server"]) == len(time_axis):
                self.chart_placeholders["Jitter"].line_chart({
                    "Jitter Client (ms)": self.results.log["Jitter Client"],
                    "Jitter Server (ms)": self.results.log["Jitter Server"]
                }, use_container_width=True)

            # Update OWD chart
            if len(results["OWD Client"]) == len(time_axis) and len(results["OWD Server"]) == len(time_axis):
                self.chart_placeholders["OWD"].line_chart({
                    "OWD Client (ms)": self.results.log["OWD Client"],
                    "OWD Server (ms)": self.results.log["OWD Server"]
                }, use_container_width=True)

            # Update tail latency chart
            if len(results["Tail Latency Client"]) == len(time_axis) and len(results["Tail Latency Server"]) == len(time_axis):
                self.chart_placeholders["Tail Latency"].line_chart({
                    "Tail Latency Client (ms)": self.results.log["Tail Latency Client"],
                    "Tail Latency Server (ms)": self.results.log["Tail Latency Server"]
                }, use_container_width=True)

    def reset_log_results(self):
        """Reset Log Results both for Dashboad and UDP-Client Logs."""
        self.results_log = {
            "Throughput": [],
            "Jitter Client": [],
            "Jitter Server": [],
            "Tail Latency Client": [],
            "Tail Latency Server": [],
            "OWD Client": [],
            "OWD Server": [],
            "Time": []
        }
        udp_client.results_log = self.results_log  # Reset client log results

    def start_server(self):
        """Start the UDP server."""
        args_server.a = self.server_ip
        args_server.p = self.server_port
        udp_server.server_main(args_server)

    def start_client(self):
        """Start the UDP client."""
        args_client.a = self.client_ip
        args_client.p = self.client_port
        args_client.i = self.experiment_interval_client
        args_client.l = self.packet_size_client
        args_client.t = self.experiment_duration
        udp_client.client_main(args_client)


def main():
    dashboard = DashboardController()
    if dashboard.run_experiment: # If Begin Experiment Clicked...
        dashboard.start_experiment()


if __name__ == "__main__":
    main()
