# 1. Project Structure
This directory mainly has 5 files and 5 folders. The files are:

1. inswitch_anomaly.p4 -> Entry p4 file ( Data plane ).
2. mycontroller.py -> Entry py file ( Control plane ).
3. Makefile -> Make file to compile p4 program and network topology, and then run the mininet.
4. receive.py -> py file running on a host to receive packets.
5. send.py -> py file running on a host to send packets.

And then the folders:

1. ML -> Contains py files to generate decision tree models and the sketch.
2. config -> Contains txt files to configure decision tree and forwading action.
3. pod-topo -> Contains json files to configure the network topology and swtiches in the runtime, if needed.
4. includes -> Contains p4 files included by the entry p4 file, inswtich_anomaly.p4.
5. imports -> Contains py files imported by the entry control plane py file, mycontroller.py.

# 2. Run the exmaple
First put the project files in the path:

`~/tutorials/exercises/`

Then run the command line:

`make run`

This will compile the p4 program and build the network topology and run mininet.

Once the mininet is running, open another terminal and run the command line:

`sudo python3 ./mycontroller.py`

This will install routing rules into the switch and print them ( May print things out in bytes ). Finally, in the mininet, run:

`xterm h1 h2 h3 h4`

In h2, h3, h4's terminal, run:

`./receive.py`

And then in h1's terminal, run:

`./send.py 10.0.2.2 HelloWorld`

And you will see the information about pkts in h1's and h3's terminal.

