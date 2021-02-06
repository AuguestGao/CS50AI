# traffic.py notes

## Requirements
Download the [dataset](https://cdn.cs50.net/ai/2020/x/projects/5/gtsrb.zip) and move the unzipped *gtsrb* directory under *traffic* directory. 


## List of Models Tried

### base model
    - filter = 12
    - kernel = 3, 3
    - activation = relu
    - maxpooling = 2, 2
    - hidden layers
        layer 1: 128 units
    - dropout = 0
----
    - loss: 0.3871
    - acc: 0.9024 

### filter number
Paramenters in models 1 were kept the same except numfer filter, then a for loop was created to iternate filter in range 1 and 129 (not-included). The loss and accuracy were recorded during each iteration into a tuple, and all records are stored in a np.array. Two plots were created against the array (num_filter vs loss and num_filter vs acc.). The graph shows no obvious improvement to conclude more filters would yield less loss and better accuracy. In fact, the result fluctuates during the entire processes. 

### pooling size
Pooling size 2-5 were experimented, and 3 is proofed the best amonge the selected pooling iszes. 

### kernel size
Smaller kerner size has better acc, 2 seems to give the best acc among 2-5 as kernel sizes.

### Num of neuron in hidden layer
Different number (5, 10, 25, 50, 100, 150, 200, 250) of neurons are tested for 1 hidden layer. Numbers between 100-150 are shown better result than other numbers. 

## Note: re-run the same model may result differently.