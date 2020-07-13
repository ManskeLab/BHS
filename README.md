# BHS Image Registration

This repository contains all scripts developed for the manuscript:
***S.C. Brunet, J.J. Tse, M.T. Kuczynski, K. Engelke, S.K. Boyd, C. Barnabe, S.L. Manske. Heterogenous bone response to biologic DMARD therapies in rheumatoid arthritis patients and their relationship to functional indices. Calcif. Tissue Int. Submitted July 2020.***

Improved image registration between baseline (3-month) and follow-up (12-month) XCT-II images of the MCP joint to show trabecular bone formation and loss over 9-months. This registration is performed outside of IPL and the OpenVMS system as we can obtain more accurate results using SimpleITK.

## Requirements:

To run the ***BHS_reg.py*** script, you will need the following:
- Python 3.6.X
- SimpleITK v1.2.4

## Steps to perform image registration:
1. Transfer the 3-month and 12-month grayscale images from the UCT system to your computer using FileZilla.
    - Make sure you set your file transfer type to "Auto".
2. Convert the AIM images to MHA images using the ***fileConverter.py*** script in the ***util*** folder.
    - Note that when using this script, the original image orientation is lost when converting from AIM to any other file format!
    - Thus, if you want to compare the images created in SimpleITK to the original images stored on the UCT system, you must convert the original images to MHA and back to AIM again. This is done to ensure both images have the same orientation.
3. In IPL, segment the bone from the grayscale images and write out the segmented AIM.
    - A typical process might be (but is not limited to):
        ```
        $ ipl
                _/_/_/  _/_/_/    _/
                    _/    _/    _/  _/           Image Processing Language
                _/    _/_/_/    _/              (c) IBT/ETH Z▒rich
                _/_/_/  _/        _/_/_/_/             Scanco Medical AG
        !%
        !%      IPL Interactive Starts.     Module: Scanco Module 64-bit Version V5.42
        !%                                  Built:  Dec  2 2015, 17:16:45
        !%
        ipl> read
        -name                      [in] >
        -filename                  [default_file_name] > BHS_030_03MO_MCP2_MID.AIM

        /read
        -name                      in
        -filename                  BHS_030_03MO_MCP2_MID.AIM
        !> Reading AimVersion020

        !%  /read completed:  CPU: 00:00.16  ELAP: 00:00.17

        ipl> seg_gauss
        -input                     [in] >
        -output                    [seg] >
        -sigma                     [1.000000] > 1.2
        -support                   [2] > 2.0
        -lower_in_perm_aut_al      [300.000000] > 125
        -upper_in_perm_aut_al      [100000.000000] >
        -value_in_range            [127] >
        -unit                      [0] > 2

        /seg_gauss
        -input                     in
        -output                    seg
        -sigma                     1.200000
        -support                   2
        -lower_in_perm_aut_al      125.000000
        -upper_in_perm_aut_al      100000.000000
        -value_in_range            127
        -unit                      2
        !% If orig aim: Thresholds correspond to Lin.Att.: 0.3157 4.000 [1/cm]
        !% If orig aim: Thresholds correspond to Dens: 124.9836 6214.679 [mg HA/ccm]
        !% If orig aim: Thresholds correspond to HU: 334.2089 15905.655 [HU]
        !% Thresholds correspond to native numbers:   2586 32767
        !% Permille Threshold would be: 78.931 1000.010

        !%  /seg_gauss completed:  CPU: 00:01.59  ELAP: 00:01.60

        ipl> cl_nr_extract
        -input                     [in] > seg
        -output                    [cl] >
        -min_number                [10] > 5
        -max_number                [0] >
        -value_in_range            [127] >
        -topology                  [6] >

        /cl_nr_extract
        -input                     seg
        -output                    cl
        -min_number                5
        -max_number                0
        -value_in_range            127
        -topology                  6

        !%  Starting first scan.
        !%  Number of labels in first scan:  5254
        !%  Number of entries in equivalence table: 869545
        !%  Calculating equivalence table with code version 1
        !%  Equivalence table rearranged. Nr iterations: 4
        !%  Histogram table created.
        !%  Translation table created.
        !%  Translation table applied.

        !%  Total number of disjoint components: 2161  (2604132 voxels)
        !%  Label      1:             99.1260 %   (2581371)
        !%  Label      2:              0.0070 %   (181)
        !%  Label      3:              0.0051 %   (132)
        !%  Label      4:              0.0050 %   (131)
        !%  Label      5:              0.0050 %   (129)
        !%  Label      6 -   2161:     0.8520 %   (22188)

        !%  Generating histogram.
        !%  Extracting components.

        !%  /cl_nr_extract completed:  CPU: 00:01.05  ELAP: 00:01.05

        ipl> write
        -name                      [internal_name] > cl
        -filename                  [default_file_name] > BHS_030_03MO_MCP2_MID_SEG.AIM
        -compress_type             [bin] >
        -version_020               [true] >

        /write_v020
        -name                      cl
        -filename                  BHS_030_03MO_MCP2_MID_SEG.AIM
        -compress_type             bin
        -version_020               true

        !> Compressing image
        !> Type of data               Char       1 byte/voxel
        !> Total memory size          8.5        Mbyte
        !> Writing AimVersion020 requested...  approved.
        !> Total size on disk:        293.4      Kbyte

        !%  /write_v020 completed:  CPU: 00:00.17  ELAP: 00:00.17
        ```

4. Now, transfer these baseline and follow-up segmented images to your computer using FileZilla
5. Convert the segmented AIM images to MHA using the ***fileConverter.py*** script.
6. Run the ***BHS_reg.py*** script as follows:
    ```python
    python BHS_reg.py arg1 arg2 arg3 arg4 arg5 arg6
    ```
    - Where:
        - arg1 = The input 03MO XCT grayscale image (image path + name)
        - arg2 = The input 12MO XCT grayscale image (image path + name)
        - arg3 = The output 12MO to 03MO registered XCT grayscale image (image path + name)
        - arg4 = The input 03MO XCT segmented image (image path + name)
        - arg5 = The input 12MO XCT segmented image (image path + name)
        - arg6 = The output 12MO to 03MO registered XCT segmented image (image path + name)

