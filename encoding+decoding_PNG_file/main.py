#pip install numpy
#pip install matplotlib?
#pip install beautifulsoup4
#pip install lxml
import matplotlib.image as mpimg
from spectrum import *
from chunkstry import *

#my_image = 'png_files\\new2.png'
my_image = 'png_files\\little2.png'

def shownew():
    pylab.figure(num='new.png', figsize=(8, 8))
    plt.axis("off")
    img = mpimg.imread('new.png')
    plt.imshow(img)


CHUNKS = PNG(my_image)


#DFT(my_image, 131)
#Colors(my_image)   #show DFT of color divided image (r,g,b)s
#shownew()

#plt.show()