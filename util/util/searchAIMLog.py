#----------------------------------------------------- 
# searchAIMLog.py
#
# Created by:   Michael Kuczynski
# Created on:   14-05-2020
#
# Description: Searches the header log file of an AIM file 
#              to determine if the file is a segmented image 
#              or grayscale image.
#-----------------------------------------------------

def searchAIMLog(log):
    if 'Segmented Objects' in open(log).read() :
        return True
    elif 'Linear Attenuation' in open(log).read() :
        return False