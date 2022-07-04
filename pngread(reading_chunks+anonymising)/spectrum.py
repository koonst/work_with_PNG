import numpy as np
import cv2
from matplotlib import pyplot as plt
import pylab

###
###
###

def DFT(image_filename, subplotpos):
    ###
    import numpy as np
    import matplotlib.pyplot as plt
    def calculate_2dft(input):
        ft = np.fft.ifftshift(input)
        ft = np.fft.fft2(ft)
        return np.fft.fftshift(ft)
    # make DFT of image
    image = plt.imread(image_filename)
    plt.subplot(subplotpos)
    plt.imshow(image)
    plt.axis("off")

    image = image[:, :, :3].mean(axis=2)  # Convert to grayscale
    plt.set_cmap("gray")
    ft = calculate_2dft(image)       

    subplotpos = subplotpos + 1
    plt.subplot(subplotpos)
    plt.imshow(np.log(abs(ft)))
    plt.axis("off")
    plt.title("Amplitude")

    subplotpos = subplotpos + 1
    plt.subplot(subplotpos)
    plt.imshow(np.angle(ft))
    plt.axis("off")
    plt.title("Phase")

    '''# Inverse Fourier transform
    ift = np.fft.ifftshift(ft)
    ift = np.fft.ifft2(ift)
    ift = np.fft.fftshift(ift)
    ift = ift.real  # Take only the real part
    subplotpos=subplotpos+1
    plt.subplot(subplotpos)
    plt.imshow(ift)
    plt.axis("off")'''

def Colors(image_filename):
    a = 331
    img = cv2.imread(image_filename)
    b,g,r = cv2.split(img)       # get b,g,r
    rgb_img = cv2.merge([r,g,b])

    x,y,z = np.shape(img)
    red = np.zeros((x,y,z),dtype=int)
    green = np.zeros((x,y,z),dtype=int)
    blue = np.zeros((x,y,z),dtype=int)
    for i in range(0,x):
        for j in range(0,y):        
            green[i][j][1]= rgb_img[i][j][1]       
            blue[i][j][0] = rgb_img[i][j][0]
            red[i][j][2] = rgb_img[i][j][2]


    cv2.imwrite("red.png", red)
    cv2.imwrite("blue.png", blue)
    cv2.imwrite("green.png", green)

    pylab.figure(num='DFT', figsize=(8, 8))
    DFT("red.png",a)
    DFT("green.png",a+3)
    DFT("blue.png",a+6)
    plt.savefig('DFT.png')
    #plt.show()