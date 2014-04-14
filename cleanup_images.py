import os
import re
import sys

projectRoot = sys.argv[1]
imageNamedRegex = re.compile('Named:@"([^"]+)"')
resourceRegEx = re.compile('<image name="([^<]+)" width=')
plistResourceRegEx = re.compile('<string>([^<]+)</string>')

def rootImageName(imageName):
    imageName = re.sub('.png$', '', imageName)
    imageName = re.sub('~ipad$', '', imageName)
    imageName = re.sub('@2x$', '', imageName)
    return imageName

files = list(os.path.join(root, file) for root, dirs, files in os.walk(projectRoot) for file in files)
headerOrMethodFiles = list(file for file in files if file.endswith('.h') or file.endswith('.m'))
lines = (line for file in headerOrMethodFiles for line in open(file))
imagesFromCode = list(rootImageName(find) for line in lines for find in imageNamedRegex.findall(line) if find)

nibFiles = (file for file in files if file.endswith('.xib'))
lines = (line for file in nibFiles for line in open(file))
imagesFromNib = list(rootImageName(find) for line in lines for find in resourceRegEx.findall(line) if find)

plistFiles = (file for file in files if file.endswith('.plist'))
lines = (line for file in plistFiles for line in open(file))
imagesFromPlist = list(rootImageName(find) for line in lines for find in plistResourceRegEx.findall(line) if find)

allImageNames = set(rootImageName(os.path.basename(file)) for file in files if file.endswith('.png'))
allUsedImages = set(imagesFromCode+imagesFromNib+imagesFromPlist)
unusedImages = allImageNames-allUsedImages

files = (os.path.join(root, file) for root, dirs, files in os.walk(projectRoot) for file in files)
imagesToDelete = (file for file in files if (file.endswith('.png') and rootImageName(os.path.basename(file)) in unusedImages) and 'Expression' not in file)
for image in imagesToDelete:
    deleteFile = True
    rootName = rootImageName(os.path.basename(image))
    if rootName.startswith('Default') or rootName.startswith('Icon') or rootName.startswith('default') or rootName.startswith('icon'):
        deleteFile = False
    if deleteFile:
        lines = (line for file in headerOrMethodFiles for line in open(file))
        for line in lines:
            if '@"%s' % rootName in line:
                deleteFile = False
                break
    if deleteFile:
        os.remove(image)
        print 'deleted', image
    else:
        print "kept", image