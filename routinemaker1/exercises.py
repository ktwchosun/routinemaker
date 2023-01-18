import json
import random
import pkg_resources

############ Load Exercises ############

filepath = pkg_resources.resource_filename(__name__, 'data/exercises.json')
with open(filepath) as data:
    all = json.load(data)

# list of exercises for each type
strength = [a for a in all if a["Type"] == "Strength"]
cardio = [a for a in all if a["Type"] == "Cardio"]
HIIT = [a for a in all if a["Type"] == "HIIT"]

############ Utility Functions ############

# function to get set of unique values by key
def unique(source, key):
    result = set()
    for s in source:
        if isinstance(s[key], list):
            for v in s[key]:
                result.add(v)
        else:
            result.add(s[key])
    return result

# function to filter exercises by key
def filter(source, target, key):
    result = []
    for s in source:
        if isinstance(s[key], list):
            if bool(set(target) & set(s[key])):
                s[key] = [x for x in s[key] if x in target]
                result.append(s)
        else:
            if s[key] in target:
                result.append(s)
    return result
