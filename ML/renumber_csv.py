###
# Renumbers the given .csv so each pkt has a unique identifier
# Riley McGinn

import csv
import sys
import os

def renumber(csv_path):
    temp_path = os.path.join(os.getcwd(), 'temp.csv')
    input = open(csv_path)
    temp = open(temp_path, "w", newline="")
    reader = csv.reader(input)
    writer = csv.writer(temp)

    # write header to new file
    header = next(reader)
    writer.writerow(header)

    # iterate, renumbering packets
    count = 0
    for packet in reader:
        count = count + 1
        packet[0] = count
        writer.writerow(packet)

    # copy from temp to output
    temp.close()
    temp = open(temp_path) # reopen in read mode
    reader = csv.reader(temp)
    input.close()
    output = open(csv_path, "w", newline="") # reopen in write mode
    writer = csv.writer(output)
    for packet in reader:
        writer.writerow(packet)
    temp.close()
    output.close()

    # file cleanup
    os.remove(temp_path)

if __name__ == '__main__':
    renumber(sys.argv[1])
