from train_generation import TrainingData, DataSampler
from auxiliary_functions import  ConvertToString, EmpiricalDist, SampleListToArray, AllBinaryStrings
from kernel_functions import KernelAllBinaryStrings
from param_init import NetworkParams
from sample_gen import BornSampler
import json
import numpy as np

from pyquil.api import get_qc

Max_qubits = 9

def PrintParamsToFile(seed):

	for qubit_index in range(2, Max_qubits):
		
		J_init, b_init, gamma_x_init, gamma_y_init = NetworkParams(qubit_index, seed)
		np.savez('data/Parameters_%iQubits.npz' % (qubit_index), J_init = J_init, b_init = b_init, gamma_x_init = gamma_x_init, gamma_y_init = gamma_y_init)

	return


#PrintParamsToFile()

def KernelDictToFile(N_qubits, N_kernel_samples, kernel_dict, kernel_choice):
	#writes kernel dictionary to file
	if (N_kernel_samples == 'infinite'):
		with open('data/%sKernel_Exact_Dict_%iQBs' % (kernel_choice[0], N_qubits), 'w') as f:
			dict_keys = kernel_dict.keys()
			dict_values = kernel_dict.values()
			k1 = [str(key) for key in dict_keys]
			print(json.dump(json.dumps(dict(zip(*[k1, dict_values])), sort_keys=True, indent=0),f))
		print(json.dumps(dict(zip(*[k1, dict_values])), sort_keys=True, indent=0))

	else:
		with open('data/%sKernel_Dict_%iQBs_%iKernelSamples' % (kernel_choice[0], N_qubits, N_kernel_samples), 'w') as f:
			dict_keys = kernel_dict.keys()
			dict_values = kernel_dict.values()
			k1 = [str(key) for key in dict_keys]
			print(json.dump(json.dumps(dict(zip(*[k1, dict_values])), sort_keys=True),f))
		print(json.dumps(dict(zip(*[k1, dict_values])), sort_keys=True, indent=0))

	return

def PrintKernel(N_kernel_samples, kernel_choice):
	#print the required kernel out to a file, for all binary strings
	devices = [('%iq-qvm' %N_qubits , True) for N_qubits in range(2, 7)]
	print(devices)

	for device_params in devices:
		device_name = device_params[0]
		as_qvm_value = device_params[1]

		qc = get_qc(device_name, as_qvm = as_qvm_value)
		qubits = qc.qubits()
		N_qubits = len(qubits)
		print("This is qubit, ", N_qubits)
		binary_string_array = AllBinaryStrings(N_qubits) #all binary strings of length N_qubits
		
		#The number of samples, N_samples = infinite if the exact kernel is being computed
		kernel_approx_array, kernel_exact_array, kernel_approx_dict, kernel_exact_dict = \
			KernelAllBinaryStrings(device_params, binary_string_array,  N_kernel_samples, kernel_choice)

		KernelDictToFile(N_qubits, N_kernel_samples, kernel_approx_dict, kernel_choice)
	return

def PrintSomeKernels(kernel_type):

	print("Kernel is printing for 10 samples")
	PrintKernel(10, kernel_type)
	print("Kernel is printing for 100 samples")
	PrintKernel(100, kernel_type)
	print("Kernel is printing for 200 samples")
	PrintKernel(200, kernel_type)
	print("Kernel is printing for 500 samples")
	PrintKernel(500, kernel_type)
	print("Kernel is printing for 1000 samples")
	PrintKernel(1000, kernel_type)
	print("Kernel is printing for 2000 samples")
	PrintKernel(2000, kernel_type)
	print("Exact Kernel is Printing")
	PrintKernel('infinite', kernel_type)
	return

#Uncomment if Gaussian Kernel needed to be printed to file
# PrintSomeKernels('Gaussian')

#Uncomment if Quantum Kernel needed to be printed to file
#PrintSomeKernels('Quantum')

np.set_printoptions(threshold=np.nan)

### This function prepares data samples according to a a specified number of samples
### for all number of visible qubits up to Max_qubits, and saves them to files
def DataDictToFile(data_type, N_qubits, data_dict, N_data_samples, *args):
	#writes data dictionary to file
	if data_type == 'Classical_Data':
		if (N_data_samples == 'infinite'):
			with open('data/Classical_Data_Dict_%iQBs_Exact' % N_qubits, 'w') as f:
				json.dump(json.dumps(data_dict, sort_keys=True),f)
		else:
			with open('data/Classical_Data_Dict_%iQBs_%iSamples' % (N_qubits, N_data_samples), 'w') as f:
				json.dump(json.dumps(data_dict, sort_keys=True),f)
	elif data_type == 'Quantum_Data':
		circuit_choice = args[0]
		if (N_data_samples == 'infinite'):
			with open('data/Quantum_Data_Dict_%iQBs_Exact_%sCircuit' % (N_qubits, circuit_choice), 'w') as f:
				json.dump(json.dumps(data_dict, sort_keys=True),f)
		else:
			with open('data/Quantum_Data_Dict_%iQBs_%iSamples_%sCircuit' % (N_qubits, N_data_samples, circuit_choice), 'w') as f:
				json.dump(json.dumps(data_dict, sort_keys=True),f)

	else: raise IOError('Please enter either \'Quantum_Data\' or \'Classical_Data\' for \'data_type\' ')

	return


def PrintDataToFiles(data_type, *args):
		
		N_sample_trials = [10, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000, 6000, 8000, 10000]

		if data_type == 'Classical_Data':
			for N_qubits in range(2,7):

				#Define training data along with all binary strings on the visible and hidden variables from train_generation
				#M_h is the number of hidden Bernoulli modes in the data
				M_h = 8
				N_h = 0
				data_probs, bin_visible, bin_hidden, exact_data_dict = TrainingData(N_qubits, N_h, M_h)
		
				for N_samples in N_sample_trials:
					data_samples = DataSampler(N_qubits, N_h, M_h, N_samples, data_probs, exact_data_dict)
					np.savetxt('data/Classical_Data_%iQBs_%iSamples' % (N_qubits, N_samples), data_samples, fmt='%s')
					data_samples_list= SampleListToArray(data_samples, N_qubits)
					emp_data_dist = EmpiricalDist(data_samples_list, N_qubits)
					DataDictToFile(data_type, N_qubits, emp_data_dist, N_samples)
				#Output exact training data (not sampled)
				np.savetxt('data/Classical_Data_%iQBs_Exact' % (N_qubits), np.asarray(data_probs), fmt='%.10f')
				DataDictToFile(data_type, N_qubits, exact_data_dict, 'infinite')

		elif data_type == 'Quantum_Data':
			
			devices = args[0]
			circuit_choice = args[1]
			for device_params in devices:
				device_name = device_params[0]
				as_qvm_value = device_params[1]
				qc = get_qc(device_name, as_qvm = as_qvm_value)
				qubits = qc.qubits()
				N_qubits = len(qubits)
				for N_samples in N_sample_trials:
					#Set random seed differently to that which initialises the actual Born machine to be trained
					random_seed_for_data = 13
					N_Born_Samples = [0, N_samples] #BornSampler takes a list of sample values, the [1] entry is the important one
					circuit_params = NetworkParams(device_params, random_seed_for_data) #Initialise a fixed instance of parameters to learn.
					quantum_data_samples, quantum_probs_dict, quantum_probs_dict_exact = BornSampler(device_params, N_Born_Samples, circuit_params, circuit_choice)
					print(quantum_data_samples)
					np.savetxt('data/Quantum_Data_%iQBs_%iSamples_%sCircuit' % (N_qubits, N_samples, circuit_choice), quantum_data_samples, fmt='%s')
					DataDictToFile(data_type, N_qubits, quantum_probs_dict, N_samples, circuit_choice)
				np.savetxt('data/Quantum_Data_%iQBs_Exact_%sCircuit' % (N_qubits, circuit_choice), np.asarray(quantum_data_samples), fmt='%.10f')
				DataDictToFile(data_type, N_qubits, quantum_probs_dict_exact, 'infinite', circuit_choice)
		
		else: raise IOError('Please enter either \'Quantum_Data\' or \'Classical_Data\' for \'data_type\' ')

		return

# # #Uncomment if quantum data needs to be printed to file
# device_params = [('%iq-qvm' %N_qubits , True) for N_qubits in range(2, 6)]
# circuit_choice = 'QAOA'
# PrintDataToFiles('Quantum_Data', device_params, circuit_choice)

# Uncomment if classical data needs to be printed to file
# PrintDataToFiles('Classical_Data')

def PrintCircuitParamsToFile(random_seed, circuit_choice):
	devices = [('%iq-qvm' %N_qubits , True) for N_qubits in range(2, 7)]
	for device_params in devices:
		
		device_name = device_params[0]
		as_qvm_value = device_params[1]

		qc = get_qc(device_name, as_qvm = as_qvm_value)
		qubits = qc.qubits()
		N_qubits = len(qubits)
		circuit_params = NetworkParams(device_params, random_seed)
		np.savez('data/Parameters_%iQbs_%sCircuit_%sDevice.npz' % (N_qubits, circuit_choice, device_name),\
				 J = circuit_params['J'], b = circuit_params['b'], gamma_x = circuit_params['gamma_x'], gamma_y = circuit_params['gamma_y'])

	return

#Uncomment to print circuit parameters to file, corresponding to the data, if the data is quantum
# random_seed_for_data = 13
# PrintCircuitParamsToFile(random_seed_for_data, circuit_choice)
def PrintFinalParamsToFile(cost_func, N_epochs, loss, circuit_params, born_probs_list, empirical_probs_list, device_params, kernel_type, N_samples):
	[N_data_samples, N_born_samples, batch_size, N_kernel_samples] = N_samples
	print("The data is:             \n \
	cost function:	        %s      \n \
	chip:        	        %s      \n \
	kernel:      		    %s      \n \
	N kernel samples:       %i      \n \
	N Born Samples:         %i      \n \
	N Data samples:         %i      \n \
	Batch size:             %i      \n \
	Epochs:                 %i      " \
	%(cost_func,\
	device_params[0],\
	kernel_type,\
	N_kernel_samples,\
	N_born_samples,\
	N_data_samples,\
	batch_size,\
	N_epochs))

	for epoch in range(0, N_epochs-1):
		print('%s Loss for Epoch on Train Batch for epoch' %(cost_func), epoch ,'is:', loss[('%s'% cost_func, 'Train')][epoch], '\n')
		print('%s Loss for Epoch on Test Batch for epoch' %(cost_func), epoch ,'is:', loss[('%s'% cost_func, 'Test')][epoch], '\n')
		print('Born Exact probabilities for epoch ', epoch, 'is', born_probs_list[epoch], '\n')
		print('Born Approximate probabilities for epoch ', epoch, 'is', empirical_probs_list[epoch], '\n')
		print('The weights for Epoch', epoch ,'are :', circuit_params[('J', epoch)], '\n')
		print('The biases for Epoch', epoch ,'are :', circuit_params[('b', epoch)], '\n')
		print('The gamma_x\'s for Epoch', epoch ,'are :', circuit_params[('gamma_x', epoch)], '\n')
		print('The gamma_y\'s for Epoch', epoch ,'are :', circuit_params[('gamma_y', epoch)], '\n')

	return

def QuantumSamplesToFile(device_params, N_samples, circuit_params, circuit_choice):
	device_name = device_params[0]
	as_qvm_value = device_params[1]

	qc = get_qc(device_name, as_qvm = as_qvm_value)

	N_qubits = len()
	born_samples, born_probs_approx_dict, born_probs_exact_dict = BornSampler(device_params, N_samples, circuit_params, circuit_choice)
	np.savetxt('data/QuantumData%iQBs_%iSamples' % (N_qubits, 10), born_samples, fmt='%s')
