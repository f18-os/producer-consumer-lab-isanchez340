import cv2
import os
import time
import threading
import base64
import queue

# Semaphore and lock for getting frames and converting
EC = threading.Lock()
ECs = threading.Semaphore(10)
ECss = threading.Semaphore(10)

# Semaphore and lock for converting and displaying
CD = threading.Lock()
CDs = threading.Semaphore(10)
CDss = threading.Semaphore(10)

# communication pipes for threads
Cframe = []
Gframe = []

frameDelay = 42

class extractF(threading.Thread):
    def __init__(self):
        super(extractF, self).__init__()

    def run(self):
        # initialize frame count
        count = 0

        # open the video clip
        clipFileName = 'clip.mp4'
        vidcap = cv2.VideoCapture(clipFileName)

        # read one frame
        success, image = vidcap.read()

        print("Extracting frame {} {} ".format(count, success))
        count += 1
        while success:
            EC.acquire()
            ECs.acquire()

            # save frame to queue
            Cframe.append(image)


            success, image = vidcap.read()
            print('Extracting frame {}'.format(count))
            count += 1
            EC.release()
            ECss.release()
        for i in range(10):
            ECss.release()


class convertG(threading.Thread):
    def __init__(self):
        super(convertG, self).__init__()

    def run(self):
        # initialize frame count
        count = 0

        while 1 == 1:
            ECss.acquire()
            CDs.acquire()

            EC.acquire()
            CD.acquire()

            if(Cframe):
                colorF = Cframe.pop()
            else:
                break

            # convert the image to grayscale
            print('Converting frame {}'.format(count))
            grayscaleFrame = cv2.cvtColor(colorF, cv2.COLOR_BGR2GRAY)

            Gframe.append(grayscaleFrame)
            count += 1

            EC.release()
            CD.release()

            ECss.release()
            CDs.release()


class displayF(threading.Thread):
    def __init__(self):
        super(displayF, self).__init__()  

    def run(self):
        # initialize frame count
        count = 0

        startTime = time.time()

        # load the frame

        while 1 == 1:
            CDss.acquire()
            CD.acquire()

            if(Gframe):
                frame = Gframe.pop()
                print("Displaying frame {}".format(count))
                cv2.imshow("Video", frame)
                # compute the amount of time that has elapsed
                # while the frame was processed
                elapsedTime = int((time.time() - startTime) * 1000)
                print("Time to process frame {} ms".format(elapsedTime))

                # determine the amount of time to wait, also
                # make sure we don't go into negative time
                timeToWait = max(1, frameDelay - elapsedTime)

                # Wait for 42 ms and check if the user wants to quit
                if cv2.waitKey(timeToWait) and 0xFF == ord("q"):
                    break

                    # get the start time for processing the next frame
                startTime = time.time()

            else:
                break

            CD.release()
            CDs.release()
        # make sure we cleanup the windows, otherwise we might end up with a mess
        cv2.destroyAllWindows()

extractFrames = extractF()
convertFrames = convertG()
displayFrames = displayF()

for i in range(10):
    ECss.acquire()
    CDss.acquire()

print("Starting thread display")
displayFrames.start()

print("Starting thread convert")
convertFrames.start()

print("Starting thread extract")
extractFrames.start()

