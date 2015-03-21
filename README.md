This script generates a JSON file that supplies the autocomplete data for a location (city/state)
input field in a standard web form. The script will read a CSV file that can be downloaded from
http://www.unitedstateszipcodes.org/zip-code-database/ and turn it into a JSON file containing
a list of lists organized as follows: [city, state, estimated population]. Estimated population
is included so that these city/state combinations can be sorted in order of descending
population (this makes a lot more sense than alphabetical sorting when you think about it).

The script can easily be extended to create a JSON file that calculates the distances between
city/state or zip code combinations; that is, when given a location, the script determines all other
locations that are within x number of miles of an inputted location. This file could then be used
to customize search results such that they are custom sorted for each user based on how far the
result is from the user's location.