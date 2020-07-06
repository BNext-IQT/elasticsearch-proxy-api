"""
Module that provides a Thread to delete old records from elasticsearch
"""
import threading
import time

class OldRecordsDeletionThread(threading.Thread):
    """
    Class that implements a thread to delete the old records of elasticsearch
    """


    def __init__(self):
        threading.Thread.__init__(self, )

        print('init Thread')


    def run(self):
        print("Starting ")
        time.sleep(2)
        print('holaaaaa')
        print("Exiting ")
