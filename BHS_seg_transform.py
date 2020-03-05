import os
import numpy as np
import math
import argparse
import sys
import SimpleITK as sitk

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

#----------------------------------------------#
# STEP 1: Read in images
#----------------------------------------------#
Fixed_image_path = '/Users/alberta/Documents/Projects/RAMHA/RAMHA_Frontiers_Fig/RAMHA_006/RAMHA_006_06MO_MCP3_fatsat.nii'
Moving_image_path = '/Users/alberta/Documents/Projects/RAMHA/RAMHA_Frontiers_Fig/RAMHA_006/RAMHA_006_06MO_MCP3_XCT.nii'
outDirectory = '/Users/alberta/Documents/Projects/RAMHA/RAMHA_Frontiers_Fig/RAMHA_006/'
TMAT_path = sitk.ReadTransform('/Users/alberta/Documents/Projects/RAMHA/RAMHA_Frontiers_Fig/RAMHA_006/RAMHA_006_06MO_MCP3_T1_REG.tfm')

if TMAT_path.SetInverse() == False :
    print('No valuable inverse matrix')
    sys.exit(1)

# Registered MRI image and transformation matrix (MRI -> XCT image space):
Moving_to_Fixed_path = '/Users/alberta/Documents/Projects/RAMHA/RAMHA_Frontiers_Fig/RAMHA_006/RAMHA_006_06MO_MCP3_XCT_TO_MRI_REG.nii'

# Read images
print('Reading in {}'.format(Fixed_image_path))
Fixed_image = sitk.ReadImage(Fixed_image_path)

print('Reading in {}'.format(Moving_image_path))
Moving_image = sitk.ReadImage(Moving_image_path)

print('Resampling')
Image_resampled = sitk.Resample( Moving_image, Fixed_image, TMAT_path, sitk.sitkLinear, 0.0, Moving_image.GetPixelID() )

print('Writing to {}'.format(Moving_to_Fixed_path))
sitk.WriteImage(Image_resampled, Moving_to_Fixed_path)
