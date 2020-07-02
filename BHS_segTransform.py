#----------------------------------------------------- 
# BHS_segTransform.py
#
# Created by:   Michael Kuczynski
# Created on:   05-02-2020
#
# Description: Transforms MRI image to XCT image space using a
#              transformation matrix generated from the BHS_reg.py script.
#              A linear interpolation is used.
#
#-----------------------------------------------------
# Usage: python BHS_segTransform.py arg1 arg2 arg3 arg4
#
# Where:  arg1 = The fixed (XCT) image
#         arg2 = The moving (MRI) image
#         arg3 = The output directory for the transformed image
#         arg4 = The transformation matrix (must be .tfm file)
#-----------------------------------------------------
import os
import argparse
import sys
import SimpleITK as sitk

#----------------------------------------------#
# STEP 1: Read in images
#----------------------------------------------#
# Parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument( 'fixedImagePath', type=str, help='The segmented XCT image (path + filename).' )
parser.add_argument( 'movingImagePath', type=str, help='The MRI image (path + filename).' )
parser.add_argument( 'outDirectory', type=str, help='The output directory to save the transformed image.' )
parser.add_argument( 'tmatPath', type=str, help='The transformation matrix (path + filename). Muste be a .tfm file.' )
args = parser.parse_args()

fixedImagePath = args.fixedImagePath
movingImagePath = args.movingImagePath
outDirectory = args.outDirectory
TMAT_path = args.tmatPath

fixedDirectory, fixedFilename = os.path.split( fixedImagePath )
fixedBasename, fixedExtension = os.path.splitext( fixedFilename )
movingDirectory, movingFilename = os.path.split( movingImagePath )
movingBasename, movingExtension = os.path.splitext( movingFilename )

# Make sure the transformation matrix file is .tfm
if not TMAT_path.endswith('.tfm'):
    print('Error: The transformation matrix file must be a .tfm file...')
    sys.exit(1)

# Check if the transformation matrix is invertible
if TMAT_path.SetInverse() == False :
    print('No valuable inverse matrix')
    sys.exit(1)

#----------------------------------------------#
# STEP 2: Transform image
#----------------------------------------------#
# Registered MRI image and transformation matrix (MRI -> XCT image space):
Moving_to_Fixed_path = os.path.join( outDirectory, movingBasename + '_TO_' + fixedBasename + '.nii' )

# Read images
print('Reading in {}'.format(fixedImagePath))
Fixed_image = sitk.ReadImage(fixedImagePath)

print('Reading in {}'.format(movingImagePath))
Moving_image = sitk.ReadImage( movingImagePath )

print('Resampling')
Image_resampled = sitk.Resample( Moving_image, Fixed_image, TMAT_path, sitk.sitkLinear, 0.0, Moving_image.GetPixelID() )

print('Writing to {}'.format(Moving_to_Fixed_path))
sitk.WriteImage( Image_resampled, Moving_to_Fixed_path )
