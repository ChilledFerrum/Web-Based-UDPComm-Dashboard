# UDP Client-Server Communication Dashboard Controller
| An implementation of a web-based controlled UDP Client Server Communication network written in python.

###### This project was developed originally as an assignment and later refined to be published as an open-source project in my Github repository. 

## Description
> An implementation of a UDP Client Server communication system used to analyze the traffic between both sides effectively and identify latency spikes. <br><br> The system can be effectively executed in two ways: <br> Manually, by directly executing each individual program in the terminal and passing arguments for both 'udp-server.py' & 'udp-client.py'. <br> Dynamically, using a web-based tool developed using Streamlit that allows the user to begin experiments by setting the preferred parameters of the network and the experiment.

## Requirements
> - (python 3.8 >= and pip) or conda
> - streamlit, matplotlib

## How to Run

<span style="font-size: 16px; font-weight: bold;">Method 1: Web-based tool</span> 
(streamlit)
```
cd Web-Based-UDPComm-Dashboard
conda create -n client-server-comm-controller python==3.10 -y 
conda activate client-server-comm-controller
pip install -r requirements.txt
streamlit run Dashboard-Controller.py
```
<span style="font-size: 16px; font-weight: bold;">Method 2: Manually</span> 

```
cd Web-Based-UDPComm-Dashboard
conda create -n client-server-comm-controller python==3.10 -y 
conda activate client-server-comm-controller
pip install -r requirements.txt
```
Run the Server '*udp-server.py*' on a terminal...
```
python udp-server.py --a 127.0.0.1 --p 8080 --i 1
```

Run the client '*udp-cliet.py*' on a new terminal...
```
python udp-client.py --a 127.0.0.1 --p 8080 --i 1 --t 10
```