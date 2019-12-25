import requests

OVERPASS_API_URL = 'https://lz4.overpass-api.de/api/interpreter'
STANDARD_QUERY = """
    way(50.746,7.154,50.748,7.157) ["building"];
    (._;>;);
    out;
    """

request = requests.post(OVERPASS_API_URL, data=STANDARD_QUERY)
string = request.content.decode('utf-8')

print(string)

f = open("nodes.osm", "w")
f.write(string)
f.close()