""" """
import csv
import json

data = {}

def dump_valgresultater():

    # Since these two files are formatted exactly the same, we can reuse the code.
    for filename in ["folketingsvalg.csv", "kommunalvalg.csv"]:
        with open(filename, encoding='ISO-8859-1') as csvfile:
            csvreader = csv.reader(csvfile)


            # Skip header lines in csv file
            next(csvreader)
            next(csvreader)
            next(csvreader)

            for row in csvreader:
    
                # We know that rows with a period in them are Party names
                if len(row) > 0 and '.' in row[0]:

                    # Setup an entry in the dictionary for the party
                    current_party = row[0]
                    data[current_party] = list()
                    continue

                # It not, we know that it is a row of
                # >> ['', 'partyname', 'votecounts']
                # So we just save the last two values, inside the
                # List of data, for the current party.
                if len(row) > 0:
                    data[current_party].append(row[1:])

            with open(filename[:-4]+'.json', 'w') as fp:
                json.dump(data, fp)


if __name__ == "__main__":
    dump_valgresultater()
