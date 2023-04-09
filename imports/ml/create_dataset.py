###
# Script to create mixed, labeled, csv datasets for training 
# and testing inswitch anomaly detection
#
# Usage: create_dataset.py 
#               --benign <directory with benign .pcaps>
#               --attack <directory with attack .pcaps> 
# 
# combines all data from the benign directory and interlaces
# with the attack directory. Then applies some formatting to make
# it more usable with Xiaoyu's code and for testing purposes, and
# outputs a final .csv to the given directory
#
# Riley McGinn
###

### Notes ###
# Iteration over directory looks like this...

"""
import os
root = 'C/Users/riley/Documents/repos/inswitch_anomaly/pcaps/6-Attacks/1-Flood/'

for subdir, dirs, files in os.walk(root):
    for file in files:
        print(os.path.join(subdir, file))

"""

# I want to process these...
# If .pcap then convert to .csv and process like .csv

# To create a dataset
#   1) choose an attack to use
#   2) Convert attack .pcap to .csv
#   3) Label attack .csv bad
#   4) Convert Benign .pcaps to .csvs
#   5) Interlace interlace or append benign .csvs
#   6) Label combined benign data .csv as benign
#   7) Randomly interlace benign data and attack data
#   8) Create MAC addresses for the mixed csv
#   9) Re-number the mixed csv so each pkt has unique identifier
#   10) Save file and send to Xiaoyu for processing in P4

import os
import sys
import csv

import append_csv
import label_bad
import label_good
import rand_interlace_csv
import trim_to_TCP
import spoof_MACs
import renumber_csv

def create_dataset(attack_dir: str, benign_dir: str, output_path: str):
    attack_root = attack_dir
    benign_root = benign_dir
    temp_bad_path = os.path.join(os.getcwd(), 'temp_bad.csv')
    temp_good_path = os.path.join(os.getcwd(), 'temp_good.csv')

    # combine all attack data
    first = True
    for subdir, dir, files in os.walk(attack_root):
        for file in files:
            if first:
                first_file = open(os.path.join(subdir, file)) # open first file in read mode
                temp_bad = open(temp_bad_path, "w", newline="") # open temp_bad in write mode
                reader = csv.reader(first_file)
                writer = csv.writer(temp_bad)
                for packet in reader:
                    writer.writerow(packet)
                first_file.close()
                temp_bad.close()
                first = False
            else:
                append_csv.append( os.path.join( subdir, file ), temp_bad_path, temp_bad_path )

    # label attack data as bad
    label_bad.label( temp_bad_path )

    # combine all benign data
    first = True
    for subdir, dir, files in os.walk(benign_root):
        for file in files:
            if first:
                first_file = open(os.path.join(subdir, file)) # open first file in read mode
                temp_good = open(temp_good_path, "w", newline="") # open temp_good in write mode
                reader = csv.reader(first_file)
                writer = csv.writer(temp_good)
                for packet in reader:
                    writer.writerow(packet)
                first_file.close()
                temp_good.close()
                first = False
            else:
                append_csv.append( os.path.join( subdir, file ), temp_good_path, temp_good_path )
    
    # label benign data as good
    label_good.label( temp_good_path )

    # interlace good & bad data
    rand_interlace_csv.interlace( temp_good_path, temp_bad_path, output_path )

    # trim to TCP, spoof MAC addresses, and renumber
    trim_to_TCP.trim( output_path )
    spoof_MACs.spoof_MACs( output_path )
    renumber_csv.renumber( output_path )

    # file cleanup
    os.remove(temp_good_path)
    os.remove(temp_bad_path)


# To test the results...
#   1) Expect a list of unique pkt identifiers that were not dropped
#   2) Sort unique pkt identifiers so they're in order
#   3) Iterate over the mixed data input
#   4) multiple cases...
#       If pkt in list & pkt labeled good: good allow ++
#       If pkt in list & pkt labeled bad: bad allow ++
#       If pkt !in list & pkt labeled good: bad drop ++
#       If pkt !in list & pkt labeled bad: good drop ++
#   5) We want to see
#       High value of good allow / good count
#       Low value of bad allow / bad count
#       Low value of bad drop / good count
#       High value of good drop / bad count

if __name__ == '__main__':
    create_dataset(sys.argv[1], sys.argv[2], sys.argv[3])
