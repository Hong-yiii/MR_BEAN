from flask import Flask, request, jsonify
from weather_params_at_coordinate import *
from most_similar_point import *
import json

app = Flask(__name__)

def best_gmo_strain(longditude, lattitude):
    stats = weather_params_at_coordinate(longditude, lattitude)
    return most_similar_point(stats[1])

# to test without front end, call best_gmo_strain(longditude, lattitude)
# print (best_gmo_strain(longditude, lattitude))