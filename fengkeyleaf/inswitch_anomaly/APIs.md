# fengkeyleaf.inswitch_anomaly

## csvparaser.py

### Class: Parser

Class to parse processed pkt csv files into a dict.

#### parse

 Parse a csv file into a dict.

---

## data_prcocessor.py

### Class: DataProcessor

Class to do the all tree processing steps:

#### process

        Process data sets and train trees. Start from beginning.
        1) Re-format csv data sets.
        2) Generate sketch csv files.
        3) Train a tree with the sketch files.

---

#### train_trees

Train tree with given csv files.

---

## mapper.py

### Class: Mapper

Class to get rid of unwanted features and mapping wanted ones to our favorite names.

---

## mix_make_ups.py

### Class: Mixer

Class to mix synthesised pkts.

#### mix

Mix synthesised pkts into the original data set.

---

## pkt_processor.py

### Class: PktProcessor

Process original pkt data set, like getting rid of unwanted features, adding synthesised good pkts.

#### process

Process a csv pkt file, adding header, mapping features, re-numbering and spoofing macs

---

## sketch.py

### Class: Sketch

Sketch class. Currently tracking src IP and dst IP.

## sketch_write.py

### Class: SketchWriter

Generate sketch csv files to train trees.

#### process

Process pre-processed csv pkt files and balancing the data set, and track some features with the sketch.

---

#### train

Train sketch with processed pkt data sets. Data sets may include synthesised good pkts or may not.

---

## tree.py

### Class: Tree

Train decision trees with sketch csv files.

#### process

Process pkt sketch csv file and train a tree.

---

#### train

Train a tree with designed features. No sketch applied.

---

