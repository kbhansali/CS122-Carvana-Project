from flask import Flask, request, render_template 
from flask_restful import Resource, Api
import sys
import os
import re
import pandas as pd
import ast
import numpy as np
from tensorflow import keras
import jellyfish


app = Flask(__name__)
api = Api(app)
port = 5100

zip_codes = [('AK', 99654),
('AL', 35242),
 ('AR', 72401),
 ('AZ', 85364),
 ('CA', 90011),
 ('CO', 80013),
 ('CT', 6902),
 ('DC', 20011),
 ('DE', 19720),
 ('FL', 33024),
 ('GA', 30043),
 ('HI', 96706),
 ('IA', 50613),
 ('ID', 83646),
 ('IL', 60629),
 ('IN', 47906),
 ('KS', 66062),
 ('KY', 40475),
 ('OK', 73099),
 ('OR', 97006),
 ('PA', 19120),
 ('RI', 2860),
 ('SC', 29483),
 ('SD', 57106),
 ('TN', 37013),
 ('TX', 77449),
 ('UT', 84095),
 ('VA', 22193),
 ('VT', 5401),
 ('WA', 99301),
 ('WI', 53215),
 ('WV', 26554),
 ('WY', 82001)]

dem_tups = [('LA', '70726'),
 ('MA', '02301'),
 ('MD', '20906'),
 ('ME', '04401'),
 ('MI', '48197'),
 ('MN', '55106'),
 ('MO', '63376'),
 ('MS', '39503'),
 ('MT', '59901'),
 ('NC', '27610'),
 ('ND', '58103'),
 ('NE', '68516'),
 ('NH', '03103'),
 ('NJ', '08701'),
 ('NM', '87121'),
 ('NV', '89108'),
 ('NY', '11368'),
 ('OH', '45011')]

# different types of packages and options from training dataset
df = pd.read_csv("agg_df_3.csv", header=0)
df['installed packages'] = df['installed packages'].apply(ast.literal_eval)
uniq_packages = np.unique(pd.DataFrame(df['installed packages'].values.tolist()).add_prefix('info_').fillna('').to_numpy(dtype='str'))
df['installed options'] = df['installed options'].apply(ast.literal_eval)
uniq_options = np.unique(pd.DataFrame(df['installed options'].values.tolist()).add_prefix('info_').fillna('').to_numpy(dtype='str'))

# our neural net model
model = keras.models.load_model('pricing_model_1')

@app.route('/', methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        # car year
        y = request.form['year']
        # car make
        try:
            m = request.form['make']
        except:
            m = ""
        # car model
        mo = request.form['model']
        # car type
        t = request.form['type']
        # number of doors
        door = request.form['door']
        # mileage
        mi = request.form['mileage']
        # basic information about the car
        b = [request.form['engine'], (request.form['interior'] + " Interior Color")*2, (request.form['exterior'] + " Exterior Color")*2, request.form['dact'], request.form['city'] + " City / " + request.form['high'] + " Hwy", request.form['aom'], request.form['drive'], request.form['keys'], request.form['seats'] + " seats"]
        # installed packages
        p = request.form['package']
        p = p.strip('][').split(', ')
        if '' in p:
            p.remove('')
        p = [" ".join(i.split(" ")[:5]) for i in p]
        # installed options
        o = request.form['options']
        o = o.strip('][').split(', ')
        if '' in o:
            o.remove('')
        o = [" ".join(i.split(" ")[:5]) for i in o]
        # State the car is from
        z = request.form['zip']
        # Parts that fail the 150-pt checklist
        i = request.form.getlist('150_point')
        i = re.findall(r"[0-9]+", str(i))
        boo = [1]*150
        if i[0] != '0':
            for num in i:
                boo[int(num) - 1] = 0
        # match state with relevant zip code
        for tup in zip_codes:
            if tup[0] == z:
                z = tup[1]
                break
        for tup in dem_tups:
            if tup[0] == z:
                z = tup
                break

        mi = int(mi)
        t = t + " " + door

        string_data = []
        string_data.append(y)
        string_data.append(m)
        string_data.append(mo)
        string_data.append(t)
        string_data.append(str(z))
        
        # make sure inputs match real packages and options from training model
        temp_p = []
        for obj in p:
            doc1 = obj
            match = 0
            word = ""
            for c,val in enumerate(uniq_options):
                val = str(val)
                if obj == val:
                    word = val
                    break
                doc2 = val
                num = jellyfish.jaro_winkler(doc1, doc2)
                if num > match:
                    word = val
                    match = num
            temp_p.append(word)
        if len(temp_p) < 7:
            temp_p += ['']*(7 - len(temp_p))
        
        temp_o = []
        for obj in o:
            doc1 = obj
            match = 0
            word = ""
            for c,val in enumerate(uniq_packages):
                val = str(val)
                if obj == val:
                    word = val
                    break
                doc2 = val
                num = jellyfish.jaro_winkler(doc1, doc2)
                if num > match:
                    word = val
                    match = num
            temp_o.append(word)
        if len(temp_o) < 15:
            temp_o += ['']*(15 - len(temp_o))
        
        price_mean = 22799.29808994536
        price_std = 6433.486075863107

        mile_mean = 50173.460304487926
        mile_sd = 24262.689932556776

        if len(string_data) < 5:
            string_data += ['']*(5 - len(string_data))
        if len(b) < 10:
            b += ['']*(10 - len(b))
        one = np.array([string_data])
        two = np.array([b])
        three = np.array([(mi - mile_mean)/mile_sd])
        four = np.array([boo])
        five = np.array([temp_p])
        six = np.array([temp_o])
        # run neural net and output estimated price (dollar amount)
        projection = price_std * model.predict([one,two,three,four,five,six]) + price_mean

        return render_template('index.html', proj = round(projection[0][0],2))

    elif request.method == 'GET':
        return render_template('index.html')


if __name__ == '__main__':
    app.run()