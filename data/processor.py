""" """

import json
from typing import Dict, Any
from collections import defaultdict


def merge_datasets() -> Dict[str, Any]:
    """ Merges multiple json files as defined in the
        global scope, into a single dictionary object
    """

    data  = defaultdict(dict)

    # Enumerate over datasets and merge them into a single dictionary
    for enum, d in enumerate(files):
        for key, value in d.items():
            data[key][names[enum]] = value


    # The dataset for parlementary votes is formatted differently,
    # so we need to handle it individually
    for party, values in folketingsvalg.items():
        for county, votes in values:
            if "folketingsvalg" not in data[county]:
                data[county]["folketingsvalg"] = {}

            data[county]["folketingsvalg"][party] = str(votes)

    return data

def extend_dataset_with_ratios(dataset: Dict[str, Any]) -> Dict[str, Any]:
    """ Extend all fields containing absolute values with   
        a 'percentage' field, using the sum of all absolute
        values found in the given field
    """

    # Dictionaries are imuteable during 
    # iteration over their values, so we
    # mutate a copy of the dataset instead
    new_dataset = dataset

    for county, metadata in dataset.items():
        for field, values in dataset[county].items():

            # If the current field is not a dictionary
            # we know that it is a flat value, and
            # not a collection of values on which
            # one could calculate ratios on
            if not isinstance(values, dict):

                # Knowing our source data, we take this opportinity
                # to convert numeric values to their true datatype
                new_dataset[county][field] = float(dataset[county][field])
                continue

            total = sum([int(values[k]) for k in values.keys()])
            new_dataset[county][field].update({"total": total})
            
            for key, value in values.items():

                value = int(value)

                # The percentage of the total will always be 100%
                # so there is no reason to extend the field
                if key == "total":
                    continue

                # Extend already existing absolute value
                # with a newly calculated 'percentage' field
                # based on the total of all absolute values.
                new_dataset[county][field][key] = {
                    "absolute": value,
                    "percent": value / total*100 if total != 0 else 0
                }

    return new_dataset

if __name__ == "__main__":

    # Read all datasets into memory, assume that they all fit in memory 
    disponibelindkomst = json.load(open("disponibelindkomst.json", 'r'))
    folketingsvalg = json.load(open("folketingsvalg.json", 'r'))
    koensfordeling = json.load(open("koensfordeling.json", 'r'))
    gennemsnitsalder = json.load(open("gennemsnitsalder.json", 'r'))
    ratioejerelejere = json.load(open("ratioejerelejere.json", 'r'))
    uddannelsesniveau = json.load(open("uddannelsesniveau.json", 'r'))

    # Neglect 'Folketingsvalg' as it requires more specialized processing
    files = [disponibelindkomst, koensfordeling, gennemsnitsalder, ratioejerelejere, uddannelsesniveau]

    # Stringify names of datasets to be used as keys in the merged dataset
    names = ["disponibelindkomst", "koensfordeling", "gennemsnitsalder", "ratioejerelejere", "uddannelsesniveau"]

    # Collect, Combine, and Extend datasets
    data = merge_datasets()
    data = extend_dataset_with_ratios(data)

    # Dump new dataset
    json.dump(data, open("result.json", 'w'))
