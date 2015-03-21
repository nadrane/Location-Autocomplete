This script generates a JSON file that supplies the autocomplete data for a location (city/state)
field that supports autocomplete. The script will read a CSV file that can be downloaded from
http://www.unitedstateszipcodes.org/zip-code-database/ and turn it into a JSON file containing
a list of lists organized as follows: [city, state, estimated population]. Estimated population
is included so that these city/state combinations can be sorted in order of descending
population (this makes a lot more sense than alphabetical sorting when you think about it).