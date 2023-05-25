# -*- coding: utf-8 -*-

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

# https://www.datacamp.com/tutorial/decision-tree-classification-python

# Load libraries
import pandas as pd
from sklearn.tree import DecisionTreeClassifier  # Import Decision Tree Classifier
from sklearn.model_selection import train_test_split  # Import train_test_split function
from sklearn import metrics  # Import scikit-learn metrics module for accuracy calculation

# Pregnancies,Glucose,BloodPressure,SkinThickness,Insulin,BMI,DiabetesPedigreeFunction,Age,Outcome
col_names = [ 'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction',
              'Age', 'Outcome' ]
# load dataset
pima = pd.read_csv( "./diabetes.csv", header = None, names = col_names )
pima = pd.read_csv( "./diabetes.csv" )

pima.head()

# print( pima )

# split dataset in features and target variable
feature_cols = [ 'Pregnancies', 'Insulin', 'BMI', 'Age', 'Glucose', 'BloodPressure', 'DiabetesPedigreeFunction' ]
X = pima[ feature_cols ]  # Features
y = pima[ "Outcome" ]  # Target variable

# print( X )
# print( y )

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split( X, y, test_size = 0.3,
                                                     random_state = 1 )  # 70% training and 30% test

print( X_train )
# print( type( X_train ) )
# print( X_test )
print( y_train )
# print( y_test )

# Create Decision Tree classifer object
clf = DecisionTreeClassifier()

# Train Decision Tree Classifer
clf = clf.fit( X_train, y_train )

# Predict the response for test dataset
y_pred = clf.predict( X_test )

# Model Accuracy, how often is the classifier correct?
print( "Accuracy:", metrics.accuracy_score( y_test, y_pred ) )
print( "Accuracy:", clf.score( X_test, y_test ) )
