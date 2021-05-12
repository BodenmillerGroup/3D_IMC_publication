import os, re
from tifffile import imread, imsave

def image_filepath_for_3D_stack(img_folder, tiff= True):
	""" This function creates full file paths for images if images can be bit sortable (make sure to check that
	images start with e.g. '001_').
	The output is a list of names that then could be used for imread function in tifffile library"""
	img_list = []
	channel_files = os.listdir(img_folder)
	channel_files = sorted(channel_files)
	for file in channel_files:
		if tiff == True:
			if file.endswith('.tiff') or file.endswith('.tif'):
				img_path = os.path.join(img_folder,file)
				img_list.append(img_path)
		else:
			img_path = os.path.join(img_folder,file)
			img_list.append(img_path)
	return img_list


def get_folder_order_from_file(stack_dir, csv_dict):
	"""Orders 3D stack folders according to order in the csv file. Used for single channel tiffs where each folder
	contains all the single channel tiffs for each slice in the 3d reconstruction """	
	list_len = len(csv_dict)
	stack_list = [None] * list_len
	files_dir = os.listdir(stack_dir)

	for item in files_dir:
		order_index = csv_dict[item]
		stack_list[order_index] = item

	return stack_list


def get_image_stack_for_one_channel_csv(stack_folder, target_metal, csv_dict):
	"""Get images for a chosen channel from single channel tiffs,
	read the folder order from a csv file to get the 3D stack in the right order. 
	Used for single channel tiffs where each folder contains all the single channel
	tiffs for each slice in the 3d reconstruction"""

	single_channel_list = []
	# need to sort the files in a stack:
	stack_dir = get_folder_order_from_file(stack_folder, csv_dict)

	for e in stack_dir:
		met_dir = os.path.join(stack_folder, e)
		channel_files = os.listdir(met_dir)

		channel = [x for x in channel_files if target_metal in x]

		if len(channel) == 1:
		    im_path = os.path.join(met_dir, channel[0])
		    single_channel_list.append(im_path)

		else:
		    print("Only one file per channel allowed, check if the search string is correct")

	return single_channel_list



def get_metal_list_from_single_tiffs(tiff_folder):
	files_in_dir = os.listdir(tiff_folder)
	channel_name = []
	channel_dir = os.path.join(tiff_folder, files_in_dir[0])
	channel_files = os.listdir(channel_dir)

	for entry in channel_files:
		match = split_name_metal(entry)
		metalName = match[1]
		channel_name.append(metalName)

	return channel_name

def split_name_metal(name):
    """get metal name from single channel tiff files i.e 'xxx__Yb175'"""
    match = re.search(r'^(.+)_([A-Za-z]+[0-9]+).*', name)
    if match is not None:
        return [match.group(1), match.group(2)]
    else:
        return -1

def save_image_as_stack_for_one_channel_csv(stack_folder, target_metal,output_folder, csv_dict):    
    """Get images for a chosen channel from single channel tiffs and save each image individually, 
    read the folder order from a csv file to get the 3D stack in the right order"""
    
    # need to sort the files in a stack:  
    stack_dir = get_folder_order_from_file(stack_folder,csv_dict)
    i=1
    for e in stack_dir:
        met_dir = os.path.join(stack_folder, e)
        channel_files = os.listdir(met_dir)

        channel = [x for x in channel_files if target_metal in x]

        if len(channel) == 1:
            im_path = os.path.join(met_dir, channel[0])
            #save image, read name 
            op_folder = output_folder +'/'+target_metal
            
            if not os.path.exists(op_folder):
                os.mkdir(op_folder)

            new_name= '{0:04}'.format((i))+'_'+ channel[0]
            
            img_met = imread(im_path)
            imsave(os.path.join(op_folder,new_name ), img_met, compress=False)   
            i=i+1
        else:
            print("Only one file per channel allowed, check if the search string is correct")


