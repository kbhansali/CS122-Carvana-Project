import tensorflow as tf
import numpy as np
import pandas as pd
from google.colab import files
import io
import ast
"""
All neural net training was done in google colab on a GPU. The code has been directly pasted into this document. 
"""
def normalize(data):
    mean = np.mean(data)
    std = np.std(data)
    normalized = (data-mean)/std
    return mean, std, normalized

df = pd.read_csv('/content/agg_df_3.csv')
df['basic info'] = df['basic info'].apply(ast.literal_eval)
basic = pd.DataFrame(df['basic info'].values.tolist()).add_prefix('info_').fillna('').to_numpy(dtype='str')

df['installed packages'] = df['installed packages'].apply(ast.literal_eval)
packages = pd.DataFrame(df['installed packages'].values.tolist()).add_prefix('info_').fillna('').to_numpy(dtype='str')

df['installed options'] = df['installed options'].apply(ast.literal_eval)
options = pd.DataFrame(df['installed options'].values.tolist()).add_prefix('info_').fillna('').to_numpy(dtype='str')

price_data = df['price'].to_numpy(dtype=int)
string_data = df[['model year','manufacturer','model','type','zipcode']].to_numpy(dtype=str)
mileage_data  = df['mileage'].to_numpy(dtype=int)
boolean_data = df[[column for column in df.columns if '150' in column]]

for column in boolean_data.columns:
  boolean_data[column] = boolean_data[column].map(
    {' True':1,' False':0,' TRUE':1,' FALSE':0,True:1,False:0}
  )

boolean_data = boolean_data.to_numpy(dtype=int)

price_mean, price_std, price_data = normalize(price_data)
mileage_mean, mileage_std, mileage_data = normalize(mileage_data)

text_input = tf.keras.Input(5,dtype='string')
lookup_layer = tf.keras.layers.StringLookup()
lookup_layer.adapt(string_data)
text_as_integer = lookup_layer(text_input)
text_as_vector = tf.keras.layers.Embedding(lookup_layer.vocab_size(),16,input_length=5)(text_as_integer) #8 is a hyperparameter
text_as_vector = tf.keras.layers.Flatten()(text_as_vector)

text_input2 = tf.keras.Input(10,dtype='string')
lookup_layer2 = tf.keras.layers.StringLookup()
lookup_layer2.adapt(basic)
text_as_integer2 = lookup_layer2(text_input2)
text_as_vector2 = tf.keras.layers.Embedding(lookup_layer2.vocab_size(),16,input_length=10)(text_as_integer2) #8 is a hyperparameter
text_as_vector2 = tf.keras.layers.GlobalAveragePooling1D()(text_as_vector2)

options_input1 = tf.keras.Input(packages.shape[-1], dtype="string")
options_lookup1 = tf.keras.layers.StringLookup()
options_lookup1.adapt(packages)
options_int1 = lookup_layer(options_input1)
options_vec1 = tf.keras.layers.Embedding(options_lookup1.vocab_size(),8,input_length=packages.shape[-1])(options_int1)
options_vec1 = tf.keras.layers.GlobalAveragePooling1D()(options_vec1)

options_input2 = tf.keras.Input(options.shape[-1], dtype="string")
options_lookup2 = tf.keras.layers.StringLookup()
options_lookup2.adapt(options)
options_int2 = lookup_layer(options_input2)
options_vec2 = tf.keras.layers.Embedding(options_lookup2.vocab_size(),8,input_length=options.shape[-1])(options_int2)
options_vec2 = tf.keras.layers.GlobalAveragePooling1D()(options_vec2)

mileage_input = tf.keras.Input(1)
checklist_input = tf.keras.Input(150)
bool_layer = tf.keras.layers.Dense(16,activation="swish")(checklist_input)

total_input = tf.keras.layers.Concatenate()([text_as_vector,text_as_vector2,mileage_input,bool_layer,options_vec1,options_vec2])
hidden3 = tf.keras.layers.Dense(64,activation='swish')(total_input)
hidden2 = tf.keras.layers.Dense(32,activation='swish')(hidden3)
hidden = tf.keras.layers.Dense(32,activation='swish')(hidden2)
output = tf.keras.layers.Dense(1,activation='linear')(hidden)

model = tf.keras.Model(inputs=[text_input,text_input2,mileage_input,checklist_input,options_input1,options_input2],outputs=output) #if you need multiple inputs or outputs, put them in a list

model.compile(optimizer=tf.keras.optimizers.Adam(0.001),loss='mse')

model.fit([string_data,basic,mileage_data,boolean_data, packages, options],price_data,batch_size=32,epochs=100000,validation_split=0.2,callbacks=tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True))
model.save("content/pricing_model")

tf.keras.utils.plot_model(model,to_file = 'test.png')