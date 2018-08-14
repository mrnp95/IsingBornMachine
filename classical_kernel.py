import numpy as np
from numpy import linalg as LA


'''This function computes the classical mixture of Gaussian's kernel function between two sets of samples'''
def GaussianKernel(sample1, sample2, sigma):
	#sigma[i] are bandwidth parameters

	c = len(sigma)
	N_samples1  = sample1.shape[0]
	N_samples2  = sample2.shape[0]

	gauss_kernel = np.zeros((N_samples1, N_samples2, c))
	l2norm = np.zeros((N_samples1, N_samples2))

	for i in range(0, N_samples1):
		for j in range(0, N_samples2):
			l2norm[i , j] = LA.norm(sample1[i,:] - sample2[j, :], 2)
			for k in range(0, c):
				gauss_kernel[i,j,k] = (1/c)*np.exp(-1/(2*sigma[k])*(l2norm[i,j]**2))
	return gauss_kernel.sum(2)

def GaussianKernelExact(N_v, bin_visible, sigma):
	#sigma[i] are bandwidth parameters
	c = len(sigma)
	N_strings  = 2**N_v

	gauss_kernel_exact_contribution = np.zeros((N_strings, N_strings, c))
	l2norm = np.zeros((N_strings, N_strings))
	gauss_kernel_exact_dict = {}
	for sample1 in range(0, N_strings):
		string1 = "0" * (N_v-len(format(sample1,'b'))) + format(sample1,'b')
		for sample2 in range(0, sample1+1):
			string2 = "0" * (N_v-len(format(sample2,'b'))) + format(sample2,'b')

			l2norm[sample1 , sample2] = LA.norm(bin_visible[sample1,:] - bin_visible[sample2, :], 2)
			l2norm[sample2, sample1] = l2norm[sample1,sample2]
			gauss_kernel_exact_dict[(string1, string2)] = l2norm
			for k in range(0, c):
				gauss_kernel_exact_contribution[sample1, sample2,k] = (1/c)*np.exp(-1/(2*sigma[k])*(l2norm[sample1, sample2]**2))

			gauss_kernel_exact = gauss_kernel_exact_contribution.sum(2)
			gauss_kernel_exact_dict[(string1, string2)] = gauss_kernel_exact[sample1, sample2]
			gauss_kernel_exact_dict[(string2, string1)] = gauss_kernel_exact_dict[(string1, string2)]

	return gauss_kernel_exact, gauss_kernel_exact_dict