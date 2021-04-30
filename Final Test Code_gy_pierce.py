# Gretta Yener and Pierce Edit #3 million-
# 4/21/21

# Purpose: Edit setup file

# IMPORT LIBRARIES
import re, os
import xml.etree.ElementTree as ET
import subprocess
from pkg_resources import parse_version

##----------DEFINE OUT SETUP,STUDYAREA,AND FLOORPLAN, LICENSE
# DEFINE SETUP FILE
setup = 'model_apt_test1_heatmap.setup'
# DEFINE STUDYAREA FILE
studyArea = 'model_apt_test1_heatmap.X3D.xml'
# DEFINE NEW FLOORPLAN
flpName = 'newFlp(2).flp'
flpList = []
wibatchLocation = r"C:\Program Files\Remcom\Wireless InSite 3.3.3\bin\calc\wibatch.exe"
#licenseLocation is only required when running WI 3.3.4 or greater
licenseLocation = r"C:\Users\Admin\Desktop"
##------------------------------------------------------------------

##----------change working directory within python to allow users to run from anywhere (Line 16)
import pathlib
pyfiledir = pathlib.Path(__file__).parent.absolute()
os.chdir(pyfiledir)
##------------------------------------------------------------------

#DETERMINE MAX NUMBER OF RUNS (Line 91)
conductivityValues = range(1, 5)
maxRuns = len(conductivityValues)

##----------CREATE ALL COMPILED VARIABLES
flpFilenameRegex = re.compile(r"(filename\s\.?/?)(.*?)\.flp") #PATTERN IS FOR THE FLP FILE
conductivityRegex = re.compile(r"(begin_<Material>\sHRG\stest\smaterial\s2.*?begin_<DielectricLayer>\sinsulator.*?)(conductivity\s.*?\n)(.*?end_<DielectricLayer>.*?end_<Material>)",re.DOTALL)
# SEARCH IN SETUP FILE FOR STUDY AREA INFO TO VARIABLES
# LINE 54
studyAreaPlacementRegex = re.compile(r"(end_<studyarea>)\n(begin_<feature>)")
studyAreaSectionRegex = re.compile(r"begin_<studyarea>.*?end_<studyarea>", re.DOTALL)
#SEARCH IN STUDYAREA XML FILE AND SAVE INFO TO VARIABLES
studyAreaPrefixRegex = re.compile(r"remcom::rxapi::", re.DOTALL)
studyAreaRevertRegex = re.compile(r"SCRIPTPLACEHOLDER", re.DOTALL)
##------------------------------------------------------------------

#SPLIT FLOORPLAN NAMES
flpFilepath = []
flpFilepathSplit = []
flpFilenameSplit = []

##----------SPLIT FILEPATH NAMES BY THE DOT AND ADD THINGS IF NECESSARY
#SPLIT NAME OF STUDYAREA BY THE DOT 
studyAreaFilepath = os.path.basename(studyArea)
studyAreaFilepathSplit = os.path.splitext(studyArea)
studyAreaFilenameSplit = studyAreaFilepath.split(".")

#SPLIT NAME OF THE SETUP BY THE DOT, ADD "_samplename" AND CREATE NEW SETUP FILE
setupFilepath = os.path.basename(setup)
setupFilepathSplit = os.path.splitext(setup)
setupFilenameSplit = setupFilepath.split(".")
newSetupFile = setupFilenameSplit[0] + "_changingconductivity." + setupFilenameSplit[1]

#SPLIT NEW SETUP FILE NAME BY THE DOT, THEN SAVE IT
newSetupFilenameSplit = newSetupFile.split(".")
newSetupFilename = newSetupFilenameSplit[0]
##--------------------------------------------------------------------------------

#CLEAR THE CONTENTS OF THE NEW SETUP FILE
open(newSetupFile, 'w+').close()

##----------DETERMINE MAXIMUM NUMBER OF RUNS
##--------------------------------------------------------------------------------

####MODIFY FLP FILE  (this is instead of Pierce version)
flpContent = []
k = 0
while (k < maxRuns):

    flpFilenameSplit.append(flpName.split("."))

    with open(flpName) as f:
        flpContent.append(f.read())
    k +=1

#REPLACED EACH INSTANCE OF remcom::rxapi:: with SCRIPTPLACEHOLDER USING re.MULTILINE
studyAreaContent = open(studyArea)
editedStudyArea = ''
for line in studyAreaContent: #goes line by line and looks for remcom:rxapi:: and replaces it
    editedStudyArea += studyAreaPrefixRegex.sub("SCRIPTPLACEHOLDER", line, re.MULTILINE) #.sub substitutes

#-----CHANGE SETUP FILE NAME IN XML FILE AND IN SQLITE (DATABASE)
tree = ET.fromstring(editedStudyArea)

#CHANGE OUTPUT LOCATION IN XML BY GETTING WTV IS AFTER the = in Value= (In XML)
for elementOutputLocation in tree.find("SCRIPTPLACEHOLDERJob/OutputLocation"):
    initialOutputLocation = elementOutputLocation.get("Value")       

#ADD wtv is in newSetupFilename TO THE elementOutputPrefix identify files
for elementOutputPrefix in tree.find("SCRIPTPLACEHOLDERJob/OutputPrefix"):
    elementOutputPrefix.set("Value", newSetupFilename)

#PUT IN NEW NAME TO LOCATION THAT REFRENCES SQLITE DATABASE, THEN ADD BACK .sqlite file type in path
for elementDatabaseLocation in tree.find("SCRIPTPLACEHOLDERJob/PathResultsDatabase/SCRIPTPLACEHOLDERPathResultsDatabase/Filename/SCRIPTPLACEHOLDERFileDescription/Filename"):
    elementDatabaseLocation.set("Value", "./" + elementOutputLocation.get("Value") + "/" + elementOutputPrefix.get("Value") + "." + elementOutputLocation.get("Value") + ".sqlite")

# FIND THE SPECIFIC LINE FOR FLOORPLAN, <--------WILL HAVE TO WRITE THE CODE SO THAT THE NAME SPLITS AND ADD THE NEXT NUMBER
for elementFloorplanLocation in tree.find("SCRIPTPLACEHOLDERJob/Scene/SCRIPTPLACEHOLDERScene/GeometryList/SCRIPTPLACEHOLDERGeometryList/Geometry/SCRIPTPLACEHOLDERFloorPlan/GeometrySource/SCRIPTPLACEHOLDERWirelessInSiteGeometry/Filename/SCRIPTPLACEHOLDERFileDescription/Filename"):
    elementFloorplanLocation.set("Value", "./" + flpName) 

#CONVERTS XML TO A STRING TO BE PARSED MORE EASILY
treeString = ET.tostring(tree, encoding='unicode', method='xml')

#undo the modifications to the xml so that it is a valid WI study area again
editedTreeString = ""
editedTreeString += studyAreaRevertRegex.sub("remcom::rxapi::", treeString)
newStudyAreaPath = newSetupFilename + "." + studyAreaFilenameSplit[1] + studyAreaFilepathSplit[1]
initialStudyAreaPath = newStudyAreaPath #<-----WILL NEED TO USE THIS WHEN EXECUTING CODE AT END
#THEN WRITE editedTreeString, which replaced the SCRIPTHOLDER STUFF
newStudyArea = open(newStudyAreaPath, "w") #OPEN the X3D.XML FILE
newStudyArea.write(editedTreeString) #WRITES THE editedTreeString file and writes it to the newStudyArea
newStudyArea.close() 

with open(setup) as f:
    setupContent = f.read()
#-----END

# Check the version of the software to see if we need to specify the license
baseVersion = "3.3.4.2"
version = re.search('(version=\")(.{7})(\")', editedStudyArea)
newVersion = parse_version(version[2]) >= parse_version(baseVersion)


#### HERE IS CORRECT BEGINING 
# iterate each variable
i = 0
fileIndex = 1
displayIndex = 2

#START THE RUN, LET USER KNOW
while (i <= maxRuns-1):
    print("Generating run %s of %s" % (fileIndex, maxRuns)) #sub the numnber into %s fileIndex and the next %s maxruns
    j = 0 #J IS OUR ITERATING VARIABLE
    
    #LOAD XML WITH SCRIPTPLACEHOLDER
    tree = ET.fromstring(editedStudyArea) #tells to hold the info in memory so I can modify it
    outputFolder = 'outputFlpFiles'
    while (j < maxRuns-1):
        indexedflpFilepath = "./" + flpFilenameSplit[j][0] + " " + str(displayIndex) + "." + flpFilenameSplit[j][1]
        #indexed_study_area_filename = "./" + studyAreaFilenameSplit[j][0] + " " + str(displayIndex) + "." + studyAreaFilenameSplit[j][1]
        #print(indexed_study_area_filename)
        ####---------------------------JUST Call the entire function
        for line in flpContent[j]:

            #matchName = flpFilenameRegex.match(line)
            #if matchName:
                #line = re.sub(r'\1%s' %flpName + str(displayIndex), line)
            #Change the conductivity in the files
            #USER DEFINED SECTION

            for i,j in enumerate(conductivityValues):
            
                # change the conductivity values
                newFlpContents = conductivityRegex.sub(r'\1conductivity %f\n\3' %j, str(flpContent))

                # write the edited contents of the initial flp file to a new flp file
                filename = os.path.join(outputFolder, flpName.split('.')[0] + str(i) + '.flp')

                # create output folder if it doesn't exist already
                if not os.path.exists(outputFolder):
                    os.makedirs(outputFolder)

                with open(filename, 'w+') as newFile:
                    newFile.write(newFlpContents)
                    newFile.close()
            #write the edited contents of the initial flp file to a new flp file
            filename = os.path.join(outputFolder, flpName.split('.')[0] + str(i) + '.flp')

            #create output folder if it doesn't exist already
            #if not os.path.exists(outputFolder):
                #os.makedirs(outputFolder)
        ####----------------------------------------------------------------------------
        
        ####---------------------CHANGE THE NAMES AFTER VALUE IN THE XML, as well as the SQLITE DATABASE
        if j == 0:
            #change the output location by adding an index to the directory
            for elementOutputLocation in tree.find("SCRIPTPLACEHOLDERJob/OutputLocation"): #changing name of xml file in setup by incrementing name
                elementOutputLocation.set("Value", elementOutputLocation.get("Value") + " " + str(displayIndex))
            #add index to the output prefix to identify files
            for elementOutputPrefix in tree.find("SCRIPTPLACEHOLDERJob/OutputPrefix"): #changing name of setup file in xml
                elementOutputPrefix.set("Value",newSetupFilename)
            #add index to the sqlite database to identify it
            for elementDatabaseLocation in tree.find("SCRIPTPLACEHOLDERJob/PathResultsDatabase/SCRIPTPLACEHOLDERPathResultsDatabase/Filename/SCRIPTPLACEHOLDERFileDescription/Filename"):
                elementDatabaseLocation.set("Value", "./" + elementOutputLocation.get("Value")+ "/" + elementOutputPrefix.get("Value") + "." + elementOutputLocation.get("Value") + ".sqlite")
            #change the name of the flp file in XML (instead of object)
            for elementFloorplanLocation in tree.find("SCRIPTPLACEHOLDERJob/Scene/SCRIPTPLACEHOLDERScene/GeometryList/SCRIPTPLACEHOLDERGeometryList/Geometry/SCRIPTPLACEHOLDERFloorPlan/GeometrySource/SCRIPTPLACEHOLDERWirelessInSiteGeometry/Filename/SCRIPTPLACEHOLDERFileDescription/Filename"):
                elementFloorplanLocation.set("Value", "./" + flpList[i])
            
            #modify .setup to add the new study area to the project
            if j == 0:    
            #duplicate existing study area and increment index
                setupContent = re.sub(r"FirstAvailableStudyAreaNumber.+", "FirstAvailableStudyAreaNumber " + str(fileIndex), setupContent)
                match = studyAreaSectionRegex.search(setupContent)
                studyAreaMatch = "\n"+match.group(0)+"\n"
                studyAreaMatch = re.sub(r"(begin_<studyarea>.+)", r"\g<0> " + str(displayIndex), studyAreaMatch)
                studyAreaMatch = re.sub(r"(StudyAreaNumber\s)(\d+)", r"StudyAreaNumber " + str(fileIndex), studyAreaMatch)
                #insert new study area after the last one in the file
                for studyAreaPlacementBounds in studyAreaPlacementRegex.finditer(setupContent):
                    studyAreaMatchTop, studyAreaMatchBottom = studyAreaPlacementBounds.groups()
                setupContent = studyAreaPlacementRegex.sub(studyAreaMatchTop + studyAreaMatch + studyAreaMatchBottom, setupContent)
        ####----------------------------------------------------------------------------- 
    #convert the xml to a string to be parsed
    treestring = ET.tostring(tree, encoding='unicode', method='xml')
    
    
    #undo the modifications to the xml so that it is a valid WI study area again
    editedTreestring = ""
    editedTreestring += studyAreaRevertRegex.sub("remcom::rxapi::", treestring) #there is also uppercase treestring, remmcom::rxapi is in x3d file,
    
    #save the new study area to a new file
    newStudyAreaPath = newSetupFilename + "." + studyAreaFilenameSplit[1] + " " + str(displayIndex) + studyAreaFilepathSplit[1]
    newStudyArea = open(newStudyAreaPath, "w")
    newStudyArea.write(editedTreestring)
    newStudyArea.close()
    i += 1
    fileIndex += 1
    displayIndex += 1

    #delete any existing cache files to prevent them from being used.
    projectFiles = os.listdir(os.getcwd())
    for file in projectFiles:
        if file.endswith(".cache"):
            os.remove(file)

    #use regex to replace lines 41-45 for ex, by subbing, use the regex that says find feature only one time, then it will not copy over other later instances
    #run simulation
    wibatch = "wibatch.exe"
    #run initial simulation first time through
    if i == 1:
        cmdFileInput = " -f " + (f'"{initialStudyAreaPath}"') #Then put in batch process, #good
        cmdFileOutput = " -out " + (f'"{studyAreaFilenameSplit[1]}"') #good
        if newVersion:
            cmdFileLicense = " -set_licenses " + licenseLocation
            commandLine = wibatch + cmdFileInput + cmdFileOutput + cmdFileLicense
        else:
            commandLine = wibatch + cmdFileInput + cmdFileOutput
            print("Running initial position simulation")
        #    print(commandLine)
        #    print(commandLine + " " + wibatchLocation)
            subprocess.run(commandLine, executable=wibatchLocation)
    newStudyAreaNameSplit = newStudyArea.name.split(".") #good
    cmdFileInput = " -f " + (f'"{newStudyArea.name}"')
    cmdFileOutput = " -out " + (f'"{newStudyAreaNameSplit[1]}"')
    if newVersion:
        cmdFileLicense = " -set_licenses " + licenseLocation
        commandLine = wibatch + cmdFileInput + cmdFileOutput + cmdFileLicense
    else:
        commandLine = wibatch + cmdFileInput + cmdFileOutput
    print(commandLine)
    subprocess.run(commandLine, executable=wibatchLocation)

# split into two functions to isolate moving parts
# function that creates new study areas

# function that modifies setup file to include new study areas



# Split REMCOM code into parts:
# Part 1: create new study area and setup files
# Part 2: Run simulations

# Delete cache files
# Run simulation

#write out the modified setup file
outSetup = open(newSetupFile,'w')
outSetup.writelines(setupContent)
outSetup.close()
print("Created new setup file " + newSetupFile )