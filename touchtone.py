import os
import time


def playTone(t):
    for i in t:
        print(i)
        if i == ' ':
            time.sleep(1)
        elif i == '*':
            os.system('omxplayer -o local ./assets/touchtones/STAR.mp3')
        else:
            os.system('omxplayer -o local ./assets/touchtones/' + i + '.mp3')
