"""This script generates a JSON file that supplies the autocomplete data for a location (city/state)
field that supports autocomplete. The script will read a CSV file that can be downloaded from
http://www.unitedstateszipcodes.org/zip-code-database/ and turn it into a JSON file containing
a list of lists organized as follows: [city, state, estimated population]. Estimated population
is included so that these city/state combinations can be sorted in order of descending
population (this makes a lot more sense than alphabetical sorting when you think about it).

The script can easily be extended to create a JSON file that calculates the distances between
city/state or zip code combinations; that is, when given a location, the script determines all other
locations that are within x number of miles of an inputted location. This file could then be used
to customize search results such that they are custom sorted for each user based on how far the
result is from the user's location."""

# Standard Imports
import csv
import logging
import json
import os
from optparse import OptionParser
from itertools import chain

# Local imports
from states import states
from models import Location, Alias


def initialize():
    """Read arguments from the command prompt and kick off helper functions to do the work"""
    parser = OptionParser()
    parser.description = 'Recalculates the zipcode information using the inputted file or zipcode_database.csv'

    parser.add_option('-i', '--input',
                      type='string',
                      default='zip_code_database.csv',
                      dest='input_file',
                      help='The file path to the csv containing zipcode information')

    parser.add_option('-o', '--output',
                      type='string',
                      dest='calculate_cities',
                      help='''Provide the file path that city, state, and population information should be inputted into''')

    (options, _) = parser.parse_args()

    input_file = options.input_file
    cities_file_path = options.calculate_cities

    if not input_file:
        raise Exception('An input file containing zipcode information is needed to run this script.')

    if not options.calculate_cities:
        raise Exception('''An output json filepath is necessary to run this script!''')

    location_list, alias_list = read_zipcodes(input_file)

    if options.calculate_cities:
        make_city_list(location_list, alias_list, cities_file_path)


def read_zipcodes(input_file):
    """Reads in zip code information from a database csv defined by input_file
       and returns a list of locations and a list of aliases"""

    location_list = []
    alias_list = []

    with open(input_file, encoding='ISO-8859-1') as file_descriptor:
        reader = csv.reader(file_descriptor)

        for (zip_code, mail_type, primary_city, aliases, _, state, _, _, _,
             latitude, longitude, _, country, _, estimated_population, _) in reader:

            # Skip the line containing the column definitions
            if reader.line_num == 1:
                continue

            # Do not handle any zip codes outside of the US
            if country != 'US':
                logging.debug('line #{}: country equal to {}'.format(reader.line_num, country))
                continue

            # Do not handle military zip codes since they are often international
            if mail_type == 'MILITARY':
                logging.debug('line #{}: country equal to {}'.format(reader.line_num, mail_type))
                continue

            if state not in states:
                logging.debug('line #{}: state identifier of {} is invalid.'.format(reader.line_num, state))
                continue
            else:
                # All strings in the database are lowercase. Let's work with lowercase from the beginning.
                state = state.lower()

            if latitude:
                latitude = float(latitude)
            else:
                logging.error('line #{}: Latitude not present.'.format(reader.line_num))
            if longitude:
                longitude = float(longitude)
            else:
                logging.error('line #{}: longitude not present.'.format(reader.line_num))

            if not zip_code:
                logging.error('line #{}: zipcode not present.'.format(reader.line_num))

            if primary_city:
                # All strings in the database are lowercase. Let's work with lowercase from the beginning.
                primary_city = primary_city.strip().lower()
            else:
                logging.error('line #{}: primary_city not present.'.format(reader.line_num))

            if estimated_population:
                estimated_population = int(estimated_population)
            else:
                logging.debug('line #{}: estimated populated not present. Marking as 0'.format(reader.line_num))
                estimated_population = 0

            if aliases:
                aliases = [city.strip().lower() for city in aliases.split(',')]
                for city in aliases:
                    alias_list.append(Alias(reader.line_num, zip_code, city,
                                            state, estimated_population))

            # There are some extra fields in here... that data is in case we want to calculate which zip codes are within 
            # an xxx radius of other zip codes. That functionality is not included in this script.
            location_list.append(Location(reader.line_num, zip_code, latitude,
                                          longitude, primary_city, state,
                                          estimated_population)
                                 )

    return location_list, alias_list


def make_city_list(location_list, alias_list, cities_file_path):
    """This functions accounts for the fact that some city state combinations appear more than once,
       just with different zip codes. We only care about the zip code with the greatest population.
       If a user inputs one of these city/state combinations with multiple zip codes, we will Take
       the combination with the largest population. This function removes duplicate city/state
       combinations and then writes the city/state/population combination to a file"""

    # The dictionary that will be encoded to a JSON file
    # We want to ensure each city/state combo is unique. Take the combo with the greatest estimated population.
    largest_places = {}

    # A place is either a Location or Alias object
    for place in chain(location_list, alias_list):
        if place not in largest_places:
            largest_places[place] = place.estimated_population
            logging.debug('Adding location {}'.format(place))
        else:
            if place.estimated_population > largest_places[place]:
                logging.debug('Replacing location {old_location} with {new_location}'
                              .format(old_location=output[place],
                                      new_location=place)
                              )
                largest_places[place] = place.estimated_population

    # We can't override the encoder for things that inherit from namedtuple since they
    # will just encode the way tuples do (I know... this stinks), we we need to pair
    # down the fields we need here
    output_list = [[place.primary_city.title(), place.state.upper(), place.estimated_population] for place in largest_places]
    write_json_file(output_list, cities_file_path)


def write_json_file(output, file_path):
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.curdir, file_path)

    with open(file_path, 'wt') as json_handler:
        json.dump(output, json_handler)

if __name__ == '__main__':
    initialize()
