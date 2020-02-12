#----------------------------------------------------- 
# BHS_reg.py
#
# Created by:   Michael Kuczynski
# Created on:   05-02-2020
#
# Description: Perform 3 month XCT to 12 month XCT image registration for MCP joints.
#              First, an initial alignment of images is obtained by matching geometric
#              image centres. Final image alignment is obtained by optimizing the mean 
#              squares error.
#              To obtain more accurate registration of the metacarpal bone, an image mask
#              of the metacarpal is provided as input.
#
#-----------------------------------------------------
# Usage: python BHS_reg.py arg1 arg2 arg3 arg4 arg5 arg6
#
# Where:  arg1 = The input 03MO XCT grayscale image
#         arg2 = The input 12MO XCT grayscale image
#         arg3 = The registered output 12MO to 03MO XCT grayscale image
#         arg4 = The input 03MO XCT segmented image
#         arg5 = The input 12MO XCT segmented image
#         arg6 = The registered output 12MO to 03MO XCT segmented image
#
# Notes: this script should work with NIfTI images as well, but hasn't been tested.
#-----------------------------------------------------

import os
import sys
import numpy as np
import math
import argparse

import SimpleITK as sitk

#----------------------------------------------#
# STEP 1: Read in images
#----------------------------------------------#
# Parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument( 'input_03MO_gray', type=str, help='The input 03MO XCT grayscale image (path + filename)' )
parser.add_argument( 'input_12MO_gray', type=str, help='The input 12MO XCT grayscale image (path + filename)' )
parser.add_argument( 'output_12MO_to_03MO_reg', type=str, help='The registered output 12MO to 03MO XCT grayscale image (path + filename)' )
parser.add_argument( 'input_03MO_seg', type=str, help='The input 03MO XCT segmented image (path + filename)' )
parser.add_argument( 'input_12MO_seg', type=str, help='The input 12MO XCT segmented image (path + filename)' )
parser.add_argument( 'output_12MO_to_03MO_seg_reg', type=str, help='The registered output 12MO to 03MO XCT segmented image (path + filename)' )
args = parser.parse_args()

# Grayscale images
XCT_3MO_image_path = args.input_03MO_gray
XCT_12MO_image_path = args.input_12MO_gray
XCT_12MO_TO_03MO_REG_path = args.output_12MO_to_03MO_reg

# Segmented images
XCT_3MO_SEG_image_path = args.input_03MO_seg
XCT_12MO_SEG_image_path = args.input_12MO_seg
XCT_12MO_TO_03MO_SEG_REG_path = args.output_12MO_to_03MO_seg_reg

# Get the sample number from the input images
sampleNum = ( XCT_3MO_image_path.rsplit('BHS_', 1)[1] ).rsplit('_', 1)[0]

# Get the MCP joint number from the input images
mcp = ( XCT_3MO_image_path.rsplit('3MO_', 1)[1] ).rsplit('.', 1)[0]

# Get the output directory
outDirectory, outFilename = os.path.split(XCT_12MO_TO_03MO_REG_path)

# Registered 12MO image and transformation matrix (12MO -> 03MO XCT image space):
XCT_12MO_to_3MO_TMAT_path = os.path.join(outDirectory, 'BHS_' + sampleNum + '_' + mcp + '_REG.tfm')

# Read images
# 03MO
print('Reading in {}'.format(XCT_3MO_image_path))
XCT_3MO_image = sitk.ReadImage(XCT_3MO_image_path)

print('Reading in {}'.format(XCT_3MO_SEG_image_path))
XCT_3MO_SEG_image = sitk.ReadImage(XCT_3MO_SEG_image_path)

# 12MO
print('Reading in {}'.format(XCT_12MO_image_path))
XCT_12MO_image = sitk.ReadImage(XCT_12MO_image_path)

print('Reading in {}'.format(XCT_12MO_SEG_image_path))
XCT_12MO_SEG_image = sitk.ReadImage(XCT_12MO_SEG_image_path)


#----------------------------------------------#
# STEP 2: Perform landmark transformation
#----------------------------------------------#
# Set initial transform by matching geometric centres
initalTransform_12MO_to_03MO = sitk.CenteredTransformInitializer(XCT_3MO_image, XCT_12MO_image, sitk.Euler3DTransform(), sitk.CenteredTransformInitializerFilter.GEOMETRY)

#----------------------------------------------#
# STEP 3: Setup registration method
#----------------------------------------------#
# Connect all of the observers so that we can perform plotting during registration.
def command_iteration(method) :
  print( '{0:3} = {1:10.5f} : {2}'.format( method.GetOptimizerIteration(), method.GetMetricValue(), method.GetOptimizerPosition() ) )

# Set up registration (12MO -> 03MO)
reg = sitk.ImageRegistrationMethod()

# Similarity metric settings:
reg.SetMetricAsMeanSquares()
reg.SetMetricSamplingStrategy(reg.RANDOM)
reg.SetMetricSamplingPercentage(0.01)   # Make this value smaller for faster (less accurate) results 

#Set Interpolator
reg.SetInterpolator(sitk.sitkLinear)

# Optimizer settings.
reg.SetOptimizerAsPowell(numberOfIterations=500)
reg.SetOptimizerScalesFromPhysicalShift()

# Setup for the multi-resolution framework.
reg.SetShrinkFactorsPerLevel(shrinkFactors = [1, 1])
reg.SetSmoothingSigmasPerLevel(smoothingSigmas=[1.0, 0])
reg.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

reg.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(reg) )

#----------------------------------------------#
# STEP 4: Perform the registration
#----------------------------------------------#
# Register 12MO and 03MO grayscale images
# Don't optimize in-place, we would possibly like to run this cell multiple times.
reg.SetInitialTransform(initalTransform_12MO_to_03MO, inPlace=False)
print('Start registration')
finalTransform = reg.Execute( sitk.Cast(XCT_3MO_image, sitk.sitkFloat64), sitk.Cast(XCT_12MO_image, sitk.sitkFloat64) )
print('Writing to {}'.format(XCT_12MO_to_3MO_TMAT_path))
sitk.WriteTransform(finalTransform, XCT_12MO_to_3MO_TMAT_path)

#----------------------------------------------#
# STEP 5: Resample and write registered image
#----------------------------------------------#
# Resample 12MO grayscale image
print('Resampling')
XCT_12MO_resampled = sitk.Resample( XCT_12MO_image, XCT_3MO_image, finalTransform, sitk.sitkLinear, 0.0, XCT_12MO_image.GetPixelID() )

print('Writing to {}'.format(XCT_12MO_TO_03MO_REG_path))
sitk.WriteImage(XCT_12MO_resampled, XCT_12MO_TO_03MO_REG_path)


#----------------------------------------------#
# STEP 6: Transform the segmented 12MO image
#----------------------------------------------#
# Resample 12MO segmented image
print('Resampling')
XCT_12MO_SEG_resampled = sitk.Resample( XCT_12MO_SEG_image, XCT_3MO_SEG_image, finalTransform, sitk.sitkLinear, 0.0, XCT_12MO_SEG_image.GetPixelID() )

print('Writing to {}'.format(XCT_12MO_TO_03MO_SEG_REG_path))
sitk.WriteImage(XCT_12MO_SEG_resampled, XCT_12MO_TO_03MO_SEG_REG_path)