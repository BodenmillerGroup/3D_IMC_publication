import numpy as np
from sklearn.decomposition import PCA as sklearnPCA



def local_image_normalization_stack(im_stack, zscore = False, quant_norm = None):
	"""applies normalization to each image in a stack, each image has to to be 2D np array to calculate mean and standard deviation"""
	for i in range(im_stack.shape[0]):
		img1 = im_stack[i, :,:]

		if quant_norm is not None:
			quant_val1 = np.quantile(img1, quant_norm)
			img1 = np.clip(img1,a_min = 0,a_max = quant_val1)

		mean_img1, std_img1 = img1.mean(dtype='float64'), img1.std(dtype='float64')

		# if zcore == True then divide by st.dev, otherwise just centering
		if zscore == True: 
			img1_norm = (img1 - mean_img1) / std_img1

		else:
			img1_norm = img1 - mean_img1

		im_stack[i, :, :] = img1_norm

	return(im_stack)


def create_pseudo_image_with_pca(img):
	xdim = img.shape[2]
	ydim = img.shape[1]
	zdim = img.shape[0]

	#print(np.where(np.isnan(img)))
	img = np.nan_to_num(img)


	composite_img = np.zeros((zdim, xdim * ydim), dtype=np.float32)

	for dim in range(zdim):
		flattened_channel = img[dim, :, :]
		flattened_channel = flattened_channel.flatten()
		composite_img[dim, :] = flattened_channel
	
	sklearn_pca = sklearnPCA(n_components=1, whiten=False)
	sklearn_transf = sklearn_pca.fit_transform(composite_img.T)
	var_explained = sklearn_pca.explained_variance_ratio_
	print(var_explained)
	eigenvector = sklearn_pca.components_
	max_eigenvector = eigenvector.T
	pca_image = np.zeros([ydim, xdim])
	x = 0
	y = 0

	for x in range(xdim):
		for y in range(ydim):
			composite_pixel = np.dot(img[:, y, x], max_eigenvector)
			pca_image[y, x] = composite_pixel

	return pca_image

