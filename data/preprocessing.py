""" """
import csv
import json
from typing import *

data= dict()

def dump_valgresultater():

    # Since these two files are formatted exactly the same, we can reuse the code.
    for filename in ["./sources/folketingsvalg.csv", "./sources/kommunalvalg.csv"]:



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
                    data[current_party].append((row[1], int(row[2])))

            with open("./preprocessed/"+filename[10:-4]+'.json', 'w') as fp:
                json.dump(data, fp)

def dump_gennemsnitsalder():

    with open("./sources/gennemsnitsalder.csv", encoding='ISO-8859-1') as csvfile:
        csvreader = csv.reader(csvfile)

        # Skip header lines in csv file
        next(csvreader)
        next(csvreader)
        next(csvreader)
        next(csvreader)

        for row in csvreader:
            data[row[1]] = row[2]
        
        with open('./preprocessed/gennemsnitsalder.json', 'w') as fp:
            json.dump(data, fp)

def dump_ratioejerlejere():

    with open("./sources/ratioejerlejere.csv", encoding='ISO-8859-1') as csvfile:
        csvreader = csv.reader(csvfile)

        # Skip header lines in csv file
        next(csvreader)
        next(csvreader)
        next(csvreader)
        next(csvreader)
        next(csvreader)

        for row in csvreader:
            data[row[2]] = {"ejere":row[3], "lejere": row[4]}
        
        with open('./preprocessed/ratioejerlejere.json', 'w') as fp:
            json.dump(data, fp)

def dump_disponibelindkomst():

    with open("./sources/disponibelindkomst.csv", encoding='ISO-8859-1') as csvfile:
        csvreader = csv.reader(csvfile)

        # Skip header lines in csv file
        for _ in range(8):
            next(csvreader)

        for row in csvreader:
            data[row[4]] = row[5]
        
        with open('./preprocessed/disponibelindkomst.json', 'w') as fp:
            json.dump(data, fp)

def dump_uddannelsesniveau():

    with open("./sources/uddannelsesniveau.csv", encoding='ISO-8859-1') as csvfile:
        csvreader = csv.reader(csvfile)

        # Skip header lines in csv file
        for _ in range(8):
            next(csvreader)

        for row in csvreader:
            row = row[4:]
            data[row[0]] = {
                "ingen uddannelse": row[2],
                "grundskole": row[1],
                "gymnasiel uddannelse": row[3],
                "erhvervsfaglig uddannelse": row[4],
                "bachelor uddannelse": row[5],
                "lange videregående uddannelser": row[6]
            }
        
        with open('./preprocessed/uddannelsesniveau.json', 'w') as fp:
            json.dump(data, fp)

def dump_koensfordeling():

    with open("./sources/koensfordeling.csv", encoding='ISO-8859-1') as csvfile:
        csvreader = csv.reader(csvfile)

        # Skip header lines in csv file
        for _ in range(6):
            next(csvreader)

        for row in csvreader:
            row = row[3:]
            data[row[0]] = {"maend": row[1], "kvinder": row[2]}
        
        with open('./preprocessed/koensfordeling.json', 'w') as fp:
            json.dump(data, fp)


if __name__ == "__main__":
    dump_valgresultater()
    dump_gennemsnitsalder()
    dump_ratioejerlejere()
    dump_disponibelindkomst()
    dump_uddannelsesniveau()
    dump_koensfordeling()
