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


def get_folder_order_from_file(stack_dir, csv_dict):
    list_len = len(csv_dict)
    stack_list = [None] *list_len
    files_dir = os.listdir(stack_dir)
    
    for item in files_dir:
        order_index = csv_dict[item]
        stack_list[order_index] = item

    return stack_list

#Apply transforms from Register Virtual Stack Slices
#-----------------------------------------prepare the right data from for the parameters needed to apply transfomration----------------------------------

interpolate = 1
save_dir =None #param save_dir Directory to store transform files into (null if transformations are not saved).


#--------------------------------------Initialize input & output folders for the transformation----------------------------------------

data_dir_base = '~/3D_model201710/' #make sure to end with '/' for string concatenation
stack_single_tiff_metal_folder = data_dir_base + '3D_metal_stack_tiffs/'

transform_dir_base = data_dir_base + '3D_registred_tiffs/IMC_fullStack_registred/imageJ_registration/'
if not os.path.exists(transform_dir_base):
  os.mkdir(transform_dir_base)

#folder to keep the registration stacks metal by metal. Later with python script will rearragne the files again slice by slice
transform_dir_base = data_dir_base + '3D_registred_tiffs/IMC_fullStack_registred/imageJ_registration/Ir191_registration_evaluation/'
if not os.path.exists(transform_dir_base):
  os.mkdir(transform_dir_base)
    	 
# transforms directory
transf_dir_base = data_dir_base + 'xml_transformMatrix_imageJ/'

#needed for detecting the right order of slices
stack_single_channel_tiff_folder = data_dir_base + '3Dstack_single_channel_tiffs/'

#---------------------------------------Read in xml files containing tranfromations and apply to stack of Ir191 images-----------------------------

##DELETE IF NOT NECESSARY
# final csv with file order after images that required stitching were merged
##stack3d_order = data_dir_base + 'final_3D_stack_order.csv'
##final3d_order = {}
##reader = csv.reader(open(stack3d_order, 'r'))    
##for k,v in reader:
##    v= int(v)
##    final3d_order[k] = v
##sorted_dir_stack = get_folder_order_from_file(stack_single_channel_tiff_folder,final3d_order)
##stack_ordered = []
##for name in sorted_dir_stack:
##	stack_ordered.append(name.rstrip('ac.ome.tiff'))
#registration used


#read in stack if Ir191 images
for fol in os.listdir(stack_single_tiff_metal_folder):
	if "Ir191" in fol:
		source_dir = os.path.join(stack_single_tiff_metal_folder, fol)
		src_dir_str = str(source_dir) + "/"
		src_names = sorted(os.listdir(source_dir))
	else:
		continue
#total number of slices in the model
print("Ir191 stack:", src_names)		
stack_len = len(src_names)
print("Nr of slices in a stack:",stack_len)

 
for fol in os.listdir(transf_dir_base):
	transf_dir = os.path.join(transf_dir_base, fol+'/')
	ordered_xml =sorted(os.listdir(transf_dir))
	#read in each transformation folder one by one. Before applying transformation check that the whole stack of images have been registered (some failed)				
	#read in the transfomration matrices for the whole stack. Has to be in a list form
	
	if len(ordered_xml)<stack_len:
		print("Not full stack:",fol)
	else:
		print(fol)
		transform = list()		
		for xml in ordered_xml:
			if xml.endswith('.xml'):
				xml_file = os.path.join(transf_dir, xml)
				transform.append(Transform_Virtual_Stack_MT.readCoordinateTransform(xml_file))	
		target_dir = transform_dir_base+fol+'/'
		if not os.path.exists(target_dir):
			os.mkdir(target_dir)	
		Register_Virtual_Stack_MT.createResults(src_dir_str, src_names,target_dir,save_dir, transform, interpolate)
	
#arguments for Register_Virtual_Stack_MT.createResults:
#param source_dir Directory to read all images from, where each image is a slice in a sequence. Their names must be bit-sortable, i.e. if numbered, they must be padded with zeros.
#param sorted_file_names Array of sorted source file names.
#param target_dir Directory to store registered slices into.
#param save_dir Directory to store transform files into (null if transformations are not saved).
#param transform array of transforms for every source image (including the first one)
