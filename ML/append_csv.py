###
# Append a .csv to the end of another .csv and write to a new file
# Riley McGinn
###

import csv
import sys
import os

def append(csv1_path: str, csv2_path: str, output_path: str):
    # open the csv files passed in
    file1 = open(csv1_path)
    file2 = open(csv2_path)
    temp_path = os.path.join(os.getcwd(), 'temp.csv')
    temp = open(temp_path, "w", newline="")

    # create readers
    reader1 = csv.reader(file1)
    reader2 = csv.reader(file2)
    writer = csv.writer(temp)

    # keep one of the headers, discard the other
    writer.writerow(next(reader1))
    next(reader2)

    # write the body of file1, then the body of file2
    for packet in reader1:
        writer.writerow(packet)
    for packet in reader2:
        writer.writerow(packet)

    # Copy from temp to output
    temp.close()
    temp = open(temp_path) # open temp in reader mode
    reader1 = csv.reader(temp)
    output = open(output_path,"w",newline="")
    writer = csv.writer(output)
    for packet in reader1:
        writer.writerow(packet)

    # file cleanup
    file1.close()
    file2.close()
    temp.close()
    os.remove(temp_path)
    output.close()

if __name__ == '__main__':
    append(sys.argv[1], sys.argv[2], sys.argv[3])
