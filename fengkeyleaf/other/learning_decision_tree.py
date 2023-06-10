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
import ast
from typing import (
    List,
    Dict,
    Tuple
)

def reformatting( df_f: pd.DataFrame, df_l: pd.Series, C: List[ str ] ) -> Tuple[ List[ List[ float ] ], List[ int ] ]:
    """
    formatting from the csv is kinda weird so it is explained here:
    each line looks something like:
        "[sketch]",label
    so, we need to unpack the sketch back into a list from a string
    and then also make sure each part of the sketch is read in as an integer
    """
    data: List[ List[ float ] ] = [ ]
    labels: List[ int ] = []

    assert len( df_f ) == len( df_l )
    for ( i, s ) in df_f.iterrows():
        # print( df.loc[ i, sketch_write.RANGE_STR ] )
        # tmp1: List[ str ] = df.loc[ i, sketch_write.RANGE_STR ].strip( '][' ).split( ',' )
        # tmp2: List[ int ] = []
        # for item in tmp1:
        #     tmp2.append( int( item ) )

        labels.append( df_l.loc[ i ] )

        # print( s )
        L: List[ float ] = []
        for c in C:
            L.append( df_f.loc[ i, c ] )

        data.append( L )

    return ( data, labels )

# Pregnancies,Glucose,BloodPressure,SkinThickness,Insulin,BMI,DiabetesPedigreeFunction,Age,Outcome
col_names = [ 'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction',
              'Age', 'Outcome' ]
# load dataset
pima = pd.read_csv( "./diabetes.csv", header = None, names = col_names )
pima = pd.read_csv( "./diabetes.csv" )

# pima.head()

# print( pima )

# split dataset in features and target variable
feature_cols = [ 'Pregnancies', 'Insulin', 'BMI', 'Age', 'Glucose', 'BloodPressure', 'DiabetesPedigreeFunction' ]
X = pima[ feature_cols ]  # Features
y = pima[ "Outcome" ]  # Target variable

# print( X )
# print( y )
print( type( y ) ) # <class 'pandas.core.series.Series'>
print( y.size )

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split( X, y, test_size = 0.3,
                                                     random_state = 1 )  # 70% training and 30% test

print( type( y_train ) ) # pandas.core.series.Series

X_train_list, y_train_list = reformatting( X_train, y_train, feature_cols )
X_test_list, y_test_list = reformatting( X_test, y_test, feature_cols )
# print( X_train_list )
# print( y_train_list )
# print( X_test_list )
# print( y_test_list )

# print( X_train )
# print( type( X_train ) ) # pandas.core.frame.DataFrame
# print( X_test )
# print( y_train )
# print( y_test )

# Create Decision Tree classifer object
clf = DecisionTreeClassifier()

# Train Decision Tree Classifer
clf = clf.fit( X_train, y_train )
t = DecisionTreeClassifier().fit( X_train_list, y_train_list )

# Predict the response for test dataset
y_pred = clf.predict( X_test )

# Model Accuracy, how often is the classifier correct?
print( "Accuracy:", metrics.accuracy_score( y_test, y_pred ) )
print( "Accuracy:", clf.score( X_test, y_test ) )
print( "Accuracy:", t.score( X_test_list, y_test_list ) )
