from bingmaps.apiservices import LocationByPoint
import urllib.request
import json
import time
import os
import requests
import math



f = open("BingMapsKey.txt","r")
BingMapsKey = f.read()      # secretkey do pobrania kafelka mapy
f.close()



def get_pbp(p1, p2):
    
    x = p1[0] + 0.5 * (p2[0] - p1[0])
    y = p1[1] + 0.5 * (p2[1] - p1[1])

    return [ x, y ]



def bbox( sp ):
    p1 = sp[0].copy()
    p2 = sp[0].copy()

    for p in sp:
        if p[0] < p1[0]: p1[0] = p[0]
        if p[1] > p1[1]: p1[1] = p[1]
        
        if p[0] > p2[0]: p2[0] = p[0]
        if p[1] < p2[1]: p2[1] = p[1]

    return get_pbp(p1,p2), [p2[0]-p1[0],p1[1]-p2[1]]



def correct_bbox(x, w):
    if (x + w/2) > 1:
        x = x - w/2 + (1 - (x - w/2))/2
        w = 2*(1 - x)

    if (x - w/2) < 0:
        x = (x + w/2)/2
        w = 2*(x)

    return x, w



def darknet_bbox( cners, bbox ):
    width = (cners[3] - cners[1])
    height = (cners[0] - cners[2])
    x1 = abs((bbox[0][0] - cners[1]) / width )
    y1 = abs((bbox[0][1] - cners[2]) / height )
    x2 = abs( bbox[1][0] / width )
    y2 = abs( bbox[1][1] / height )

    x1, x2 = correct_bbox(x1,x2)
    y1, y2 = correct_bbox(y1,y2)
        
    return [    
                [
                    x1,
                    y1
                ],
                [
                    x2,
                    y2
                ]
            ]



def PolygonArea(corners):
    n = len(corners) # of corners
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    area = abs(area) / 2.0
    return area



def download( filename ):
    with open(filename + '.bin') as f:
        d = json.loads(f.read())
        corners = d['resourceSets'][0]['resources'][0]['bbox']

    OVERPASS_API_URL = 'https://lz4.overpass-api.de/api/interpreter'
    STANDARD_QUERY = """
        way(""" + str(corners).replace('[','').replace(']','') + """) ["building"];
        (._;>;);
        out;
        """

    request = requests.post(OVERPASS_API_URL, data=STANDARD_QUERY)
    string = request.content.decode('utf-8')

    f = open( filename + '.osm', "w")
    f.write(string)
    f.close()
    os.system('osmtogeojson ' + filename + '.osm > ' + filename + '.geojson')

    bboxes = []
    with open( filename + '.geojson') as f:
        d = json.loads(f.read())
        for bding in d['features']:
            if bding['geometry']['type'] == 'Polygon' and PolygonArea(bding['geometry']['coordinates'][0]) > 0.8e-08:
                try:
                    bboxes.append( bbox(bding['geometry']['coordinates'][0]))
                except:
                    print( 'Failed for bbox: ')
                    print( bding['geometry']['coordinates'] )
                    
    for i in range(0,len(bboxes)):
        bboxes[i] = darknet_bbox( corners, bboxes[i] )
    
    with open( 'labels/' + filename + '.txt', 'w') as f:
        for x in bboxes:
            print( '0', f'{x[0][0]:.6f}', f'{x[0][1]:.6f}',
            f'{x[1][0]:.6f}', f'{x[1][1]:.6f}', sep=" ", end="\n", file = f )



def generate_for(point = (51.05256,17.02998)):
    mapSize= "3000,3000"        # ustawienie rozmiaru mapy do pobrania
    mapMetadata = "1"           # flaga do pobrania metadanych
    filename = f'{point[0]:.6f}' + '_' + f'{point[1]:.6f}'

    def corners(pp,width):
        a = [ pp[0]-width, pp[1]-width, pp[0]+width, pp[1]+width ]
        return str(a[0])+","+str(a[1])+","+str(a[2])+","+str(a[3]), a

    mapArea, ret = corners(point,0.002)


    # http request pobierajacy kawalek mapy w JPG
    urlp = "https://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial?mapArea="+mapArea+"&mapsize="+mapSize+"&key="+BingMapsKey
    print(urlp)
    # http request pobierajacy metadane (rozmiar, koordynaty naroznikow itp..)
    urlpMeta = "https://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial?mapArea="+mapArea+"&mapsize="+mapSize+"&mapMetadata=1&key="+BingMapsKey

    # Subprogram do pobrania mapki
    print("Trying get a map....")
    try:
        contents = urllib.request.urlopen(urlp).read()  # wyslij request
        print("Pobralem mape")                          # jesli sie uda printuj message
        with open( str('images/' + filename + '.jpg'),"wb") as output:   # zapisz to co masz w pamieci do pliku (wb - writebinary)
            output.write(contents)
        output.close()                                  # zamknij zapisywany plik
    except:
        print("nie moglem pobrac mapy")                 # jesli jest fuckup to powiedz mi o tym
 
    time.sleep(0.5)                                     # anti - To many request error

    # subprogram do pobrania metadanych z kawalka mapki
    print("Trying get metadata....")
    try:
        contents = urllib.request.urlopen(urlpMeta).read()  # wyslij request
        print("Pobralem metadane")                          # powiedz czy udalo sie pobrac
        #print(contents)
        with open( filename + '.bin',"wb") as output:       # zapisz to co masz w pamieci do pliku (wb - writebinary)
            output.write(contents)
        output.close()                                      # zamknij zapisywany plik

        mapjs = json.loads(contents)                            # odpowiedz jest formatu JSON - tutaj go parsuje
        resources = mapjs["resourceSets"][0]["resources"][0]    # przepisuje odpowiednie drzewko JSON z odpowiedzi (pomijam smieci)
        #print(resources)                                       # pokaz mi co jest w odpowiedzi
    except:
        print("nie moglem pobrac meta danych")                  # anti-fuckup

    download( filename )
    os.remove(filename + '.geojson')
    os.remove(filename + '.osm')
    os.remove(filename + '.bin')
    return ret



def generate_area(area = (51.062753, 17.01, 51.059165, 17.022017)):
    n = int(math.ceil(abs(area[2] - area[0])/0.004))
    m = int(math.ceil(abs(area[3] - area[1])/0.004))
    print(n,m,sep=" ")
    for x in range(0, n):
        for y in range(0,m):
            generate_for((area[0] + x*0.004,area[1] + y*0.004))



generate_area()