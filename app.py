import os
from flask import Flask, render_template, request
import file_processing as fp
import pickle
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from scipy.sparse import hstack
from sklearn import preprocessing
import pandas as pd
import numpy as np
from sklearn.metrics.classification import accuracy_score, log_loss

__author__ = 'jayeshthukarul'

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/upload", methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT, 'files/')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)

        label=predictclass(filename)

        if label==0:
            return render_template("success.html")
        else:
            return render_template("review.html")
    


def predictclass(filename):
    data=fp.readFile("files/"+filename)
    os.remove("files/"+filename)

    file_blocks=fp.processData(data)

    def getVals(file_blocks):

        fraud_check_vals=[]

        survey_prepared_for, vehicle_make, vehicle_model, vehicle_rating, vehicle_market_value, vehicle_claim_value, vehicle_model_year=fp.getGeneralInfo(file_blocks['GENERAL INFORMATION'])

        policeInformed=fp.policeInformed(file_blocks["CIRCUMSTANCES"])

        incident_type, vehicle_involved=fp.incidentType(file_blocks["PARTIES INVOLVED"])

        collosion_type=fp.collisonType(file_blocks["ASPECT OF THE DAMAGE"])

        incident_severity=fp.incidentSeverity(file_blocks["GENERAL INFORMATION"])

        property_damage, body_damage=fp.damageNature(file_blocks["NATURE OF THE DAMAGE"])

        fraud_check_vals=[incident_type, collosion_type, incident_severity, vehicle_involved, property_damage, body_damage, policeInformed, vehicle_claim_value, vehicle_make, vehicle_model, vehicle_model_year]

        return fraud_check_vals

    vals=getVals(file_blocks)

    lst = [vals]
    test_data1 = np.array(vals)
    test_data = pd.DataFrame(lst)

    # data preparing and predicting

    if int(test_data[10]) > 2015:
        test_data[10] = '2015'

    #print(test_data)   

    with open('incident_type_vectorizer.pk', 'rb') as pickle_file:
        incident_type_encoder = pickle.load(pickle_file)
        
    with open('incident_severity_vectorizer.pk', 'rb') as pickle_file:
        incident_severity_encoder = pickle.load(pickle_file)

    with open('collision_type_vectorizer.pk', 'rb') as pickle_file:
        collision_type_encoder = pickle.load(pickle_file)

    with open('police_vectorizer.pk', 'rb') as pickle_file:
        police_encoder = pickle.load(pickle_file)

    with open('propery_damage_vectorizer.pk', 'rb') as pickle_file:
        property_encoder = pickle.load(pickle_file)

    with open('auto_maker_vectorizer.pk', 'rb') as pickle_file:
        auto_make_encoder = pickle.load(pickle_file)

    with open('auto_model_vectorizer.pk', 'rb') as pickle_file:
        auto_model_encoder = pickle.load(pickle_file)

    with open('label_calsse.pk', 'rb') as pickle_file:
        label_classes = pickle.load(pickle_file)
        
    with open('standardiser.pk', 'rb') as pickle_file:
        sc = pickle.load(pickle_file)

        
    with open('final_xgboost_model.sav', 'rb') as pickle_file:
        xgboost_model = pickle.load(pickle_file)


    #print(test_data[0].replace(' ', '_',regex=True))
        
    test_data[0].replace(' ', '_',regex=True,inplace=True)
    test_data[1].replace(' ', '_',regex=True,inplace=True)
    test_data[2].replace(' ', '_',regex=True,inplace=True)


    incidentType_onehot = incident_type_encoder.transform(test_data[0])
    incidentSeverity_onehot = incident_severity_encoder.transform(test_data[2])
    collisonType_onehot = collision_type_encoder.transform(test_data[1])
    police_onehot = police_encoder.transform(test_data[6])
    property_onehot = property_encoder.transform(test_data[4])
    auto_make_onehot = auto_make_encoder.transform(test_data[8])
    auto_model_onehot = auto_model_encoder.transform(test_data[9])

    #print(label_classes)

    enc = LabelEncoder()
    enc.fit(label_classes)
    new_cat_features = enc.transform(label_classes)
    new_cat_features = new_cat_features.reshape(-1, 1) # Needs to be the correct shape
    #print(new_cat_features)

    lable = int(test_data[10]) - 1995
    lbl_arr = pd.Series(lable)

    ohe = OneHotEncoder(sparse=False) #Easier to read
    final_tran = ohe.fit(new_cat_features)

    #
    tst = lbl_arr.values.reshape(1,-1)

    auto_year_onehot = ohe.transform(tst)





    boost = pickle.load(open("final_xgboost_model.sav", "rb"))

    interm1 = hstack((incidentType_onehot,incidentSeverity_onehot,collisonType_onehot,police_onehot,property_onehot,auto_make_onehot,auto_model_onehot))
    interm2 = hstack((interm1,auto_year_onehot))
    interm3 = test_data[[3,5,7]]
    final_feed_data = hstack((interm2,interm3.astype(float)))

    standardised_final_data = sc.transform(final_feed_data)

    class_lbl = boost.predict(standardised_final_data)

    return class_lbl



if __name__ == "__main__":
    app.run(port=4555, debug=True)
