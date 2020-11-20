import numpy as np
import matplotlib.pyplot as plt

lr = np.loadtxt("lr_eff_bias.txt")
print(np.shape(lr))
lr_mod = []
for i in range(len(lr[:,0])):
    lr_mod.append(np.sqrt(lr[i, 0]**2+ lr[i, 1]**2))
plt.figure()
plt.title("Effective learning rate for bias parameters in the Born Machine")
plt.xlabel("Epoch")
plt.ylabel("lr_eff")
plt.plot(lr_mod)
plt.savefig("lr_eff_bias.png")