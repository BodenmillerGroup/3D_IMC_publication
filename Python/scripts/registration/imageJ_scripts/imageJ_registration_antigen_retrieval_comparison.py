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


def image_filepath_for_3D_stack_csvfile_order(img_folder, csv_dict):
    img_list = []
    channel_files = os.listdir(img_folder)
    channel_files = get_folder_order_from_file(img_folder,csv_dict)
    for file in channel_files:
        img_path = os.path.join(img_folder,file)
        img_list.append(img_path)
        
    return img_list

def get_folder_order_from_file(stack_dir, csv_dict):
    list_len = len(csv_dict)
    stack_list = [None] *list_len
    files_dir = os.listdir(stack_dir)
    
    for item in files_dir:
        order_index = csv_dict[item]
        stack_list[order_index] = item

    return stack_list

 
#-----Initialize input & output folders 
# add code to read parameter values from a text file
# source directory with your data where all the input subfolders will be present and output folders created
data_dir_base = '~/Antigen_retrieval_comparison/s4_80C/' #make sure to end with '/' for string concatenation

stack_single_channel_tiff_folder = data_dir_base + '3Dstack_single_channel_tiffs/'


norm_dir = data_dir_base + 'histo_equalized_singleChannel_registration_images/'

# output directory
target_dir_base = data_dir_base + '3D_registred_tiffs/singleChanelRegistration/imagJ_singleChanelRegistration/'
# transforms directory
transf_dir_base = data_dir_base + 'xml_transformMatrix_imageJ/'

# final csv with file order after images that required stitching were merged
stack3d_order = data_dir_base + 'final_3D_stack_order.csv'

final3d_order = {}
reader = csv.reader(open(stack3d_order, 'r'))    
for k,v in reader:
    v= int(v)
    final3d_order[k] = v



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
p.maxEpsilon = 10 #previous 60==>1, 20 ==>2, 10==>3, 5==>4, 1==>5 (mostly failed), 3==>6
#Closest/next neighbor distance ratio:
p.rod = 0.86

#Implemented transformation models for choice 0=TRANSLATION, 1=RIGID, 2=SIMILARITY, 3=AFFINE, 4=ELASTIC, 5=MOVING_LEAST_SQUARES
p.registrationModelIndex = 2


 #--------------------First read the images into virtual stack -------------
 #-------------------------------------------------------------------------- 
#__Cd112 __Dy161 __Dy162 __Dy163 __Dy164 __Er166 __Er167 __Er168
#__Eu151 __Eu153 __Gd156 __Gd158 __Gd160 __Ho165 __In113 __In115
#__Ir191 __Ir193 __Lu175 __Nd142 __Nd145 __Nd146 __Nd148 __Nd150
#__Pr141 __Sm147 __Sm149 __Sm152 __Sm154 __Tb159 __Yb171 __Yb172 __Yb174 __Yb176


metal_list = ["Cd111"] #"Cd111","Cd112","In113","In115","Cd116","Pr141","Nd142","Nd143","Nd144","Nd146","Sm147","Nd148","Sm149","Nd150","Eu151","Sm152","Eu153","Sm154","Gd156","Gd158","Dy161","Dy162","Dy163","Dy164","Ho165","Er167","Er168","Tm169","Er170","Yb171","Yb172","Yb173","Yb174","Lu175","Yb176",]
#rename type and run for each try for saving paramters:
registration_run =10
registration_type='SIMILARITY'

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
	sorted_dir = get_folder_order_from_file(stack_single_channel_tiff_folder,final3d_order)
	
	i = 0
	files_in_dir = []
	names_in_dir = []
	for e in sorted_dir: 
	  channel_dir = os.path.join(stack_single_channel_tiff_folder,e)
	  channel_files = os.listdir(channel_dir)
	  channel = [x for x in channel_files if metal_name in x]
	  
	  if len(channel)== 1:
	   if i == 0:
	      reference_name = channel[0]
	      reference_folder = channel_dir
	      
	      
	   channel_full = os.path.join(channel_dir, channel[0]) 
	   files_in_dir.append(channel_full)
	   names_in_dir.append(channel[0])
	  
	  else:
	    print("Only one file per channel allowed, check if the search string is correct")
	  i= i+1
	######os.listdir(channel_dir)###################### end of the block
	
	# Read the dimensions from the first image  
	first_path = os.path.join(reference_folder, reference_name)
	
	# Read the dimensions from the first image    
	width, height = dimensionsOf(first_path)  
	
	# Create the VirtualStack without a specific ColorModel  
	# (which will be set much later upon loading any slice)  
	vstack = VirtualStack(width, height, None, "")  
	
	for e in files_in_dir:
	  vstack.addSlice(e)  
	
	 
	#----equalize histogram between images based on the reference image -------------
	if not os.path.exists(norm_dir):
	    os.mkdir(norm_dir)
	  
	  
	# Process and save every slice in targetDir :
	for i in xrange(0, vstack.size()): 
	  file_name =  names_in_dir[i]
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
	
	
