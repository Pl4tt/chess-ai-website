import matplotlib.pyplot as plt


plt.figure()

print(0)
with open("output.txt", "r") as file:
    data = file.read().split("LOSS train ")
    xpoints_train = []
    ypoints_train = []
    
    for i, line in enumerate(data[1:]):
        number = line.split(" ")[0]
        # print(i, line)
        # print(line[:19])
        xpoints_train.append(i+1)
        ypoints_train.append(float(number))

with open("output.txt", "r") as file2:
    data = file2.read().split("valid ")
    xpoints_validation = []
    ypoints_validation = []
    
    for i, line in enumerate(data[1:]):
        number = line.split("\n")[0]
        # print(i, line)
        # print(line[:19])
        xpoints_validation.append(i+1)
        ypoints_validation.append(float(number))

plt.plot(xpoints_train, ypoints_train, label="training loss")
plt.plot(xpoints_validation, ypoints_validation, label="validation loss")

plt.title("training vs. validation loss")
plt.legend(loc="best")

plt.ylabel("Loss")
plt.xlabel("Epoch")
plt.savefig("training_vs_validation_loss.png")
plt.show()

