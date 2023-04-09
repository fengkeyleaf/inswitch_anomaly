###
# Label input file as benign traffic
# Riley Mcginn
###

import csv
import sys
import os

def label(csv_path: str):
    temp_path = os.path.join(os.getcwd(), 'temp.csv')
    input = open(csv_path)
    temp = open(temp_path, "w", newline="")
    reader = csv.reader(input)
    writer = csv.writer(temp)

    # write header to new file
    headers = next(reader)
    headers.append("Label")
    writer.writerow(headers)

    # label packets as benign (0)
    for packet in reader:
        packet.append("0")
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

    # file cleanup
    temp.close()
    os.remove(temp_path)
    output.close()

if __name__ == '__main__':
    label(sys.argv[1])
