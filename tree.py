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
  #for i in range(0, num_pages):
    #pagecontent = pdf.getPage(i).extractText()
    #content = content + pagecontent + " "
  for i in range(0, 4):
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
  # remove whitespace before name of Subclass
  while not subcontent.match(incontent[0]):
    incontent.pop(0)
  # pop subcontent id and initiate n to count how many tabs
  n = 1
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
    incontent.pop(0)
    # remove extratab if it's there 
    if not incontent[0]:
      incontent.pop(0)
    else:
      while 0<len(incontent) and incontent[0] and not (subcontent.match(incontent[0]) and subcontent.match(incontent[0]).span()[1] == len(incontent[0])):
        subclassname = subclassname + " " + incontent.pop(0)
  returnedcontent.append(subclassname.strip())
  getSubclassContents(returnedcontent, incontent, n)
  return

def getSubclassContents(returnedcontent, incontent, minindent):
  subcontentpat = "[A-Z]+\(?[0-9.A-Z]*\)?-?\(?[0-9.A-Z]*\)?"
  subcontent = re.compile(subcontentpat)
  n = 1
  while not incontent[0]:
    n = n + 1
    incontent.pop(0)
  if not subcontent.match(incontent[0]):
    returnedcontent.append(n)
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
      # remove extratab after line feed character
      if not incontent[0]:
        incontent.pop(0)
    n = 1
    while 0<len(incontent) and not incontent[0]:
      n = n + 1
      incontent.pop(0)
    if 0<len(incontent) and not (subcontent.match(incontent[0]) and subcontent.match(incontent[0]).span()[1] == len(incontent[0])):
      returnedcontent.append(n-minindent)
      nameofsubcontent = ""
      while 0<len(incontent) and incontent[0] and not (subcontent.match(incontent[0]) and subcontent.match(incontent[0]).span()[1] == len(incontent[0])) and not (incontent[0]=="Subclass" or incontent[0]=="Subclasses"):
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
  for element in separatedContent:
    print element
  return

if __name__ == '__main__': sys.exit(main(sys.argv))
