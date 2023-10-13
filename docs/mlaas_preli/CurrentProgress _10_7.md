# Current Progress ( Mlaas_preli ) - 10/7

## 1. Testbed

Network topology: One client connected to one switch.

Data set: [pima-indians-diabetes.data.csv](https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv)

Testing detail: The client trained a DNN with the input data set above and evaluated the performance of the DNN on the same dataset after the training process is done. Also, in each round, the client will compute local gradients for each parameter and send the gradients to the switch to add on all gradients together, and the switch will send the full gradient updates to the client after it gets all local gradients. Finally, we ran the test three times for each test case.

Expected outcome: Since only one client was running, the expected accuracy should be close to the one while training the model locally. i.e. no gradients communication with the switch.

### 1.1  Characteristics of the data set

The data set contains 8 features [^1]:

1.  Number of times pregnant
2. Plasma glucose concentration at 2 hours in an oral glucose tolerance test
3. Diastolic blood pressure (mm Hg)
4. Triceps skin fold thickness (mm)
5. 2-hour serum insulin (μIU/ml)
6. Body mass index (weight in kg/(height in m)2)
7. Diabetes pedigree function
8. Age (years)

The output has 2 classes, so an instance should be labelled as 0 or 1, binary classification and roughly 760 instances in total.

### 1.2 DNN structure

The DNN has 4 layers, two of which are hidden layers and other two of which are input layer and output layer. The structure is as follows [^1]:

- The input layer has 8 input variables.
- The first hidden layer of 12 neurons, followed by a ReLU activation function.
- The second hidden layer of 8 neurons, followed by a ReLU activation function.
- The output layer of one neuron, followed by a sigmoid activation function.

Note that the number of epochs is chosen as 30 and the size of a batch is 10 due to the limited performance of a virtual machine.

## 2. Result

The program achieved an average accuracy of 67.27% compared to 67.96% without gradient communication between the switch. Consequently, the program works as we expected with at least one client.

| Description    | Round 1  | Round 2  | Round 3  |
| -------------- | -------- | -------- | -------- |
| Local Test     | 0.674479 | 0.679688 | 0.684896 |
| In-switch Test | 0.660156 | 0.667979 | 0.690104 |

## 3.  Problems

### 3.1  YouTube multiview video games dataset

When I was switching to the YouTube dataset, there is an problem making it difficult to train the DNN with the program described above. The dataset is in "sparse format"(akin to libsvm). To be precise, each instance in the dataset is described up to 13 features, but there are thousands of features in total. In this way, it is too large to convert it into the format of a dense matrices, such as the one used in the test above, to train the DNN. 

Fortunately, Pytorch has a group of class, [TORCH.SPARSE](https://pytorch.org/docs/stable/sparse.html), to handle such sparse matrices or vectors. However, as far as I know, it's better to let the DNN has the same number of input neurons as the one in the dataset, meaning that the program needs to communicate thousands of gradient values with the switch, which is inconceivable with regarding to the current implementation.

To be concrete and to make the program simple, the current implementation computes one gradient and send it out to the switch to be added on, and waits for the average gradient updates from the switch. And it will not go on processing next gradient until receiving the updates from the switch. If we want to train the DNN with the YouTube dataset, we will be facing at least two problems: 1) the program has to deal with gradient synchronization and 2) the switch cannot allocate enough space to store all gradients at once.

By the way, I tried training the DNN with fewer features( Like selecting 13 features from the first one to the 13th among all the features ) and fewer instances( Like 700 ), but the accuracy is horrible, almost close to 0%, due to incomplete training dataset. So I don't think this would help a lot.

As for the solution, either we use another simple dataset but meeting our needs, or switch to another ML model or training methods( But I have no clues about this part ) in my opinion, or introduce more complicated mechanism to handle the problems.

### 3.2 Dealing floating point

The way of dealing floating points in switch doesn't have too much negative influence on the current testing process, but it may become a major concern if more datasets are used. As we discussed before, we aim to keep a floating number as accurate as possible when converting it into a 32-bit integer passed to the switch. The simplest way of doing so is scaling a floating point number as big as possible but not overflow or underflow the range that a 32-bit integer can represent. But this also means that every floating point number may have its own scaling factor. For example, assume using 8-bit signed integer ( max: 255, min: 256 ) to roughly present a floating point number, and two numbers here: 1.113 and 100.1. We can scale 1.113 by 100 while scaling 100.1 by 1 since a scaling factor larger than 1 would make the integer presenting 100.1 overflow the upper bound, which is 255.

So the switch needs to notify all clients with the minimum scaling factor when prorogating a cumulative gradient update, This idea is possible to implement but for simplicity, I randomly chose a scaling factor equal to 10000 to do the test. We can add this feature to the program if needed, but how this idea would influence the training process or performance is unknown.

And SwtichML defines a per-packet scaling factor we discussed early. I will do more research to see how they solve the problem in detail.

## 4. Future plan after this progress report

I will test the program with a different network topology, two clients and one switch, which is close to the real-world situation, to see if the program would function properly as we expected in the example video.

---

[^1]:[Develop Your First Neural Network with PyTorch, Step by Step](https://machinelearningmastery.com/develop-your-first-neural-network-with-pytorch-step-by-step/)
