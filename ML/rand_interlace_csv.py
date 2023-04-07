###
# Psuedorandomly interlace two given .csv files and write to the output
# Riley McGinn
###

import csv
import sys
import os
import random

def interlace(csv1_path: str, csv2_path: str, output_path: str):
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

    # Loop through input simultaneously
    while True:
        # pick randomly between reader1 and reader2 to write rows
        if random.randint(1,2) == 1:
            try:
                row1 = next(reader1)
                writer.writerow(row1)
            except StopIteration:
                # reader 1 is empty, write the rest of reader 2 and break
                for row2 in reader2:
                    writer.writerow(row2)
                break
        else:
            try:
                row2 = next(reader2)
                writer.writerow(row2)
            except StopIteration:
                # reader2 is empty, write the rest from reader1 and break
                for row1 in reader1:
                    writer.writerow(row1)
                break

    # copy from temp to output
    temp.close()
    temp = open(temp_path) # reopen in read mode
    reader1 = csv.reader(temp)
    output = open(output_path, "w", newline="")
    writer = csv.writer(output)
    for packet in reader1:
        writer.writerow(packet)

    # file cleanup
    temp.close()
    os.remove(temp_path)
    file1.close()
    file2.close()
    output.close()

if __name__ == '__main__':
    interlace(sys.argv[1], sys.argv[2], sys.argv[3])
