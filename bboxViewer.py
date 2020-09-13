import os
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import struct

def get_image_size(fname):
    #Determine the image type of fhandle and return its size. From draco.
    with open(fname, 'rb') as fhandle:
        try:
            fhandle.seek(0) # Read 0xff next
            size = 2
            ftype = 0
            while not 0xc0 <= ftype <= 0xcf:
                fhandle.seek(size, 1)
                byte = fhandle.read(1)
                while ord(byte) == 0xff:
                    byte = fhandle.read(1)
                ftype = ord(byte)
                size = struct.unpack('>H', fhandle.read(2))[0] - 2
            # We are at a SOFn block
            fhandle.seek(1, 1)  # Skip `precision' byte.
            height, width = struct.unpack('>HH', fhandle.read(4))
        except Exception: #IGNORE:W0703
            return
        return width, height

def view( filename ):
    img = cv.imread( filename + '.jpg' )
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    size = get_image_size( filename + '.jpg' )

    with open( filename + '.txt', "r" ) as file2:
                for line in file2:
                    bbox = np.delete(np.array( line.split(" ") ), 0)
                    bbox = [ float(x) for x in bbox ]

                    cornerL = ( int(size[0] * bbox[0] - 0.5 * bbox[2] * size[0]), \
                        int(size[1] * bbox[1] - 0.5 * bbox[3] * size[1]) )
                    cornerR = ( int(size[0] * bbox[0] + 0.5 * bbox[2] * size[0]), \
                        int(size[1] * bbox[1] + 0.5 * bbox[3] * size[1]) )
                    cv.rectangle( img, cornerL, cornerR, (0,255,0), 5)
                    cv.drawMarker(img, (int(size[0]*bbox[0]), int(size[1]*bbox[1])), (255,0,0), 0, 3, 10 )
    plt.imshow(img)
    plt.show()

if __name__ == '__main__':
    #print( 'Okresl nazwe pliku:' )
    view('51.062753_17.016000')
    