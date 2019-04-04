 # -*- coding: utf-8 -*
import os
import sys, getopt
import xml.etree.ElementTree as ET
from PIL import Image
from xml.dom import minidom

def loadNames(filepath):
    classes = []
    for line in open(filepath, 'r'):
        classes.append(line.strip())
    print(classes)
    return classes

def convert(size, strs):
    centerX = float(strs[1])
    centerY = float(strs[2])
    rateW = float(strs[3])
    rateH = float(strs[4])
    imgW = size[0]
    imgH = size[1]

    realW = rateW*imgW
    realH = rateH*imgH
    realX = centerX*imgW
    realY = centerY*imgH

    xmin = int(realX+1-realW/2)
    ymin = int(realY+1-realH/2)
    xmax = int(realX+1+realW/2)
    ymax = int(realY+1+realH/2)

    return (xmin,ymin,xmax,ymax)

def prettyXml(filepath):
    doc=minidom.parse(filepath)
    f=open(filepath,'w',encoding='utf-8')
    #addindent表示子元素缩进，newl='\n'表示元素间换行，encoding='utf-8'表示生成的xml的编码格式（<?xml version="1.0" encoding="utf-8"?>）
    doc.writexml(f, addindent='  ', newl='\n', encoding='utf-8')



if len(sys.argv) < 4:
    print('usage: python txt2xml.py -i input_dir -o output_dir -p images_dir -n names_file')
    sys.exit(1)
#用法：
#input_dir = '/txt'  标签txt所在路径
#output_dir = '/xml'  要输出的xml文件路径
#images_dir = '/images'   txt对应图片所在文件路径
#names_file = '/.names'    数据集类名所在文件路径
try:
    options,args = getopt.getopt(sys.argv[1:],"i:o:p:n:",["input=", "output=", "images=", "names="])
except getopt.GetoptError:
    sys.exit()

for name, value in options:
    if name in ('-i', '--input'):
        input_dir = value
    if name in ('-o', '--output'):
        output_dir = value
    if name in ('-p', '--images'):
        images_dir = value
    if name in ('-n', '--names'):
        names_file = value

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

namesArray = loadNames(names_file)

txtFiles = os.listdir(input_dir)
for temp in txtFiles:
    if temp.endswith('.txt'):
        infile = os.path.join(input_dir, temp)
        print('Process: %s' % (infile))
        imgfile = os.path.join(images_dir, temp.replace('.txt', '.jpg'))
        if not os.path.exists(imgfile):
            print('Skip, no image file: %s' % (imgfile))
            continue
        img = Image.open(imgfile)
        (w, h) = img.size
        root = ET.Element('annotation')
        # skip 'folder'
        filename = ET.SubElement(root, 'filename')
        filename.text = temp.replace('.txt', '.jpg')
        path = ET.SubElement(root, 'path')
        path.text = imgfile
        source = ET.SubElement(root, 'source')
        database = ET.SubElement(source, 'database')
        database.text = 'Unknow'
        size = ET.SubElement(root, 'size')
        width = ET.SubElement(size, 'width')
        width.text = str(w)
        height = ET.SubElement(size, 'height')
        height.text = str(h)
        depth = ET.SubElement(size, 'depth')
        depth.text = '3'
        segmented = ET.SubElement(root, 'segmented')
        segmented.text = '0'

        for line in open(infile, 'r'):
            array = line.split(' ')
            nameId = int(array[0])
            obj = ET.SubElement(root, 'object')
            name = ET.SubElement(obj, 'name')
            name.text = namesArray[nameId]
            pos = ET.SubElement(obj, 'pose')
            pos.text = 'Unspecified'
            truncat = ET.SubElement(obj, 'truncated')
            truncat.text = '0'
            difficult = ET.SubElement(obj, 'difficult')
            difficult.text = '0'
            bndbox = ET.SubElement(obj, 'bndbox')

            (x_lt, y_lt, x_rb, y_rb) = convert((w, h), array)
            xmin = ET.SubElement(bndbox, 'xmin')
            ymin = ET.SubElement(bndbox, 'ymin')
            xmax = ET.SubElement(bndbox, 'xmax')
            ymax = ET.SubElement(bndbox, 'ymax')
            xmin.text = str(x_lt)
            ymin.text = str(y_lt)
            xmax.text = str(x_rb)
            ymax.text = str(y_rb)

        tree = ET.ElementTree(root)
        outfile = os.path.join(output_dir, temp.replace('.txt', '.xml'))
        tree.write(outfile)
        prettyXml(outfile)
