import cv2
import math
import json
import base64
import numpy
from typing import *
from operator import itemgetter
from flask import Flask, render_template, request

app = Flask(__name__)


original_map: Final[numpy.ndarray] = cv2.imread("map.png")
data: Final[Dict[str, Dict[str, Any]]] = json.load(open("data.json", "r"))
number_of_counties: Final[int] = len(data.keys())


def floodfill(
    img: numpy.ndarray, coords: Tuple[int, int], col: Tuple[int, int, int]
) -> numpy.ndarray:
    img_copy = img.copy()
    cv2.floodFill(
        img_copy,
        None,
        seedPoint=coords,
        newVal=col,
        loDiff=(35, 35, 35, 35),
        upDiff=(35, 35, 35, 35),
    )
    return img_copy


def rgb(minimum, maximum, value) -> Tuple[int, int, int]:
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b = 255 - int(max(0, 255 * (1 - ratio)))
    g = 0
    r = b

    return r, g, b


def get_normalized_difference(d, metadata=None) -> float:
    return ((d - metadata["minv"]) * 100) / (metadata["maxv"] - metadata["minv"])


criteria_metadata_dict = {}


def get_criteria_metadata(criteria: str) -> Dict[str, float]:

    if criteria in criteria_metadata_dict:
        return criteria_metadata_dict[criteria]

    total = 0
    minv = 0
    maxv = 0

    for e, v in data.items():
        total += v[criteria]
        if v[criteria] < minv: minv = v[criteria]
        if v[criteria] > maxv: maxv = v[criteria]

    criteria_metadata_dict[criteria] = {"total": total, "minv": minv, "maxv": maxv}
    return criteria_metadata_dict[criteria]


def search_for_criterias(query) -> List[Dict]:
    """ """

    new_data = data

    # County, County data
    for key, value in data.items():
        county_total_diff = 0

        for enum, criteria in enumerate(query["criterias"]):

            # Subclass-able criteria
            if type(criteria["key"]) == list:

                reference = value
                for i in criteria["key"]:

                    # Ensure that the current depth of the criteria exists
                    if i not in reference: raise Exception("fdsdfds:")
                    reference = reference[i]

                diff = reference["percent"]

            else:
                metadata = get_criteria_metadata(criteria["key"])
                diff = get_normalized_difference(value[criteria["key"]], metadata)

            if criteria["priority"]: diff *= criteria["priority"]
            if criteria["invert"]: diff *= -1
            county_total_diff += diff

        new_data[key]["diff"] = county_total_diff

    sorted_data = dict(
        sorted(new_data.items(), key=lambda item: item[1]["diff"], reverse=True)
    )
    return sorted_data


def get_possible_criterias():
    
    criterias = []
    def inner(reference):
        if type(reference) != dict:
            return

        for key in reference.keys():
            if type(reference[key]) == dict:
                criterias.append(key)
                inner(reference[key])

    reference = data[list(data.keys())[0]]
    for key in reference.keys():
        inner(reference[key])
    

    return criterias

crits = get_possible_criterias()
    

def hardcoded_criteria_filler(crit):
            

    if crit in ["maend", "kvinder"]:
        return ["koensfordeling", crit]

    if crit in ["ingen uddannelse", "grundskole", "gymnasiel uddannelse", "erhvervsfaglig uddannelse", "bachelor uddannelse", "lange videregående uddannelser"]:
        return ["uddannelsesniveau", crit]

    if crit in ["ejere", "lejere"]:
        return ["ratioejerelejere", crit]

    if crit in ["A. Socialdemokratiet", "B. Radikale Venstre", "C. Det Konservative Folkeparti", "D. Nye Borgerlige", "E. Klaus Riskær Pedersen", "F. SF - Socialistisk Folkeparti", "I. Liberal Alliance", "K. Kristendemokraterne", "O. Dansk Folkeparti", "P. Stram Kurs", "V. Venstre, Danmarks Liberale Parti", "Ø. Enhedslisten - De Rød-Grønne", "Å. Alternativet"]:
        return ["folketingsvalg", crit]

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response 

@app.route("/", methods=["GET", "POST"])
def index():


    criterias = []
    for crit in crits:
        if request.form.get(crit) != None:
            criterias.append({
                "key": hardcoded_criteria_filler(crit),
                "invert": request.form.get(f"{crit}-invert") != None,
                "priority": int(request.form[f"{crit}-slider"]) / 100 

            })


    new_image = original_map.copy()

    query = {"criterias": criterias}
    print(query)



    sorted_dict = search_for_criterias(query)

    new_image = original_map.copy()


    get_possible_criterias()

    for enum, (key, value) in enumerate(sorted_dict.items()):
        new_image = floodfill(new_image, value["coordinates"], rgb(0, 210, enum))


    cv2.imwrite("./static/filled.png", new_image)
    return render_template("index.html", counties=sorted_dict.keys(), criterias=crits)
