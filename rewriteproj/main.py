from importlib import reload
from threading import Thread
from time import sleep

import ioService
# import 

tc = Thread(target=ioService.main)
tc.start()

# slack service, just copy the old file
#sn = Thread(target=slackNotifService.main)
#sn.start()