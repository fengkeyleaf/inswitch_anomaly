

# Sketch-enabled In-switch Anomaly Detection

This project/paper( missing URL ) mainly focuses on letting a programmable switch( bmv2 ) have the ability to know what is a good or bad packet, thus enabling in-switch anomaly detection with sketches enabled.

## 1. Project Structure

This directory mainly has 5 files and 6 folders. The files are:

1. [inswitch_anomaly.p4](https://github.com/fengkeyleaf/inswitch_anomaly/blob/main/inswitch_anomaly.p4) -> Entry p4 file ( Data plane ).
3. [Makefile](https://github.com/fengkeyleaf/inswitch_anomaly/blob/main/Makefile) -> Make file to compile p4 program and network topology, and then run the mininet.
4. [receive.py](https://github.com/fengkeyleaf/inswitch_anomaly/blob/main/receive.py) -> py file running on a host to receive packets.
5. [send.py](https://github.com/fengkeyleaf/inswitch_anomaly/blob/main/send.py) -> py file running on a host to send packets.

And then the folders:

1. config -> Contains txt files to configure decision tree and forwading action.
2. docs -> folder containing various documentation.
3. fengkeyleaf -> self-developed py library package, including those files related to in-switch anomaly detection.
4. includes -> Contains p4 files included by the entry p4 file, inswtich_anomaly.p4.
5. pod-topo -> Contains json files to configure the network topology and swtiches in the runtime, if needed.
6. pseudocode -> Contains pseudocode txt files for each model.
7. utils -> py files used by [the p4 tutorial VM](https://github.com/p4lang/tutorials/tree/master/vm-ubuntu-20.04) to compile files and running tests.

## 2.Prerequisites

1. P4 VM either from [p4 tutorials](https://github.com/p4lang/tutorials/tree/master/vm-ubuntu-20.04) or [p4 guide](https://github.com/jafingerhut/p4-guide/tree/master).
2. Python packages: [numpy](https://numpy.org/install/), [pandas](https://pandas.pydata.org/docs/getting_started/install.html), [sklearn](https://scikit-learn.org/stable/install.html), [colorlog](https://pypi.org/project/colorlog/), [scapy](https://scapy.net/), [ptf](https://github.com/p4lang/ptf), [p4runtime_sh](https://github.com/p4lang/p4runtime-shell). You can first check out whether those VMs have these packages installed or not and install missing ones if necessary.

## 3. Run Tests

### 3.1 Generate ML models and datasets

(* Missing pictures *)

> python .\fengkeyleaf\inswitch_anomaly\_executes\_data_pro.py -da datasetFolderPath [ -dm madeUpPacketsFolderPath -he headerFilePath -iwe isWritingEvaluationResult -inb isNotBalancing -lim sketchLimiation -ll loggingLevel ]

| Identifier | Value                     | Description                                                  | Example                                                      | Default                     |
| ---------- | ------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | --------------------------- |
| -da        | datasetFolderPath         | Folder path to training datasets without sub-folders.        | "D:\networking\datasets\anomoaly_detection\BoT-loT"          |                             |
| -dm        | madeUpPacketsFolderPath   | Folder path to synthesized good packets without sub-folders. (Optional) | "D:\networking\datasets\anomoaly_detection\pcap"             | None                        |
| -he        | headerFilePath            | File path to the csv header file (Optional)                  | "D:\networking\datasets\anomoaly_detection\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv" | None                        |
| -iwe       | isWritingEvaluationResult | Is writing evaluation results to a file (Optional)           | True                                                         | False                       |
| -inb       | isNotBalancing            | Is not data balancing (Optional)                             | False                                                        | False                       |
| -lim       | sketchLimiation           | Sketch LImiation when validating ML models (Optional)        | 8                                                            | -1( meaning no limitation ) |
| -ll        | loggingLevel              | Logging level                                                | DEBUG                                                        | INFO                        |

For example:

>  python .\fengkeyleaf\inswitch_anomaly\_executes\_data_pro.py -da "D:\networking\datasets\anomoaly_detection\BoT-loT" -he "D:\networking\datasets\anomoaly_detection\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv" -iwe True -lim 8

This commend will use datasets located in the folder, "D:\networking\datasets\anomoaly_detection\BoT-loT", as training datasets, and the header file, , to first pre-process packets, do sketching algorithm and finally train a decision tree model while writing evaluation results into a file and setting the sketch limitation to 8 when validating. Once the process is done, we will get the following file structure:

> ./BoT-loT:
>
> ​	-- balanced_reformatted
>
> ​	-- re-formatted
>
> ​	-- sketches
>
> ​	-- trees
>
> ​	-- UNSW_2018_IoT_Botnet_Dataset_1.csv
>
> ​	-- ......
>
> ​	-- UNSW_2018_IoT_Botnet_Dataset_n.csv
>
> ​	-- sketches_accu_result.csv

where the folder, balanced_reformatted, contains csv dataset files after pre-processing and balancing process, and the folder, re-formatted, contains csv dataset files only after packet pre-process, and the folder, sketches, contains sketching csv files consumed by ML training framework, and the folder, trees, contains decision tree models in the form of txt file. The file named, sketches_accu_result.csv, is the one containing evaluation results with sketch limitation after the training process is done ( if -iwe is set to true ).

### 3.2 Run tests in P4 VM

(* Missing pictures *)

First going to the working directory:

> ~/inswitch_anomaly/

Then run the command line:

> python3 ./fengkeyleaf/inswitch_anomlay/\_executes/\_topo_json.py
>

This will read an input pkt data file and convert it to a network toplogy, read by the P4 mininet. You can also change the file path to the input data in [that file](https://github.com/fengkeyleaf/inswitch_anomaly/blob/main/fengkeyleaf/inswitch_anomaly/_executes/_topo_json.py).

Then you can choose which tree model you want to inject into the data plane in the p4 runtime in the file, [_mycontroller.py](https://github.com/fengkeyleaf/inswitch_anomaly/blob/main/fengkeyleaf/inswitch_anomaly/_executes/_mycontroller.py#L178).

After this, run the command line:

> make run
>

This will compile the p4 program and build the network topology and run mininet.

Once the network is initialized and the mininet is running, open another terminal and run the command line:

> sudo python3 ./fengkeyleaf/inswitch_anomaly/\_executes/\_mycontroller.py
>

After a few minuets, the program will automatically start sniffing on the host1 and send all pkts from the dataset on the host2.

Once the sending process is done, the program will also stop sniffing, evaluate the accuracy and output the result to a file named output.json in the working directory containing all packet IDs received on host2 and the evaluation results at the end of the file. If no such file is generated but another file named output_raw.json is generated, manually run the file named [_eval_test.py](https://github.com/fengkeyleaf/inswitch_anomaly/blob/main/fengkeyleaf/inswitch_anomaly/_eval_test/_eval_test.py) to get the result.

Note that s1-runtime.json should be configured in topology.json if outside runtime routing rules should be injected when initializing the network, something like: "runtime_json" : "pod-topo/s1-runtime.json".

## 3. Debugging ( PTF )

Note that there are [PTF tests](https://github.com/fengkeyleaf/inswitch_anomaly/blob/main/fengkeyleaf/inswitch_anomaly/_ptf/_inswitch_anomaly.py) in this project, you can use them as reference when you want to add extra features to the program and test it.

## 4. References

1. [BEHAVIORAL MODEL (bmv2)](https://github.com/p4lang/behavioral-model)
2. [P4 tutorials](https://github.com/p4lang/tutorials/tree/master)
3. [PTF](https://github.com/p4lang/ptf)
4. [p4-guide](https://github.com/jafingerhut/p4-guide)
5. [IIsy](https://github.com/cucl-srg/IIsy)

