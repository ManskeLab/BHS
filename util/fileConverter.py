#----------------------------------------------------- 
# fileConverter.py
#
# Created by:   Michael Kuczynski
# Created on:   21-01-2020
#
# Modified by:          Michael Kuczynski
# Modified on:          13-07-2020
# Modification Notes:   -Modified original file converter script to only handle MHA and AIM files 
#                        for the manuscript: S.C. Brunet et al. Calcif. Tissue Int. Submitted July 2020.
#
# Description: Converts between MHA and AIM images.
#              Currently supported conversions:
#                   1. MHA to AIM
#                   2. AIM to MHA
#----------------------------------------------------- 
# USAGE:
# 1. conda activate manskelab
# 2. python fileConverter.py <inputImage.ext> <outputImage.ext>
#    OR:
#    python fileConverter.py <inputImage.ext> <outputImage.ext> -l <AIMProcessingLog.txt>
#
# Notes: 
#    -You may add another argument for AIM processing logs. If you don't provide this argument
#     when reading in an AIM, the output base file name will be used to generate the header text file.
#     When writing out an AIM, you MUST provide the processing log .TXT file.
#-----------------------------------------------------

import os
import sys
import argparse

from util.searchAIMLog import searchAIMLog
from util.sitk_vtk import sitk2vtk, vtk2sitk

import vtk
import vtkbone

import SimpleITK as sitk


def fileConverter(inputImage, outputImage, AIMProcessingLog) :
    print('******************************************************')
    print(f'CONVERTING: {inputImage} to {outputImage}')

    # Extract directory, filename, basename, and extensions from the output image
    outDirectory, outFilename = os.path.split(outputImage)
    outBasename, outExtension = os.path.splitext(outFilename)

    # Check the output file format
    if outExtension.lower() == '.mha' :
        outputImageFileName = os.path.join(outDirectory, outBasename + '.mha')
    elif outExtension.lower() == '.aim' :
        if not AIMProcessingLog or ( '.txt' not in AIMProcessingLog.lower() ):
            print()
            print('Error: A valid processing log (header) is needed to write out an AIM file.')
            sys.exit(1)
        outputImageFileName = os.path.join(outDirectory, outBasename + '.aim')
    else :
        print()
        print('Error: output file extension must be MHA or AIM')
        sys.exit(1)

    # Check if the input is a file or directory
    if os.path.isfile(inputImage) :
        # NOT DIRECTORY:
        # Extract directory, filename, basename, and extensions from the input image
        inDirectory, inFilename = os.path.split(inputImage)
        inBasename, inExtension = os.path.splitext(inFilename)

        # Setup the correct reader based on the input image extension
        if '.aim' in inExtension.lower() :

            # If the input AIM contains a version number, remove it and rename the file
            if ';' in inExtension.lower() :
                inputImageNew = inputImage.rsplit(';', 1)[0]
                os.rename(inputImage, inputImageNew)
                inputImage = inputImageNew

            # Get the processing log file extension
            procLogDir, procLogFilename = os.path.split(AIMProcessingLog.lower())
            procLogBasename, procLogExtension = os.path.splitext(procLogFilename)

            # Check to make sure the processing log file extension is valid
            # If the provided file name is not valid, create a new file based on the requested output file name
            if not AIMProcessingLog or ( procLogExtension != '.txt' ) :
                AIMProcessingLog = os.path.join(outDirectory, outBasename + '.txt')
                print('Warning: No AIM processing log file name provided or invalid file extension provided. Using default file name: ' + AIMProcessingLog)
            else :
                print('WRITING PROCESSING LOG: ' + AIMProcessingLog)   

            # Read in the AIM
            imageReader = vtkbone.vtkboneAIMReader()
            imageReader.SetFileName(inputImage)
            imageReader.DataOnCellsOff()
            imageReader.Update()
            inputHeader = imageReader.GetProcessingLog()

            # Write out the processing log as a txt file
            f = open(AIMProcessingLog, 'w')
            f.write(inputHeader)

            # Determine scalar type to use
            #   VTK_CHAR <-> D1char
            #   VTK_SHORT <-> D1short
            #   If it is of type BIT, CHAR, SIGNED CHAR, or UNSIGNED CHAR it is possible
            #   to store in a CHAR.
            inputScalarType = imageReader.GetOutput().GetScalarType()

            if (inputScalarType == vtk.VTK_BIT or inputScalarType == vtk.VTK_CHAR or
                inputScalarType == vtk.VTK_SIGNED_CHAR or
                inputScalarType == vtk.VTK_UNSIGNED_CHAR) :

                # Make sure the image will fit in the range
                #   It is possible that the chars are defined in such a way that either
                #   signed or unsigned chars don't fit inside the char. We can be safe
                #   buy checking if the image range will fit inside the VTK_CHAR
                scalarRange = imageReader.GetOutput().GetScalarRange()
                if scalarRange[0] >= vtk.VTK_SHORT_MIN and scalarRange[1] <= vtk.VTK_SHORT_MAX :
                    outputScalarType = vtk.VTK_CHAR
                else :
                    outputScalarType = vtk.VTK_SHORT
            else :
                outputScalarType = vtk.VTK_SHORT
        
            # Cast
            caster = vtk.vtkImageCast()
            caster.SetOutputScalarType(outputScalarType)
            caster.SetInputConnection(imageReader.GetOutputPort())
            caster.ReleaseDataFlagOff()
            caster.Update()

            # Get VTK and SITK images
            vtk_image = caster.GetOutput()
            sitk_image = vtk2sitk(vtk_image)

        else :
            sitk_image = sitk.ReadImage(inputImage)

    # Check if the input is a directory
    elif os.path.isdir(inputImage) :
        # DIRECTORY:
        print()
        print('Error: Please provide a valid file, not a directory!')
        sys.exit(1)

    # Setup the correct writer based on the output image extension
    if outExtension.lower() == '.mha' :
        print('WRITING IMAGE: ' + str(outputImage))
        sitk.WriteImage(sitk_image, str(outputImageFileName))

    elif outExtension.lower() == '.aim' :
        print('WRITING IMAGE: ' + str(outputImage))

        # Handle the special case of MHA to AIM to avoid crashing due to SITK to VTK conversion
        # Need to cast grayscale images to VTK_SHORT type and binary images to VTK_CHAR type to display properly on the OpenVMS system
        # Scan the AIM log file to determine if the image is segmented or grayscale
        segFile = searchAIMLog(AIMProcessingLog)

        if segFile and inExtension.lower() == '.mha' :
            img = vtk.vtkMetaImageReader()
            img.SetFileName(inputImage)
            img.Update()

            caster = vtk.vtkImageCast()
            caster.SetInputData(img.GetOutput())
            caster.SetOutputScalarType(vtk.VTK_CHAR)
            caster.ReleaseDataFlagOff()
            caster.Update()

            vtk_image = caster.GetOutput()

        elif not segFile and inExtension.lower() == '.mha':
            img = vtk.vtkMetaImageReader()
            img.SetFileName(inputImage)
            img.Update()

            caster = vtk.vtkImageCast()
            caster.SetInputData(img.GetOutput())
            caster.SetOutputScalarType(vtk.VTK_SHORT)
            caster.ReleaseDataFlagOff()
            caster.Update()

            vtk_image = caster.GetOutput()
    
        # Open the processing log for reading
        f = open(AIMProcessingLog, 'r')
        header = f.read()

        writer = vtkbone.vtkboneAIMWriter()
        writer.SetInputData(vtk_image)
        writer.SetFileName( str(outputImageFileName) )

        # Do not create a new processing log as this will add extra values that 
        # will cause problems when processing the new AIM in IPL
        writer.NewProcessingLogOff()    
        writer.SetProcessingLog(header)
        
        writer.Update() 

    print ('DONE')
    print('******************************************************')
    print()


if __name__ == '__main__' :
    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument( 'inputImage', type=str, help='The input image (path + filename)' )
    parser.add_argument( 'outputImage', type=str, help='The output image (path + filename)' )
    parser.add_argument( '-l', dest='log', type=str, default='', help='Processing log for the output AIM file (text file).' )
    args = parser.parse_args()

    inputImage = args.inputImage
    outputImage = args.outputImage
    AIMProcessingLog = args.log

    fileConverter(inputImage, outputImage, AIMProcessingLog)