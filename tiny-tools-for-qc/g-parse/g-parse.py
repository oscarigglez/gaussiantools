import csv, re, sys

f01 = r"Frequencies --"

welcomeText = "\nHello! :)\n\n"

jobOptions = """
Select the values you want to extract by typing their indexes as a string without whitespace in the order you want them. (For example: 0245)
0: Frequencies (cm-1)
1: Reduced masses
2: Force constants
3: IR intensity
4: Raman activity
5: Raman1

> """

modeOptions = """
Do you want to only extract certain modes? Type them separated by commas (For example: 13,14,15,20,30)

> """

outOptions = """
0: Write an individual file for each of the input files
1: Write a big file including data from all input files

> """

optionList = [r"Frequencies --", r"Red. masses --", r"Frc consts  --", r"IR Inten    --", r"RamAct Fr= 1--", r"Raman1 Fr= 1--"]
titles = ["Frequency", "Red. mass", "Force ct.", "IR int.", "Raman act.", "Raman1"]
abbreviations = ["freq", "rmass", "frcct", "ir", "raman", "raman1"]
outList = [0,1]

###

print(welcomeText)

while True:
    try:
        request = input(jobOptions)
        for job in request:
            optionList[int(job)]
        break
    except IndexError:
        print("Oops... Please enter only valid numbers.")

while True:
    try:
        modeString = input(modeOptions)
        customModeList = modeString.split(",")
        break
    except IndexError:
        print("Oops... Please enter only valid numbers.")

while True:
    try:
        outMode = input(outOptions)
        outList[int(outMode)]
        break
    except IndexError:
        print("Oops... Please enter only valid numbers.")
    except ValueError:
        print("Oops, do not leave this blank.")

def extract(jobID, filename, modeList):
    title = titles[jobID]
    column = [filename[:-4], title]
    regex = re.compile(optionList[int(job)] + r"((?:\ *\S+)+)")
    with open(filename, "r") as file:
        matchList = " ".join(regex.findall(file.read())).split()
    for mode in modeList:
        column.append(matchList[int(mode) - 1])
    return column

with open(sys.argv[1], "r") as file:
    if customModeList == [""]:
        modeRegex = re.compile(r"Deg. of freedom\ *(\d+)")
        modeList = list(range(int(modeRegex.search(file.read()).group(1)) + 1)[1:])
    else:
        modeList = customModeList

goFiles = sys.argv[1:]

if outMode == str(1):
    resultList = [["-", "Mode"] + list(modeList[:])]
    outFile = open("output" + ".data", "w")
    for goFile in goFiles:
        for job in request:
            resultList.append(extract(int(job), goFile, modeList))
    resultList = list(map(list, zip(*resultList)))
    for lilList in resultList:
        outFile.write(" ".join(str(x) for x in lilList) + "\n")
else:
    for goFile in goFiles:
        resultList = [["-", "Mode"] + list(modeList[:])]
        for job in request:
            resultList.append(extract(int(job), goFile, modeList))
        resultList = list(map(list, zip(*resultList)))
        outFile = open(goFile[:-4] + ".data", "w")
        for lilList in resultList:
            outFile.write(" ".join(str(x) for x in lilList) + "\n")
