###
# Trims .csv input file to only include rows where
#   protocol = 'TCP'
# Riley McGinn

import csv
import sys
import os

def trim(csv_path):
    temp_path = os.path.join(os.getcwd(), 'temp.csv')
    input = open(csv_path)
    temp = open(temp_path, "w", newline="")
    reader = csv.reader(input)
    writer = csv.writer(temp)

    # write header to new file
    header = next(reader)
    writer.writerow(header)

    # write over packets if protocol = TCP
    for packet in reader:
        if(packet[4] == "TCP"):
            writer.writerow(packet)

    # copy from temp to output
    temp.close()
    temp  = open(temp_path) # reopen in read mode
    reader = csv.reader(temp)
    input.close()
    output = open(csv_path, "w", newline="") # reopen in write mode
    writer = csv.writer(output)
    for packet in reader:
        writer.writerow(packet)

    # file cleanup
    temp.close()
    os.remove(temp_path)
    output.close()

if __name__ == '__main__':
    trim(sys.argv[1])
