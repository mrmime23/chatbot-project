import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, Conv1D, GlobalMaxPooling1D
from sklearn.model_selection import train_test_split
from functions import read_database, label_encoding, process_text

# 1. Load and preprocess data
sentences_raw, labels_raw, all_intents = read_database('../../db.sqlite3')
for i in range(len(sentences_raw)):
    sentences_raw[i] = process_text(sentences_raw[i])

# Split the data into train and test sets
sentences_train, sentences_test, labels_train, labels_test = train_test_split(sentences_raw, labels_raw, test_size=0.3)

# 2. Tokenize the data
tokenizer = Tokenizer()
tokenizer.fit_on_texts(sentences_train)
train_sequences = tokenizer.texts_to_sequences(sentences_train)
test_sequences = tokenizer.texts_to_sequences(sentences_test)

# Pad sequences to the same length
train_padded = pad_sequences(train_sequences, maxlen=50, padding='post', truncating='post')
test_padded = pad_sequences(test_sequences, maxlen=50, padding='post', truncating='post')

# Convert labels to one-hot encoding
y_train = label_encoding(labels_train)
y_test = label_encoding(labels_test)

# 3. Create CNN model
vocab_size = len(tokenizer.word_index) + 1
embedding_dim = 100
num_labels = len(all_intents)

model = Sequential([
    Embedding(vocab_size, embedding_dim, input_length=50),
    Conv1D(128, 5, activation='relu'),
    GlobalMaxPooling1D(),
    Dense(num_labels, activation='softmax')
])

# 4. Train the model
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(train_padded, y_train, epochs=10, validation_data=(test_padded, y_test))

# 5. Save the trained model
model.save("./data/cnn_model")
