import pandas as pd
import numpy as np
from tqdm import tqdm
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.layers import Embedding, LSTM, GRU, BatchNormalization
from tensorflow.keras.utils import  to_categorical
from tensorflow.keras.engine.topology import Merge
from tensorflow.keras.layers import TimeDistributed, Lambda
from tensorflow.keras.layers import Convolution1D, GlobalAveragePooling1D
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras import  backend as K
from tensorflow.keras.advanced_activations import PReLU
from keras.preprocessing import sequence, text

data = pd.read_csv('data/quora_data.csv', sep='\t')
y = data.is_duplicate.values

tk = text.Tokenizer(nb_words=200000)

max_len = 40
tk.fit_on_texts(list(data.question1.values)+list(data.question2.values))
x1 = tk.texts_to_sequences(data.question1.values)
x1 = sequences.pad_sequences(x1, maxlen=max_len)

x2 = tk.texts_to_sequences(data.question2.values)
x2 = sequences.pad_sequences(x2, maxlen=max_len)

word_index = tk.word_index

y_train_enc = to_categorical(y)

embeddings_index = {}
f = open('data/glove.840B.300d.txt')
for line in tqdm(f):
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings[word] = coefs 

f.close()

print('Found {} word vectors'.format(len(embeddings_index)))

embedding_matrix = np.zeros((len(word_index)+1, 300))
for word, i in tqdm(word_index.items()):
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        embedding_matrix[i] = embedding_vector

max_features = 200000
filter_length = 5
nb_filter = 64
pool_length = 4

model = Sequential()
print('Build model...')

model1 = Sequential()
model1.add(Embedding(len(word_index)+1),
                     300,
                     weigths=[embedding_matrix], 
                     input_length=40, 
                     trainable=False)

model1.add(TimeDistributed(Dense(300, activtivation='relu')))
model1.add(Lambda(lambda x: K.sum(x, axis=1), output_shape=(300,)))

model2 = Sequential()
model2.add(Embedding(len(word_index)+1, 
                    300, 
                    weights=[embedding_matrix], 
                    input_length=40, 
                    trainable=False))

model2.add(TimeDistributed(Dense(300, activation='relu')))
model2.add(Lambda(lambda x: K.sum(x,axis=1), output_shape=(300, )))

model3 = Sequential()
model3.add(Embedding(len(word_index)+1,
                    300, 
                    weights=[embedding_matrix], 
                    input_length=40, 
                    trainable=False))

model3.add(Convolution1D(nb_filter=nb_filter,
                        filter_length=filter_length, 
                        border_mode='valid',
                        activation='relu', 
                        subsample_length=1))
model3.add(GlobalAveragePooling1D())
model3.add(Dropout(0.2))

model3.add(Dense(300))
model3.add(Dropout(0.2))
model3.add(BatchNormalization())

model4 = Sequential()
model4.add(Embedding(len(word_index)+1, 
                    300, 
                    weights=[embedding_matrix],
                    input_length=40, 
                    trainable=False))
model4.add(Convolution1D(nb_filter=nb_filter, 
                        filter_length=filter_length, 
                        border_mode='valid', 
                        activation='relu',
                        subsample_length=1))
model4.add(Dropout(0.2))

model4.add(Convolution1D(nb_filter=nb_filter, 
                        filter_length=filter_length, 
                        border_mode='valid', 
                        activation='relu', 
                        subsample_length=1))
model4.add(GlobalAveragePooling1D())
model4.add(Dropout(0.2))

model4.add(Dense(300))
model4.add(Dropout(0.2))
model4.add(BatchNormalization())

model5 = Sequential()
model5.add(Embedding(len(word_index)+1, 300, input_length=40, dropout=0.2))
model5.add(LSTM(300, dropout_w=0.2, dropout_u=0.2))

model6 = Sequential()
model6.add(Embedding(len(word_index)+1, 300, input_length=40, dropout=0.2))
model6.add(LSTM(300, dropout_w=0.2, dropout_u=0.2))

merged_model = Sequential()
merged_model.add(Merge([model1, model2, model3, model4, model5, model6], model='concat'))
merged_model.add(BatchNormalization())

merged_model.add(Dense(300))
merged_model.add(PReLU())
merged_model.add(Dropout(0.2))
merged_model.add(BatchNormalization())

merged_model.add(Dense(300))
merged_model.add(PReLU())
merged_model.add(Dropout(0.2))
merged_model.add(BatchNormalization())

merged_model.add(Dense(300))
merged_model.add(PReLU())
merged_model.add(Dropout(0.2))
merged_model.add(BatchNormalization())

merged_model.add(Dense(300))
merged_model.add(PReLU())
merged_model.add(Dropout(0.2))
merged_model.add(BatchNormalization())

merged_model.add(Dense(300))
merged_model.add(PReLU())
merged_model.add(Dropout(0.2))
merged_model.add(BatchNormalization())

merged_model.add(Dense(1))
merged_model.add(Activation('sigmoid'))

merged_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

checkpoint = ModelCheckpoint('weights.h5', monitor='val_acc', save_best_only=True, 
                            verbose=2)

merged_modle.fit([x1, x2, x1, x2, x1, x2], y=y, batch_size=384, nb_epochs=200, 
        verbose=1, validation_split=0.1, shuffle=True, callbacks=[checkpoint]) 

                       


