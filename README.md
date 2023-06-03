# 1. Project Structure

This directory mainly has 5 files and 6 folders. The files are:

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
6. pseudocode -> Contains pseudocode txt files for each model.

# 2. Run the exmaple

First put the project files in the path:

`~/tutorials/exercises/<FOLDER_NAME_OF_YOUR_CHOICE>/`

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

# 3. Sketch Testing

Assumptions: 
- Cannot send pkts to host itself.
- All 4 features may be set to 0 when no replacement policy applied.
- Replacement policy: replace the last one when ties.
- Decision Tree configuration: ./config/test_tree.txt.

Test cases:

1. One pkt: h3 -> pkt -> h1;
2. Two pkts: h3 -> h1, h2 -> h1; h1 -> h2, h2 -> h3;
3. Three pkts: h3 -> h1, h2 -> h1, h4 -> h1;
4. Four pkts: h1 -> h2, h2 -> h3, h3 -> h4, h4 -> h1;
5. Lowest count: Four pkts;
6. Highest TLS: Four pkts;
7. Smallest TLS: Four pkts;
8. No replacement: Four pkts;

# 4. Generating data set

1. create_dataset.py attack_data benign_data result.csv ( Optionally )
2. sketch_write.py result.csv sketch.csv
3. tree.py sketch.csv tree.txt

#  5. Data Folders

1. Data: original data sets.
2. original: processed without adding synthesized good pkts.
3. processed: processed with adding synthesized good pkts.
4. re-formatted: Get rid of unwanted features and mapping feature names.
5. sketches: sketch csv files in one column, 4 features in a list.
6. sketches_new: sketch csv files in separate column.
7. trees: trained tree txt files.