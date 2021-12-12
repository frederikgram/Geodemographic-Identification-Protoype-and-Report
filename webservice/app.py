import cv2
import math
import json
import base64
from operator import itemgetter
from flask import Flask, render_template

app = Flask(__name__)
original_map = cv2.imread("map.png");
data = json.load(open("data.json", 'r'))


# Coloring Utilities

def floodfill(img, coords, col):
    img_copy = img.copy()
    cv2.floodFill(img_copy, None, seedPoint=coords, newVal=col, loDiff=(35,35,35,35), upDiff=(35,35,35,35))
    return img_copy


def rgb(minimum, maximum, value):
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value-minimum) / (maximum - minimum)
    b = int(max(0, 255*(1 - ratio)))
    g = 0
    r = b

    return r, g, b


# Search Utilities

def get_normalized_difference(d, metadata=None):
    if metadata != None:
        return ((d-metadata["minv"]) * 100) / (metadata["maxv"]-metadata["minv"])
    else:
        return d[list(d.keys())[0]]["percent"]


criteria_metadata_dict = {}
def get_criteria_metadata(criteria):

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

def search_for_criterias(criterias, priorities=None):
    """ """
    
    # Counties
    for key, value in data.items():
    
        innerdiffs  = []
        
        # e.g. Indkomst, Koensfordeling
        for enu, criteria in enumerate(criterias):
            
            
            # Hacky solution for search for
            # the inverse of the first element in   
            # the dataset, if you wanted to find
            # the counties with the most women pr. capita
            # you'd search for men and append :t at the end
            invert = False
            if criteria[-2:] == ":t":
                criteria = criteria[:-2]      
                invert = True

            # Subdict specifier, if people wanted to find say.
            # a specific party in the dictionary of parlamentary votes
            if ':' in criteria:
                crit1 = criteria.split(':')[0]    
                crit2 = criteria.split(':')[1]    
                diff = value[crit1][crit2]["percent"]

            elif isinstance(value[criteria], dict):
                diff = get_normalized_difference(value[criteria])

            else:
                metadata = get_criteria_metadata(criteria)
                diff = get_normalized_difference(value[criteria], metadata)
                    
            if invert:
                diff = diff * (-1) 

            innerdiffs.append(diff)

        data[key]["diff"] = sum(innerdiffs)
        print(key, ": ", data[key]["diff"] / 100)

    sorted_data = dict(sorted(data.items(), key=lambda item: item[1]["diff"], reverse=True))
    return sorted_data



@app.route("/map/")
def index():

    new_image = original_map.copy()

    sorted_dict = search_for_criterias(["ratioejerelejere:t", "disponibelindkomst"])
    sorted_dict = search_for_criterias(["folketingsvalg:A. Socialdemokratiet"])
    sorted_dict = search_for_criterias(["ratioejerelejere"])
    sorted_dict = search_for_criterias(["disponibelindkomst", "ratioejerelejere"])
    sorted_dict = search_for_criterias([
        "uddannelsesniveau:bachelor uddannelse",
        "uddannelsesniveau:lange videregående uddannelser",
        "disponibelindkomst",
        "gennemsnitsalder:t",
        "folketingsvalg:Ø. Enhedslisten - De Rød-Grønne",
    
    ])
    #sorted_dict = search_for_criterias(["koensfordeling:maend:t"])
    sdl = sum([1 for s in sorted_dict.values() if "coordinates" in s])

    new_image = original_map.copy()
    idx = 0
    for key, value in sorted_dict.items():
        
        if "coordinates" not in value:
            continue
    
        coords = tuple(value["coordinates"])

        new_image = floodfill(new_image, coords, rgb(0, 210, idx))
        idx += 1
        
        #print(key)
        #cv2.imshow("r", new_image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

    cv2.imwrite("./static/filled.png", new_image)
    return render_template("index.html")

