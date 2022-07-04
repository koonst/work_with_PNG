#from pickle import TRUE
#import matplotlib.image as mpimg
#from matplotlib import pyplot as plt
#import pylab
from binascii import crc32
from sys import byteorder
import xml.etree.ElementTree as ET
from lxml import etree
import zlib
from RSA import *

class PNG:

    global bytes_per_pixel
    global pub_key
    global pri_key
    global nonce
    keys = get_key()
    pub_key = keys[0]
    pri_key = keys[1]
    nonce = keys[2]

    def __init__(self, fname=None):
        self.width = 0
        self.height = 0
        self.bit_depth = 0
        self.color_type = 0
        self.chunks = []
        self.chunks2 = []
        self.pallet = []
        self.funcs = {}
        self.funcs[b'IHDR'] = self._ihdr_chunk      
        self.funcs[b'PLTE'] = self._plte_chunk
        self.funcs[b'sRGB'] = self._srgb_chunk
        self.funcs[b'gAMA'] = self._gama_chunk
        self.funcs[b'tRNS'] = self._trns_chunk
        self.funcs[b'pHYs'] = self._phys_chunk
        self.funcs[b'tEXt'] = self._text_chunk
        if fname:
            self.readwrite_png(fname)
            self.new_chunks()
            self.writenew_png('new.png')
            self.encrypt_or_decrypt('ECB_en')
            self.writenew_png('ECB_encrypted.png')
            self.encrypt_or_decrypt('ECB_de')
            self.writenew_png('ECB_decrypted.png')
            self.encrypt_or_decrypt('CTR_en')
            self.writenew_png('CTR_encrypted.png')
            self.encrypt_or_decrypt('CTR_de')
            self.writenew_png('CTR_decrypted.png')
            self.encrypt_or_decrypt('RSA_en')
            self.writenew_png('RSA_encrypted.png')
            self.encrypt_or_decrypt('RSA_de')
            self.writenew_png('RSA_decrypted.png')


    def _readwrite_chunks(self, fname, fnew):
        self.chunks.clear()
        with open(fname, 'rb') as a_file:
            #with open(fnew, 'wb') as b_file:
                
                if a_file.read(8) != b'\x89PNG\r\n\x1a\n':
                    raise Exception('Signatur error')
                #b_file.write(b'\x89PNG\r\n\x1a\n')
                print('anonymised png:')
                datl = a_file.read(4)               
                while datl != b'':
                    length = int.from_bytes(datl, 'big')
                    data = a_file.read(4 + length)
                    crcheck = a_file.read(4)
                    if int.from_bytes(crcheck, 'big') != crc32(data):
                        raise Exception('CRC Checkerror')
                    self.chunks.append([data[:4], data[4:]])

                    '''strdata = data[:4].decode("utf-8")
                    if strdata[0].isupper():
                        b_file.write(datl)
                        b_file.write(data)
                        b_file.write(crcheck)
                        print (strdata)'''                    
                    datl = a_file.read(4)  
        print()
        print()

    def _def_chunk(self, index, name, data):
        print(f' {name.decode("utf-8")} Chunk')
        _ = index
        _ = data

    def _srgb_chunk(self, index, name, data):
        print(f'- {name.decode("utf-8")} Chunk')
        choseone = {
            0: 'Perceptual',
            1: 'Relatice colorimetric',
            2: 'Saturation',
            3: 'Absolute colorimetric'
            }
        index = int.from_bytes(data, 'big')
        print(f'   Rendering intent: {choseone[index]}')

    def _gama_chunk(self, index, name, data):
        print(f'- {name.decode("utf-8")} Chunk')
        _ = index
        print(f'   Image gamma: {int.from_bytes(data, "big")}')

    def _plte_chunk(self, index, name, data):
        print(f'- {name.decode("utf-8")} Chunk')
        index = divmod(len(data), 3)
        if index[1] != 0:
            raise Exception('pallet')
        for pin in range(index[0]):
            color = data[pin * 3], data[pin * 3 + 1], data[pin * 3 + 2]
            print(f'  - #{color[0]:02X}{color[1]:02X}{color[2]:02X}')
            self.pallet.append(color)

    def _trns_chunk(self, index, name, data):
        print(f'- {name.decode("utf-8")} Chunk')
        _ = index
        length = len(data)
        if self.color_type == 0:
            if length != 2:
                raise Exception('format error')
            print(f'  - Grey sample value: {int.from_bytes(data, "big")}')
        elif self.color_type == 2:
            if length != 6:
                raise Exception('format error')
            print(f'  - R sample value: {int.from_bytes(data[0:2], "big")}')
            print(f'  - G sample value: {int.from_bytes(data[2:4], "big")}')
            print(f'  - B sample value: {int.from_bytes(data[4:6], "big")}')
        elif self.color_type == 3:
            for a_i in range(len(self.pallet)):
                _ = self.pallet[a_i]
                print(f'  - {data[a_i]:02X}(#{_[0]:02X}{_[1]:02X}{_[2]:02X})')

    def _phys_chunk(self, index, name, data):
        print(f'- {name.decode("utf-8")} Chunk')
        _ = index
        _ = data[:4], data[4:8], data[8:9]
        spec = ''
        if _[2] == b'\01':
            spec = ' px/m'
        print(f'  - Pixel per unit, X axis {int.from_bytes(_[0], "big")}'+spec)
        print(f'  - Pixel per unit, Y axis {int.from_bytes(_[1], "big")}'+spec)

    def _text_chunk(self, index, name, data):
        _ = index, name
        print(f'- {name.decode("utf-8")} Chunk')
        probablyxml = data.decode("utf-8")
        #probablyxml = '<persons><person><name>John</name></person></persons>'
        try:
            ET.fromstring(probablyxml)
            root = etree.fromstring(probablyxml)
            print(etree.tostring(root, pretty_print=True).decode())
        except ET.ParseError:
            _ = data.split(b'\x00')
            print(f'   {_[0].decode("utf-8")}: {_[1].decode("utf-8")}')

    def _ihdr_chunk(self, index, name, data):
        if index != 0:
            raise Exception('first chunk')
        _ = name
        self.width = int.from_bytes(data[:4], 'big')
        self.height = int.from_bytes(data[4:8], 'big')
        self.bit_depth = int.from_bytes(data[8:9], 'big')
        self.color_type = int.from_bytes(data[9:10], 'big')
        print('- IHDR Chunk')
        print(f'   width : {self.width}')
        print(f'   height: {self.height}')
        print(f'   bit depth: {self.bit_depth}')
        _ = {
            0: '0: Grayscale',
            2: '2: Truecolor',
            3: '3: Indexed-color',
            4: '4: Greyscale with alpha',
            6: '6: Truecolor with alpha'}
        print(f'   color type: {_[self.color_type]}')
        print(f'   compression method: {int.from_bytes(data[10:11], "big")}')
        print(f'   filter method: {int.from_bytes(data[11:12], "big")}')
        print(f'   interlace method: {int.from_bytes(data[12:13], "big")}')

        match self.bit_depth:
            case 1:
                bytes_per_pixel = 1
            case 2:
                bytes_per_pixel = 4
            case 3:
                bytes_per_pixel = 3
            case 4:
                bytes_per_pixel = 2
            case 6:
                bytes_per_pixel = 4


    def readwrite_png(self, fname):
        """Loading png image"""
        filenew = 'new.png'
        self._readwrite_chunks(fname, filenew)
        for index, chunk in enumerate(self.chunks):
            self.funcs.get(chunk[0], self._def_chunk)(index, chunk[0], chunk[1])
        print('')


    ### Creating single IDAT chunk
    ###
    ###

    def new_chunks(self):
        print('starting new_chunks')
        print('')
        global place
        place = 0
        global meet
        meet = False
        for index, chunk in enumerate(self.chunks):
            name = str(chunk[0])
            #print(name)
            #print (meet)
            #print (place)
            if name[2].isupper():
                #print(name)
                
                if name[2:6] != 'IDAT':
                    self.chunks2.append([chunk[0],chunk[1]])                    
                else:
                    if meet == False:
                        meet = True
                        self.chunks2.append([chunk[0],chunk[1]])
                    else:
                        len1 = int.from_bytes(self.chunks2[place][0], byteorder='big')
                        len2 = int.from_bytes(chunk[0], byteorder='big')
                        len3 = len1 + len2
                        chunkappend = (len3).to_bytes(4, byteorder = 'big')
                    
                        self.chunks2[place][1] += chunk[1]          
                if meet == False:
                    place += 1
            

    def encrypt_or_decrypt(self,wichis):
        data = self.chunks2[place][1]
        new_data = []
        match wichis:
            case 'ECB_en':               
                #print ('starting encrypt')                 
                for i in range (len(data)):
                    to_encrypt = int.from_bytes(data[i:i+1],'big')
                    
                    to_append = ECB_encrypt(to_encrypt, pub_key)
                    #print(f'encrypt: {to_append}')
                    new_data.append(to_append)
                self.chunks2[place][1] = b''.join(new_data)  # b'': separator
                print('ECB encrypting complete')
                print(f'ECB encrypted box length: {len(to_append)}')
            case 'ECB_de':
                #print ('starting decrypt')
                for i in range (0, len(data), 2):
                    to_decrypt = int.from_bytes(data[i:i+2],'big')
                    
                    to_append = ECB_decrypt(to_decrypt, pri_key)
                    new_data.append(to_append)
                    #print(f'decrypt: {to_append}')
                self.chunks2[place][1] = b''.join(new_data)  # b'': separator
                print('ECB decrypting complete')
                print('')
            case 'CTR_en':
                for i in range(len(data)): 
                    to_encrypt = int.from_bytes(data[i:i+1],'big')

                    to_append = CTR_encrypt(to_encrypt, pub_key, nonce, i)
                    #print(f'CTRencrypt: {to_append}')
                    new_data.append(to_append)
                self.chunks2[place][1] = b''.join(new_data)
                print('CTR encrypting complete')
                print(f'CTR encrypted box length: {len(to_append)}')
            case 'CTR_de':
                for i in range (len(data)):
                    to_decrypt = int.from_bytes(data[i:i+1],'big')
                    to_append = CTR_decrypt(to_decrypt, pub_key, nonce, i)
                    #print(f'CTRdecrypt: {to_append}')
                    new_data.append(to_append)
                self.chunks2[place][1] = b''.join(new_data)
                print('CTR decrypting complete')
                print('')
            case 'RSA_en':
                for i in range(len(data)):
                    to_encrypt = data[i:i+1]
                    to_append = RSA_encrypt(to_encrypt)
                    #print(f'length: {len(to_encrypt)}')
                    new_data.append(to_append)
                    #print(f'decrypt: {to_append}')
                self.chunks2[place][1] = b''.join(new_data)
                print('RSA encrypting complete')
                print(f'RSA encrypted box length: {len(to_append)}')
            
            case 'RSA_de':
                for i in range (0, len(data), 256):
                    to_decrypt = data[i:i+256]
                    
                    to_append = RSA_decrypt(to_decrypt)
                    new_data.append(to_append)
                    #print(f'decrypt: {to_append}')
                self.chunks2[place][1] = b''.join(new_data)
                print('RSA decrypting complete')
    ###
    ###
    ###

    def writenew_png(self,filename):
        myfile = filename
        #print (self.chunks[0][1])
        with open(myfile, 'wb') as file:
            file.write(b'\x89PNG\r\n\x1a\n')
            for chunk in enumerate(self.chunks2):
                #print (self.chunks2[1][0])
                file.write((len(chunk[1][1])).to_bytes(4, byteorder='big'))
                file.write(chunk[1][0])
                file.write(chunk[1][1])
                crcheck = chunk[1][0] + chunk[1][1]
                crc = crc32(crcheck)
                crcbyte = (crc).to_bytes(4, byteorder='big')
                file.write(crcbyte)

    
    
