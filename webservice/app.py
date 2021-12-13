""" Expose a web-service allowing a user to search the counties
of Denmark based on criterias such as parlamentary votes, demographics and more.
"""

import cv2
import math
import json
import base64
import numpy
from typing import *
from operator import itemgetter
from flask import Flask, render_template, request

app = Flask(__name__)

# Initialize Global Scope Variables
original_map: Final[numpy.ndarray] = cv2.imread("map.png")
data: Final[Dict[str, Dict[str, Any]]] = json.load(open("data.json", "r"))
number_of_counties: Final[int] = len(data.keys())
criteria_metadata_dict: Dict[str, Tuple[int, int, int]] = dict()


def floodfill(
    img: numpy.ndarray, coords: Tuple[int, int], col: Tuple[int, int, int]
) -> numpy.ndarray:
    """ Fills in a region on the given image bounded by
    the given color +- 35
    """

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
    """ Takes a given value and maps it to a range between
    0 and 255 based on the minimum and maximum values
    in its original range
    """

    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b = 255 - int(max(0, 255 * (1 - ratio)))
    g = 0
    r = b

    return r, g, b


def get_normalized_difference(d, metadata=None) -> float:
    """ Converts an absolute number into a normalized percentage
    by using the minimum and maximum values in the dataset
    found, for the given key the absolute value represents
    """

    return ((d - metadata["minv"]) * 100) / (metadata["maxv"] - metadata["minv"])


def get_criteria_metadata(criteria: str) -> Dict[str, float]:
    """ Returns the total, minimal and maximal value of a criteria
    found in the dataset, for any county. This is used to convert
    absolute values into percentages for normalized difference calculations
    """

    if criteria in criteria_metadata_dict:
        return criteria_metadata_dict[criteria]

    total = 0
    minv = 0
    maxv = 0

    for e, v in data.items():
        total += v[criteria]
        if v[criteria] < minv:
            minv = v[criteria]
        if v[criteria] > maxv:
            maxv = v[criteria]

    criteria_metadata_dict[criteria] = {"total": total, "minv": minv, "maxv": maxv}
    return criteria_metadata_dict[criteria]


def search_for_criterias(query) -> List[Dict]:
    """ Given a search query, return a sorted list
    of counties ordered by how well they fulfill
    the given search criteria
    """

    data_copy = data

    # County, County data
    for key, value in data.items():
        county_total_diff = 0

        for enum, criteria in enumerate(query["criterias"]):

            # Subclass-able criteria
            if type(criteria["key"]) == list:

                reference = value
                for i in criteria["key"]:

                    # Ensure that the current depth of the criteria exists
                    if i not in reference:
                        raise Exception("fdsdfds:")
                    reference = reference[i]

                # If the given criteria is formatted as a percentage
                # in the dataset, it is already normalized
                diff = reference["percent"]

            else:

                # If the value for the criteria in the dataset
                # is an absolute value, we need to normalize it using
                # the minimal and maximal values for that criteria
                # found in the entire dataset
                metadata = get_criteria_metadata(criteria["key"])
                diff = get_normalized_difference(value[criteria["key"]], metadata)

            # Apply search modifiers
            if criteria["priority"]:
                diff *= criteria["priority"]
            if criteria["invert"]:
                diff *= -1

            county_total_diff += diff

        data_copy[key]["diff"] = county_total_diff

    sorted_data = dict(
        # Sort the counties based on this difference, lowest difference becomes the first element
        sorted(data_copy.items(), key=lambda item: item[1]["diff"], reverse=True)
    )
    return sorted_data


def get_possible_criterias():
    """ Recursively walks down
    each possible node in the dataset,
    return a complete set of all
    searchable criterias
    """

    criterias: List[str] = list()

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


possible_criterias: Final[List[str]] = get_possible_criterias()

# This is clearly a hacky solution
# as we'd love to have a generic function
# instead, but this is primarily limited
# by our very primitive web-service
# solution, so this is a compromise
# for the MVP
def hardcoded_criteria_filler(crit):
    """ Converts a given criteria into a
    list of keys in order of the respective
    level of nested needed to arrive at the
    given criteria """

    if crit in ["maend", "kvinder"]:
        return ["koensfordeling", crit]

    if crit in [
        "ingen uddannelse",
        "grundskole",
        "gymnasiel uddannelse",
        "erhvervsfaglig uddannelse",
        "bachelor uddannelse",
        "lange videregående uddannelser",
    ]:
        return ["uddannelsesniveau", crit]

    if crit in ["ejere", "lejere"]:
        return ["ratioejerelejere", crit]

    if crit in [
        "A. Socialdemokratiet",
        "B. Radikale Venstre",
        "C. Det Konservative Folkeparti",
        "D. Nye Borgerlige",
        "E. Klaus Riskær Pedersen",
        "F. SF - Socialistisk Folkeparti",
        "I. Liberal Alliance",
        "K. Kristendemokraterne",
        "O. Dansk Folkeparti",
        "P. Stram Kurs",
        "V. Venstre, Danmarks Liberale Parti",
        "Ø. Enhedslisten - De Rød-Grønne",
        "Å. Alternativet",
    ]:
        return ["folketingsvalg", crit]


# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers[
        "Cache-Control"
    ] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response


@app.route("/", methods=["GET", "POST"])
def index():

    criterias = []
    for crit in possible_criterias:
        if request.form.get(crit) != None:
            criterias.append(
                {
                    "key": hardcoded_criteria_filler(crit),
                    "invert": request.form.get(f"{crit}-invert") != None,
                    "priority": int(request.form[f"{crit}-slider"]) / 100,
                }
            )

    new_image = original_map.copy()
    query = {"criterias": criterias}
    sorted_dict = search_for_criterias(query)
    new_image = original_map.copy()

    for enum, (key, value) in enumerate(sorted_dict.items()):
        new_image = floodfill(new_image, value["coordinates"], rgb(0, 210, enum))

    cv2.imwrite("./static/filled.png", new_image)
    return render_template(
        "index.html", counties=sorted_dict.keys(), criterias=possible_criterias
    )
