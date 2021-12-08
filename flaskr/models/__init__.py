from flaskr import app
from typing import * 
import json
import os
import os, sys, codecs

def load_json_data() -> Dict:
    """ """

    data = {}

    disponibelindkomst = json.load(open("../data/preprocessed/disponibelindkomst.json"))
    for key, value in disponibelindkomst.items():
        if key not in data:
            data[key] = {}
        data[key]["indkomst"] = value

    koensfordeling = json.load(open("../data/preprocessed/koensfordeling.json"))
    for key, value in koensfordeling.items():
        if key not in data:
            data[key] = {}
        data[key]["koensfordeling"] = value

    gennemsnitsalder = json.load(open("../data/preprocessed/gennemsnitsalder.json"))
    for key, value in gennemsnitsalder.items():
        if key not in data:
            data[key] = {}
        data[key]["gennemsnitsalder"] = value

    folketingsvalg = json.load(open("../data/preprocessed/folketingsvalg.json"))
    for key, value in folketingsvalg.items():
        print(value)
        # key = party
        for res in value:
            # res = [kommunne, tal]
            if res[0] not in data:
                data[res[0]] = {}
            # data[kommune][party] = tal
            data[res[0]][key] = res[1] 


    ratioejerelejere = json.load(open("../data/preprocessed/ratioejerlejere.json"))
    for key, value in ratioejerelejere.items():
        if key not in data:
            data[key] = {}
        data[key]["ratioejerelejere"] = value

    uddannelsesniveau = json.load(open("../data/preprocessed/uddannelsesniveau.json"))
    for key, value in uddannelsesniveau.items():
        if key not in data:
            data[key] = {}
        data[key]["uddannelsesniveau"] = value

    json.dump(data, open("test.json", 'w'))

