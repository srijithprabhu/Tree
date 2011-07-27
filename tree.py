import sys
import pyPdf
import re
from Products.orderedbtreefolder.orderedbtreefolder \
     import OrderedBTreeFolder
from Products.BTreeFolder2.BTreeFolder2 \
     import ExhaustedUniqueIdsError

def main(argv):
  convert_pdf(argv[1])

def getPDFContent(path):
  content = ""
  p = file(path, "rb")
  pdf = pyPdf.PdfFileReader(p)
  num_pages = pdf.getNumPages()
  for i in range(0, num_pages):
    pagecontent = pdf.getPage(i).extractText()
    content = content + pagecontent + " "
  return content

def getSeparatedContent(content):
  space = re.compile(" ")
  separatedcontent = space.split(content)
  contentreturned = []
  foundclass = False
  while 0<len(separatedcontent):
    if not separatedcontent[0]:
      separatedcontent.pop(0)
    else:
      if(not foundclass):
        # get CLASS and classname from document
        if(separatedcontent[0]=="CLASS"):
          contentreturned.append(separatedcontent.pop(0))
          classname = ""
          while(not separatedcontent[0]=="-"):
            separatedcontent.pop(0)
          separatedcontent.pop(0)
          while(not (separatedcontent[0]=="Subclass" or separatedcontent[0]=="Subclasses")):
            classname = classname + " " + separatedcontent.pop(0)
          contentreturned.append(classname.strip())
          foundclass = True
        else:
          # remove everything before class header
          separatedcontent.pop(0)
      else:
        # get Subclass name and subcontents
        contentreturned.append(separatedcontent.pop(0))
        getSubclass(contentreturned, separatedcontent)
  return contentreturned

def getSubclass(returnedcontent, incontent):
  subcontentpat = "[A-Z]+\(?[0-9.A-Z]*\)?-?\(?[0-9.A-Z]*\)?"
  subcontent = re.compile(subcontentpat)
  # append "Subclass" to returnedcontent
  subclassname = ""
  # pop subcontent id and initiate n to count how many tabs
  n = 0
  incontent.pop(0)
  # get total amount of indentation
  while not incontent[0]:
    incontent.pop(0)
    n = n + 1
  while (subcontent.match(incontent[0]) and subcontent.match(incontent[0]).span()[1] == len(incontent[0])):
    incontent.pop(0)
  # get subclassname until you get to a indent or subcontent id
  while incontent[0] and not (subcontent.match(incontent[0]) and subcontent.match(incontent[0]).span()[1] == len(incontent[0])):
    subclassname = subclassname + " " + incontent.pop(0)
  # remove linefeed character if it's there
  if not incontent[0]:
    if incontent[1]:
      incontent.pop(0)
      while 0<len(incontent) and incontent[0] and not (subcontent.match(incontent[0]) and subcontent.match(incontent[0]).span()[1] == len(incontent[0])):
        subclassname = subclassname + " " + incontent.pop(0)
  returnedcontent.append(subclassname.strip())
  getSubclassContents(returnedcontent, incontent, n)
  return

def getSubclassContents(returnedcontent, incontent, minindent):
  subcontentpat = "[A-Z]+\(?[0-9.A-Z]*\)?-?\(?[0-9.A-Z]*\)?"
  accronympat = "([A-Z]\.)+"
  subcontent = re.compile(subcontentpat)
  accronym = re.compile(accronympat)
  n = 1
  while not incontent[0]:
    n = n + 1
    incontent.pop(0)
  if not subcontent.match(incontent[0]):
    if (n - minindent) <=0:
      returnedcontent.append(0)
    else :
      returnedcontent.append(n-minindent)
    nameofsubcontent = ""
    while incontent[0] and not (subcontent.match(incontent[0]) and subcontent.match(incontent[0]).span()[1] == len(incontent[0])):
      nameofsubcontent = nameofsubcontent + " " + incontent.pop(0)
    # special case where "subcontent" is part of the name of the file
    if nameofsubcontent.endswith(",") or nameofsubcontent.endswith(" see"):
      nameofsubcontent = nameofsubcontent + " " + incontent.pop(0)
    returnedcontent.append(nameofsubcontent.strip())
  while 0<len(incontent) and not (incontent[0]=="Subclass" or incontent[0]=="Subclasses"):
    # remove subcontentid or linefeed character
    if (subcontent.match(incontent[0]) and subcontent.match(incontent[0]).span()[1] == len(incontent[0])):
      incontent.pop(0)
    elif not incontent[0]:
      incontent.pop(0)
      if not incontent[0]:
        incontent.pop(0)
    n = 1
    while 0<len(incontent) and not incontent[0]:
      n = n + 1
      incontent.pop(0)
    if 0<len(incontent) and not (subcontent.match(incontent[0]) and subcontent.match(incontent[0]).span()[1] == len(incontent[0])):
      if (n - minindent) <= 0:
        returnedcontent.append(0)
      else:
        returnedcontent.append(n-minindent)
      nameofsubcontent = ""
      while 0<len(incontent) and incontent[0] and (not (subcontent.match(incontent[0]) and subcontent.match(incontent[0]).span()[1] == len(incontent[0])) or accronym.match(incontent[0])) and not (incontent[0]=="Subclass" or incontent[0]=="Subclasses"):
        nameofsubcontent = nameofsubcontent + " " + incontent.pop(0)
      # special case where "subcontent" is part of the name of the folder
      if (nameofsubcontent.endswith(",") or nameofsubcontent.endswith(" see")):
        nameofsubcontent = nameofsubcontent + " " + incontent.pop(0)
      if not incontent[0]:
        if incontent[1] and not (incontent[0]=="Subclass" or incontent[0]=="Subclasses"):
          incontent.pop(0)
          while 0<len(incontent) and incontent[0] and not (subcontent.match(incontent[0]) and subcontent.match(incontent[0]).span()[1] == len(incontent[0])) and not (incontent[0]=="Subclass" or incontent[0]=="Subclasses"):
            nameofsubcontent = nameofsubcontent + " " + incontent.pop(0)
      returnedcontent.append(nameofsubcontent.strip())
  return

def convert_pdf(path):
  pdfContent = getPDFContent(path)
  separatedContent = getSeparatedContent(pdfContent)
  theclass = separatedContent.pop(0)
  classname = separatedContent.pop(0)
  classfolder = OrderedBTreeFolder(classname)
  while 0<len(separatedContent):
    appendSubclasses(classfolder, separatedContent)
  return

def appendSubclasses(classfolder, content):
  folders = []
  content.pop(0)
  subclassname = content.pop(0)
  subclassfolder = OrderedBTreeFolder(subclassname)
  print subclassname
  try:
    classfolder._setOb(subclassfolder.id, subclassfolder)
  except KeyError:
    subclassfolder = classfolder._getOb(subclassfolder.id)
  folders.append(subclassfolder)

  leveloffolder = 0
  while len(content) > 0 and not (content[0] == "Subclass" or content[0]=="Subclasses"):
    leveloffolder = content.pop(0)
    while leveloffolder>= len(folders):
      folders.append(folders[-1])
    nameoffolder = content.pop(0)
    tempfolder = OrderedBTreeFolder(nameoffolder)
    parent = folders[leveloffolder]
    parent._setOb(tempfolder.id, tempfolder)
    print " " + unicode(" " * leveloffolder) + nameoffolder
    if leveloffolder + 1 >= len(folders):
      folders.append(tempfolder)
    else:
      while leveloffolder + 1 < len(folders):
        folders[leveloffolder+1]=tempfolder
        leveloffolder = leveloffolder + 1


if __name__ == '__main__': sys.exit(main(sys.argv))
