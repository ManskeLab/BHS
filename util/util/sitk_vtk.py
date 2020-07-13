#----------------------------------------------------- 
# sitk-2-vtk.py
#
# Created by:   Michael Kuczynski
# Created on:   21-01-2020
#
# Description: Converts between SimpleITK and VTK image types
#-----------------------------------------------------
import vtk
from vtk.util.numpy_support import vtk_to_numpy

import SimpleITK as sitk

def sitk2vtk(img):
    size = list(img.GetSize())
    origin = list(img.GetOrigin())
    spacing = list(img.GetSpacing())
    ncomp = img.GetNumberOfComponentsPerPixel()

    # Cconvert the SimpleITK image to a numpy array
    rawData = sitk.GetArrayFromImage(img)

    # Send the numpy array to VTK with a vtkImageImport object
    dataImporter = vtk.vtkImageImport()
    dataImporter.SetImportVoidPointer(rawData)
    dataImporter.SetNumberOfScalarComponents(ncomp)

    # VTK expects 3-dimensional parameters
    if len(size) == 2:
        size.append(1)

    if len(origin) == 2:
        origin.append(0.0)

    if len(spacing) == 2:
        spacing.append(spacing[0])

    # Set the new VTK image's parameters
    # For some reason we need to set both the data and whole extent...?
    # Output image orientation will be lost when converting to a VTK image
    dataImporter.SetDataExtent(0, size[0]-1, 0, size[1]-1, 0, size[2]-1)
    dataImporter.SetWholeExtent(0, size[0]-1, 0, size[1]-1, 0, size[2]-1)
    dataImporter.SetDataOrigin(origin)
    dataImporter.SetDataSpacing(spacing)
    dataImporter.Update()

    vtk_image = dataImporter.GetOutput()

    # Cast the image data to VTK_SHORT so we can read it with UCT_3D
    caster = vtk.vtkImageCast()
    caster.SetInputData(vtk_image)
    caster.SetOutputScalarType(vtk.VTK_CHAR)
    caster.ReleaseDataFlagOff()
    caster.Update()

    return caster.GetOutput()


def vtk2sitk(img):
    vtk_data = img.GetPointData().GetScalars()
    numpy_data = vtk_to_numpy(vtk_data)
    dims = img.GetDimensions()
    numpy_data = numpy_data.reshape(dims[2], dims[1], dims[0])
    numpy_data = numpy_data.transpose(2, 1, 0)

    sitk_image = sitk.GetImageFromArray(numpy_data)

    return sitk_image