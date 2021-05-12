from __future__ import with_statement  
#This code assumes that one channel of IMC images is chosen for registration, 
#and sigle channel tiffs are created for that chanel.
#The files in the registration tiffs have to be in the order they appera in the 3D stack

#code adapted from https://www.ini.uzh.ch/~acardona/fiji-tutorial/

import os, sys, re
from ij import IJ, ImagePlus, VirtualStack  
from loci.formats import ChannelSeparator  
from register_virtual_stack import Register_Virtual_Stack_MT 
from ij.io import FileSaver  
import ij.ImageStack
from ij.plugin import ContrastEnhancer
import csv
from register_virtual_stack import Transform_Virtual_Stack_MT

	
# Read the dimensions of the image at path by parsing the file header only,  
# thanks to the LOCI Bioformats library  
def dimensionsOf(path):  
  fr = None  
  try:  
    fr = ChannelSeparator()  
    fr.setGroupFiles(False)  
    fr.setId(path)  
    return fr.getSizeX(), fr.getSizeY()  
  except:  
    # Print the error, if any  
    print sys.exc_info()  
  finally:  
    fr.close()  

def normalizeImage(index, file_name):
  ip1 = vstack.getProcessor(index+1) # 1-based listing of slices 
  name = vstack.getFileName(index+1)
  matcher = ContrastEnhancer()
  matcher.setUseStackHistogram(1)
  #print(name)
  #print("before")
  #stats = ip1.getStatistics()
  #print(stats.histogram)   
  matcher.equalize(ip1)
  #stats = ip1.getStatistics()
  #print("after")   
  #print(stats.histogram) 
  image = ImagePlus(name, ip1)
  image.setDefault16bitRange(16)  
  FileSaver(image).saveAsTiff(os.path.join(norm_dir, '{0:04}'.format((i+1))+'.tiff'))

def image_filepath_for_3D_stack(img_folder):
	""" This function creates full file paths for images if images can be bit sortable (make sure to check that
	images start with e.g. '001_').
	The output is a list of names that then could be used for imread function in tifffile library"""
	img_list = []
	channel_files = os.listdir(img_folder)
	channel_files = sorted(channel_files)
	for file in channel_files:
		img_path = os.path.join(img_folder,file)
		img_list.append(img_path)

	return img_list
 
#-----Initialize input & output folders 
# add code to read parameter values from a text file
# source directory with your data where all the input subfolders will be present and output folders created
data_dir_base = '~/registration_LVI_test_model/LVI_breast_cancer/' #make sure to end with '/' for string concatenation

stack_single_channel_tiff_folder = data_dir_base + 'PseudoPCA/'


norm_dir = data_dir_base + 'histo_equalized_singleChannel_registration_images/'

# output directory
target_dir_base = data_dir_base + '3D_registred_tiffs/singleChanelRegistration/imagJ_singleChanelRegistration/'
# transforms directory
transf_dir_base = data_dir_base + 'xml_transformMatrix_imageJ/'

#--------------------------Initilize registration parmeters---------------
#--------------------------------------------------------------------------
# shrinkage option (false):
use_shrinking_constraint = 0

p = Register_Virtual_Stack_MT.Param()

# The "maximum image size" :
#(By reducing the size, fine scaled features will be discarded. Increasing the size beyond that of the actual images has no effect.)
p.sift.maxOctaveSize = 1200

# The "inlier ratio":
#The ratio of the number of true matches to the number of all matches including both true and false used by RANSAC
p.minInlierRatio = 0.05  

#Implemented transformation models for choice 0=TRANSLATION, 1=RIGID, 2=SIMILARITY, 3=AFFINE:
#The expected transformation model finding inliers (i.e. correspondences or landmarks between images) in the feature extraction
p.featuresModelIndex =1

p.interpolate = 1

#Maximal allowed alignment error in pixels:
p.maxEpsilon = 20 #previous 60, 20, 10, 5, 1 (mostly failed), 3

#Closest/next neighbor distance ratio:
p.rod = 0.86

#Implemented transformation models for choice 0=TRANSLATION, 1=RIGID, 2=SIMILARITY, 3=AFFINE, 4=ELASTIC, 5=MOVING_LEAST_SQUARES
p.registrationModelIndex = 5


 #--------------------First read the images into virtual stack -------------
 #-------------------------------------------------------------------------- 

metal_list = ["pseudoPCA"]
#rename type and run for each try for saving paramters:
registration_run =20
registration_type='MLS'
reference_name = 'image1'
if not os.path.exists(transf_dir_base):
	  os.mkdir(transf_dir_base)

if not os.path.exists(target_dir_base):
	  os.mkdir(target_dir_base)
	  

for metal in metal_list:
	
	metal_name = metal
	
	transf_dir = os.path.join(transf_dir_base, registration_type+str(registration_run)+"_"+metal_name+'/')
	
	if not os.path.exists(transf_dir):
	  os.mkdir(transf_dir)
	
	########### uncomment this block for one metal registration: Add all TIFF images in source_dir as slices in vstack  
	sorted_dir = image_filepath_for_3D_stack(stack_single_channel_tiff_folder)
	
	# Read the dimensions from the first image  
	first_path = (sorted_dir[0])
	
	# Read the dimensions from the first image    
	width, height = dimensionsOf(first_path)  
	
	# Create the VirtualStack without a specific ColorModel  
	# (which will be set much later upon loading any slice)  
	vstack = VirtualStack(width, height, None, "")  
	
	for e in sorted_dir:
	  vstack.addSlice(e)  
	
	 
	#----equalize histogram between images based on the reference image -------------
	if not os.path.exists(norm_dir):
	    os.mkdir(norm_dir)
	  
	  
	# Process and save every slice in targetDir :
	for i in xrange(0, vstack.size()): 
	  file_name =  sorted_dir[i]
	  normalizeImage(i, file_name)
	  
	target_dir = os.path.join(target_dir_base, registration_type+str(registration_run)+"_"+metal_name+'/')
	
	if not os.path.exists(target_dir):
	  os.mkdir(target_dir)
	
	
	#rewrite reference name as the histogram normalization changes file names
	indexed_reference_name  = '0001.tiff'	
		
	Register_Virtual_Stack_MT.exec(norm_dir, target_dir, transf_dir,indexed_reference_name, p, use_shrinking_constraint)
	
	#save parameters of the registration
	param_file = (os.path.join(transf_dir,registration_type+str(registration_run)+"_"+metal_name+'_'+'SIFT_parameters_used.csv'))
	
	reg_params = [['maxOctaveSize',p.sift.maxOctaveSize],['minInlierRatio',p.minInlierRatio], \
					['featuresModelIndex',p.featuresModelIndex],['interpolate',p.interpolate], \
					['maxEpsilon',p.maxEpsilon], ['rod',p.rod], ['registrationModelIndex',p.registrationModelIndex], \
					['reference_name',reference_name], ['registration_channel', metal_name]]
	
	with open(param_file, 'w') as csvFile:
	    writer = csv.writer(csvFile)
	    writer.writerows(reg_params)
	    
	csvFile.close()
	
	
