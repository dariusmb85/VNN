import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
from keras.utils import Sequence
from sklearn.model_selection import train_test_split, cross_val_score
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from collections import defaultdict
import pickle
import argparse

# Add arguments for the directory and neuron number
parser = argparse.ArgumentParser()
parser.add_argument('--directory', type=str, help='Directory name')
args = parser.parse_args()

def save_model_with_filename(model, neuron_nb, directory):
    # Create the filename using the provided directory argument
    filename = f'{directory}/rawData_{directory}_300epochs_batch1k_{neuron_nb}neurons_12layers.h5'
    # Save the model with the dynamic filename
    model.save(filename)

def create_binary_matrix(df, gene_col1, gene_col2):
    # Create a mapping of unique genes to column indices in the binary matrix
    gene_to_index = defaultdict(lambda: len(gene_to_index))
    
    data = []
    row_indices = []
    col_indices = []
    
    for i, (gene1, gene2) in enumerate(zip(df[gene_col1], df[gene_col2])):
        index1 = gene_to_index[gene1]
        index2 = gene_to_index[gene2]
        
        data.extend([1, 1])  # Add 1 to both gene1 and gene2 positions
        row_indices.extend([i, i])
        col_indices.extend([index1, index2])
        
    # Create a sparse matrix in Compressed Sparse Row (CSR) format
    binary_matrix = csr_matrix((data, (row_indices, col_indices)))
    
    # Create a DataFrame from the sparse matrix
    binary_matrix_df = pd.DataFrame.sparse.from_spmatrix(binary_matrix, columns=list(gene_to_index.keys()))
    
    return binary_matrix_df


class DataGenerator(Sequence):
    def __init__(self, x, y, batch_size, shuffle=True):
        self.x, self.y = x, y
        self.batch_size = batch_size
        self.indexes = np.arange(len(self.x))
        self.shuffle = shuffle
        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __len__(self):
        return int(np.ceil(len(self.x) / self.batch_size))

    def __getitem__(self, index):
        start_idx = index * self.batch_size
        end_idx = (index + 1) * self.batch_size
        batch_indexes = self.indexes[start_idx:end_idx]
        batch_x = self.x.iloc[batch_indexes]
        batch_y = self.y.iloc[batch_indexes]
        return batch_x, batch_y
    
    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indexes)


def split_data_generator(binary_inputs, output, test_size=0.2, batch_size=1000, shuffle=True):
    indexes = np.arange(len(binary_inputs))
    if shuffle:
        np.random.shuffle(indexes)

    start_idx = 0
    while True:
        end_idx = start_idx + batch_size
        if end_idx >= len(binary_inputs):
            break

        batch_indexes = indexes[start_idx:end_idx]
        batch_x = binary_inputs.iloc[batch_indexes]
        batch_y = output.iloc[batch_indexes]

        # Split the batch data
        x_train, x_val, y_train, y_val = train_test_split(batch_x, batch_y, test_size=test_size)

        start_idx = end_idx

        yield x_train, y_train, x_val, y_val



# Load and preprocess the data
dtypes = {'Query_allele': str, 'Array_allele': str, 'aggregated_growth_score': float, 'weighted_average_pvalue': float}
chunksize = 100000  # Adjust the chunksize based on available memory and processing capabilities

data_chunks = pd.read_csv("NxN_yeastRawData_StrainID_aggregateGrowth_weightedPval.csv", delimiter=',', dtype=dtypes, chunksize=chunksize)

# Initialize an empty list to store chunks
df_list = []

# Read and append each chunk to the list
for chunk in data_chunks:
    df_list.append(chunk)

# Concatenate all chunks into a single DataFrame
df = pd.concat(df_list, ignore_index=True)

del df_list

num_rows, num_columns = df.shape
print("Number of rows:", num_rows)
print("Number of columns:", num_columns)

# Sample data
# df = data.sample(n = 50)
df.memory_usage(deep=True).sum()

print("randomize sample observations")
df = df.sample(frac=0.5, random_state=42)

#gets first layer number of neurons based on total number of alleles
neuron_nb = len(set(df['Query_allele']).union(set(df['Array_allele'])))

print("Call function to create binary matrix for input")
binary_inputs = create_binary_matrix(df, 'Query_allele', 'Array_allele')
output = df['aggregated_growth_score']

# delete dataframe
del df

print("Split the data into training and validation sets")
data_split_generator = split_data_generator(binary_inputs, output)
x_train, y_train, x_val, y_val = next(data_split_generator)

# Define the model architecture
model = Sequential()

# Add the first layer with input dimension
model.add(Dense(neuron_nb, activation='relu', input_dim=binary_inputs.shape[1]))

# Add 10 hidden layers
for _ in range(10):
    model.add(Dense(64, activation='relu'))

# Add the final output layer
model.add(Dense(1, activation='linear'))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

print("Create data generators")
train_data_generator = DataGenerator(x_train, y_train, batch_size=1000)
val_data_generator = DataGenerator(x_val, y_val, batch_size=1000)

print("Train the model using data generators")
history = model.fit(train_data_generator, epochs=300, validation_data=val_data_generator)

# Save the history object to a file
with open('NxN/nnn_training_history.pkl', 'wb') as history_file:
    pickle.dump(history.history, history_file)

# Save validation data to a CSV file
x_val.to_csv('NxN/nnn_validation_x.csv', index=False)
y_val.to_csv('NxN/nnn_validation_y.csv', index=False)


# Evaluate the model
score = model.evaluate(val_data_generator)

# Save model
save_model_with_filename(model, neuron_nb, directory=args.directory)

# Make predictions using the trained model
predictions = model.predict(x_val)

# Plot the scores
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.show()
plt.savefig('NxN/rawData_NxN_1k_300Epoch_{neuron_nb}neurons_12layers_plot.png')

# # Perform cross-validation
# num_folds = 10  # Number of cross-validation folds
# scores = cross_val_score(model, binary_inputs, output, cv=num_folds, scoring='neg_mean_squared_error')
#
# # # Print scores
# print("Cross-validation scores:")
# print(scores)
#
# # Calculate mean and standard deviation of the scores
# mean_score = -np.mean(scores)
# std_score = np.std(scores)
#
# print(f"Mean score: {mean_score:.4f}")
# print(f"Standard deviation: {std_score:.4f}")

# Save the history object to a file
# with open('{args.directory}/nnn_training_history.pkl', 'wb') as history_file:
#     pickle.dump(history.history, history_file)
# 
# # Save validation data to a CSV file
# x_val.to_csv('{args.directory}/nnn_validation_x.csv', index=False)
# y_val.to_csv('{args.directory}/nnn_validation_y.csv', index=False)

# Plot the scores
# plt.figure(figsize=(8, 6))
# plt.plot(range(1, num_folds + 1), -scores, marker='o', linestyle='-', color='blue')
# plt.xlabel('Fold')
# plt.ylabel('Negative Mean Squared Error')
# plt.title('Cross-Validation Scores')
# plt.grid(True)

# Save the plot as an image file
# plt.savefig('cross_validation_scores.png')

# Create a scatter plot to visualize predictions vs. ground truth
# plt.scatter(y_val, predictions)
# plt.xlabel('Ground Truth')
# plt.ylabel('Predictions')
# plt.title('Predictions vs. Ground Truth')
# plt.savefig('rawData_NxN_1kbs_300Epoch_TruthVsPrediction_plot.png')
