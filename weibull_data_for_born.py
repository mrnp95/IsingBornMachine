import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import weibull_min
from file_operations_out import DataDictToFile

def weibull_dist(a, lam, N, bounds):
    data = weibull_min.rvs(a, loc=0, scale=lam, size=N)
    data_min = np.min(data)
    data = data - data_min
    data_max = np.max(data)
    data = data*bounds[1]/data_max
    return data

def IntegerToString(integer, N_qubits):
    '''This function converts a integer to a binary string'''
    if type(integer) is not int:
        raise TypeError('\'index\' must be an integer')
    if type(N_qubits) is not int:
        raise TypeError('\'N_qubits\' must be an integer')

    return "0" * (N_qubits-len(format(integer,'b'))) + format(integer,'b')

# Set number of qubits per data dimension as list of k qubit values[#q_0,...,#q_k-1]
num_qubits = [2]

bounds = np.array([0., float(2**num_qubits[0]-1)])

N = 2000

weibull = weibull_dist(5.,5.5,N, bounds)
weibull = np.round(weibull)
weibull = weibull[weibull<= bounds[1]]

# print(out)
np.savetxt('binary_data/weibull_dat_int.txt', weibull, fmt='%i')

elements = []
for i in range(len(weibull)):
    elements.append(IntegerToString(int(weibull[i]), 2))

print(elements)
np.savetxt('data/weibull_dat_str.txt', elements, fmt='%s')


temp = []

for i in range(int(bounds[1]+1)):
    temp += [np.sum(weibull==i)]

weibull = np.array(temp/sum(temp))
print(weibull)

if num_qubits[0] == 2:
    data_dic = {
        "00": weibull[0],
        "01": weibull[1],
        "10": weibull[2],
        "11": weibull[3]
    }
elif num_qubits[0] == 3:
    data_dic = {
        "000": weibull[0],
        "001": weibull[1],
        "010": weibull[2],
        "011": weibull[3],
        "100": weibull[4],
        "101": weibull[5],
        "110": weibull[6],
        "111": weibull[7]
    }
else:
    print("Don't be lazy and automatize this ...")

print(data_dic)

DataDictToFile(data_type="Weibull_Data", N_qubits=num_qubits[0], data_dict=data_dic, N_data_samples=N)
DataDictToFile(data_type="Weibull_Data", N_qubits=num_qubits[0], data_dict=data_dic, N_data_samples='infinite')

np.savetxt("data/weibull_exact.txt", weibull)

plt.figure(figsize=(6,5))
#plt.title("CDF")
plt.title("Weibull Original Dist.")
plt.plot(weibull,'-o', label='weibull', color='deepskyblue', linewidth=4, markersize=12)
plt.grid()
plt.xlabel('x')
plt.ylabel('p(x)')
plt.legend(loc='best')
plt.savefig('outputs/weibull_orig.png')
plt.close()