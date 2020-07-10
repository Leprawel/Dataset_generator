import requests
import json
import os



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
    
    with open( filename + '.txt', 'w') as f:
        for x in bboxes:
            print( '0', f'{x[0][0]:.6f}', f'{x[0][1]:.6f}',
            f'{x[1][0]:.6f}', f'{x[1][1]:.6f}', sep=" ", end="\n", file = f )
    
if __name__ == '__main__':
    download( '51.052560_17.029980' )