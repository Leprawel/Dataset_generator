from bingmaps.apiservices import LocationByPoint
import urllib.request
import json
import time

f = open("BingMapsKey.txt","r")
BingMapsKey = f.read()  # secretkey do pobrania kafelka mapy
f.close()
mapSize= "3000,3000"                    # ustawienie rozmiaru mapy do pobrania
pp=[51.10765,17.06052]             # srodek zdjecia
mapMetadata = "1"                       # flaga do pobrania metadanych

def corners(pp,width):
    a = [ pp[0]-width, pp[1]-width, pp[0]+width, pp[1]+width ]
    return str(a[0])+","+str(a[1])+","+str(a[2])+","+str(a[3])

mapArea = corners(pp,0.005)


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
    with open("img4.jpg","wb") as output:           # zapisz to co masz w pamieci do pliku (wb - writebinary)
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
    with open("meta.bin","wb") as output:           # zapisz to co masz w pamieci do pliku (wb - writebinary)
        output.write(contents)
    output.close()                                  # zamknij zapisywany plik

    mapjs = json.loads(contents)                        # odpowiedz jest formatu JSON - tutaj go parsuje
    resources = mapjs["resourceSets"][0]["resources"][0]    # przepisuje odpowiednie drzewko JSON z odpowiedzi (pomijam smieci)
    print(resources)                                    # pokaz mi co jest w odpowiedzi
except:
    print("nie moglem pobrac meta danych")              # anti-fuckup

 