# IMPORTS
import os
import datetime
import json
import cv2 as cv

# FUNCTIONS

# Load the config into global variables and then start the work
def loadConfig(file):
    global conf, imgPath, vidPath
    conf = json.load(open(f"./cfg/{file}.json"))
    imgPath = f"./{conf['dirImg']}"
    vidPath = f"./{conf['dirVid']}"

    if not os.path.exists(imgPath):
        os.mkdir(imgPath)
    if not os.path.exists(vidPath):
        os.mkdir(vidPath)

    work()

# Returns true if cfgFile is found cfg folder
def checkCFG(cfgFile):
    return os.path.exists("./cfg/"+cfgFile+".json")

# A wrapper around datetimeOBJ with .strftime('%Y-%m-%d_%H_%M_%S_%f')
def getTimeNow():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S_%f')

# Adds message to frame
def addTS(frame, message):  # draw the text and timestamp on the frame
    cv.putText(frame, message, (10,
               frame.shape[0] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

# Returns contours: Did it to clean-up the code in work()
def getCnts(diff):
    gray = cv.cvtColor(diff, cv.COLOR_RGB2GRAY)
    blur = cv.GaussianBlur(gray, (5, 5), 0)
    thresh = cv.threshold(blur, 20, 255, cv.THRESH_BINARY)[1]
    dilated = cv.dilate(thresh, None, iterations=3)
    cnts, _ = cv.findContours(dilated, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    return cnts

# Returns true if there is any motion
def isMotion(cnts):
    for c in cnts:
        if cv.contourArea(c) > 36000:
            return True
    return False

def work():
    global cam
    cam = cv.VideoCapture(0)
    NMFR = conf["NMFR"]
    original = cam.read()[1]
    motionFlag = False
    cv.imwrite("./Images/original.jpeg", original)
    motionCounter = 0
    while cam.isOpened():
        print(motionCounter)
        frame = cam.read()[1]
        cnts = getCnts(cv.absdiff(original, frame))
        title = getTimeNow()

        if isMotion(cnts):
            NMFR = conf["NMFR"]
            record(frame, title)
            motionCounter+=1
            motionFlag=True
        else:
            if NMFR <=0:
                motionFlag = False
            if NMFR > 0 and motionFlag == True:
                NMFR -= 1
                record(frame, title)

        if conf["showVideo"]:
            cv.imshow("Security Feed", frame)
            key = cv.waitKey(1) & 0xFF
            if key == ord("q"):
                img2Video()
                break
        if cv.waitKey(10) == ord('q'):
            img2Video()
            break


def record(frame, title):
    folder = f"./{imgPath}/{title[0:13]}"
    if not os.path.exists(folder):
        os.mkdir(folder)
    addTS(frame, title)
    cv.imwrite(f"{imgPath}/{title[0:13]}/{title}.jpeg", frame)


def recordVideoFromFolder(folder):
    imgArray = [cv.imread(image) for image in os.listdir("./"+imgPath+"/"+folder)]
    size = (640, 480)
    print(f'./{vidPath}/{folder}.avi')
    out = cv.VideoWriter(f'./{vidPath}/{folder}.avi', cv.VideoWriter_fourcc(*'DIVX'), 15, size)

    for i in range(len(imgArray)):
        out.write(imgArray[i])
    
    out.release()


def img2Video():
    dirList = [f for f in os.listdir(imgPath) if os.path.isdir(imgPath+f)]
    for folder in dirList:
        recordVideoFromFolder(folder)


# MAIN


instructions = '''
### START
 --> To start camera and recording with default settings choose option 1

### MAKE A CONFIG FILE
 --> To make a new config file copy the contents from default("default.json") config and paste it into a new file and save that file to cfg folder with a name.

### DELETE A CONFIG FILE
 --> Just delete the file from cfg folder after closing the application

### DEFAULT CONFIG
 --> It is the default config file of the security camera

### GENERAL
 -> All the config files will be stored in the "cfg" folder.
 -> Unless any config file is deleted manually, it will stay there.
 -> To make a custom config as default, delete the default("default.json") config and rename new config as "default.json".
'''

os.system("cls")

toolName = '''
 _____                 _ _          _____ _____ _____ _____ _____ _____ 
|   __|___ ___ _ _ ___|_| |_ _ _   |     |  _  |     |   __| __  |  _  |
|__   | -_|  _| | |  _| |  _| | |  |   --|     | | | |   __|    -|     |
|_____|___|___|___|_| |_|_| |_  |  |_____|__|__|_|_|_|_____|__|__|__|__|
                            |___|                                       
                           
                             by github.com/prakharsaxena1

'''

print(f'''{toolName}\n1. Enter config file name\n2. Start with default config\n3. Help\n4. Exit\n''')

# Globals
conf = None
imgPath = None
vidPath = None
cam = None

# Input option to use Security Camera
option = input("Choose option (number): ")


if option == "1":
    configName = input("Config name(Full path): ")
    if checkCFG(configName):
        print("Config loaded successfully")
        loadConfig("default")
    else:
        print("No config found at ./cfg/")
        exit()
elif option == "2":
    print("Starting with default config")
    if checkCFG("default"):
        loadConfig("default")
    else:
        print("No config found at ./cfg/")
        exit()
elif option == "3":
    cam.release()
    os.system("cls")
    print(f'''          
 _____ _____ __    _____ 
|  |  |   __|  |  |  _  |
|     |   __|  |__|   __|
|__|__|_____|_____|__|    
          {instructions}''')
elif option == "4":
    print('''          
         _ _   _            _____                 _ _          _____ _____ _____ _____ _____ _____       
 ___ _ _|_| |_|_|___ ___   |   __|___ ___ _ _ ___|_| |_ _ _   |     |  _  |     |   __| __  |  _  |      
| -_|_'_| |  _| |   | . |  |__   | -_|  _| | |  _| |  _| | |  |   --|     | | | |   __|    -|     |_ _ _ 
|___|_,_|_|_| |_|_|_|_  |  |_____|___|___|___|_| |_|_| |_  |  |_____|__|__|_|_|_|_____|__|__|__|__|_|_|_|
                    |___|                              |___|                                             
                                    by github.com/prakharsaxena1
''')
    cam.release()
    exit()
else:
    print("Wrong option")
