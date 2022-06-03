# -*- coding: utf-8 -*-
"""Final Lab 5: IDS using Random Forest Classifier

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YG46gY93ccLauZLLoGkHQqElg0DNtEHX

# Intrusion Detection System using ML model to predict attacks
#### Using KDD dataset to predict attacks correctly.

### Learning Objectives
* Learn to create Intrusion Detection System using Random Forest Classifier.
* Visualize the predictions made by the algorithm with Confusion Matrix and performance metrics.

### Imports

Import all the required libraries including pandas, numpy, and matplotlib for the lab.
"""

import pandas as pd
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
plt.style.use('seaborn-white')
import seaborn as sns

"""### Mount Google Drive

In the code cell below, we mount the google drive to the colab environment so that we have access to the local version of the dataset.
"""

from google.colab import drive
drive.mount('/content/drive')

"""### Read CSV

We read the csv file using pandas in the code below.
"""

mydata = pd.read_csv('/content/drive/My Drive/Intro2MLDatasets/Lab5/KDDCup99.csv')

"""### Analyzing Dataset

This code allows us to see the length and width of the dataset. The first integer denotes the number of rows and the second integer denotes the number of columns in the dataset.
"""

mydata.shape

"""The code cells below help us visualize the dataest in every angle. We use the given functions from pandas to display the shape, first 100 data, and the features in the dataset."""

mydata.head(100)

mydata.columns

"""### Identify Features to drop

In the code below, we identify the features which are same in every instances. 'lnum_outbound_cmds' and 'is_host_login' are the two features which has same data in every row of the dataset. Hence, these features will not help model to predict the attacks and are not necessary in the dataset that will be used to train a model.  

"""

cols_to_drop = []

"""
Check if column has any dissimilar data or not.
If Column with no dissimilar data, add to cols_to_drop as it will be insignificant for model training.
"""

for (columnName, columnData) in mydata.iteritems():
  if columnName == 'logged_in' or columnName == 'dst_host_same_srv_rate':
    newdata = mydata[(mydata[columnName] != 1) | (mydata[columnName] != 1.00)]
    if newdata.empty:
      cols_to_drop.append(columnName)
  else:
    newdata = mydata[(mydata[columnName] != 0) | (mydata[columnName] != 0.00)]
    if newdata.empty:
      cols_to_drop.append(columnName)
      
print(cols_to_drop)

"""### Drop Features

The features we identified as futile are now dropped from the dataset we use to train the model. An original copy of the dataset is kept safe in a new variable. It is always smart to keep a copy of the original dataset. 
"""

mydata_orig = mydata.copy()
mydata.drop(columns=cols_to_drop, inplace=True)
cols_to_drop = []

"""### Visualize type of Attacks
In the given dataframe, we will only be working with the select attack types from the dataset. We will be using the top 8 more frequent attacks available in the dataset.
"""

dd = mydata.groupby('label').size()
dd.sort_values()

attacks = ['normal', 'neptune', 'smurf', 'back', 'satan', 'ipsweep', 'portsweep', 'warezclient']
mydata = mydata[mydata['label'].isin(attacks)]

"""### Identify missing values

The code below helps us identify features in the dataset which have missing values in it. Machine Learning model needs to have a dataset with no missing values. Hence, it is a part of the data preprocessing to check if there are any missing values in the dataset.
"""

#finds column with missing values or null values 
def print_missing_values(data):
  data_null = pd.DataFrame(len(data) - data.notnull().sum(), columns = ['Count'])
  data_null = data_null[data_null['Count'] > 0].sort_values(by='Count', ascending=False)
  data_null = data_null/len(data)*100
  return data_null

"""### Missing values observation

As we can see below, there seems to be no missing values in any feature in the dataset. Hence, we can skip the part where we identify median value of the row and replace with missing value.
"""

print_missing_values(mydata)

"""### Numerical and Categorical Features

It is necessary to split the features into numerical and categorical values before we feed the dataset to the model. All the integers are regarded as the numerical features and all the rest are categorized as categorical features.
"""

def categorize(data):
  num_columns = []
  cat_columns = []

  #separate numerical and categorical features
  for col in data.columns.values:
    if data[col].dtypes == 'int64' or data[col].dtypes == 'float64':
      num_columns += [col]
    else: 
      cat_columns += [col]

  return [cat_columns, num_columns]

categories = categorize(mydata)
categorical_features = categories[0]
numerical_features = categories[1]
print("Categorical Features", categorical_features)
print("Numerical Features", numerical_features)

"""### Identify the type of labels

Label is the column in the dateset which is what the model is going to predict using all the other features from the dataset. KDD dataset has multiple label hence making this multi-class classification.
"""

attacks = set()
for index, row in mydata.iterrows():
  attacks.add(row['label'])
print(attacks)

"""### Import Scaler and label encoder

Label Encoder helps encode the categorical features into numerical format. MinMaxScaler is one of the way of scaling and normalizing the data. 
"""

from sklearn.preprocessing import MinMaxScaler, LabelEncoder

"""### Utilizing Label Encoder
Label Encoder converts the categorical features into numerical format so that the machine learning algorithm can understand it.
"""

def label_encode(data, categorical_features):
  data_encoded = data.copy()

  # Use Label Encoder for categorical columns (including target column)
  for feature in categorical_features:
      le = LabelEncoder()
      le.fit(data_encoded[feature])
      data_encoded[feature] = le.fit_transform(data_encoded[feature])
      if feature == 'label':
        le_name_mapping = dict(zip(le.transform(le.classes_), le.classes_))

  return (data_encoded, le_name_mapping)

data_encoded, label_mapping = label_encode(mydata, categorical_features)

"""### label_mapping
label_mapping variable is the hashmap which contains all the one-hot encoded numeric value and it's corresponding label.
"""

print(label_mapping)

"""### Visualize the label

As we can see in the result below, the label is converted into the numerical format from the categorical version for the model to understand and make predictions.
"""

labeled_attacks = set()
for index, row in data_encoded.iterrows():
  labeled_attacks.add(row['label'])
print(labeled_attacks)

data_encoded.head()

"""### Utilizing Scaler

Similary, we make use of the MinMaxScaler to scale and normalize the data and make it ready to use for the Machine Learning model.
"""

def scale_data(data, numerical_features):
  data_encoded = data.copy()
  for feature in numerical_features:
      val = data_encoded[feature].values[:, np.newaxis]
      mms = MinMaxScaler()
      data_encoded[feature] = mms.fit_transform(val)
      
  data_encoded = data_encoded.astype(float)
  return data_encoded

data_encoded = scale_data(data_encoded, numerical_features)

data_encoded.head()

print(label_mapping)

data_encoded.shape

"""### What is Random Forest?
Decision Trees are the fundamental part of the Random Forest Classifier. Random Forest consists of large number of individual decision trees that operate as an ensemble. The majority predictions from the individual decision trees is the ultimate prediction of the Random Forest Classifier.

Understanding Random Forest

https://towardsdatascience.com/understanding-random-forest-58381e0602d2

### RandomForest Classifier

We use Random Forest Machine learning technique as suggested and experimented by one of the research paper. The paper found that the Random Forest works particularly best with the KDD dataset. 

Mohammad  Almseidin  et  al.  “Evaluation  of  MachineLearning  Algorithms  for  Intrusion  Detection  System”.In:CoRRabs/1801.02330  (2018).  arXiv:  1801.02330.URL: http://arxiv.org/abs/1801.02330.

### Initilaizing Random Forest model
"""

from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators = 100)

"""### Model performance

The function below evaluates the accuracy, precision, recall, and F1 score of the prediction made on the test dataset while also generating the confusion matrix for the model.
"""

from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, roc_curve, auc, precision_score, recall_score

def get_model_performance(test_labels, predicted_labels):
  accuracy = accuracy_score(test_labels, predicted_labels)
  matrix = (confusion_matrix(test_labels, predicted_labels)/test_labels.shape[0]) * 100
  precision = precision_score(test_labels, predicted_labels, average='macro')
  recall = recall_score(test_labels, predicted_labels, average='macro')
  f1 = f1_score(test_labels, predicted_labels, average='macro')
  return accuracy, matrix, precision, recall, f1

"""### Plot Performance

The function below helps plot the confusion matrix generated from the get_model_performance function above.
"""

def plot_model_performance(matrix):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    sns.heatmap(matrix, annot=True, cmap='Blues', fmt='g')
    ax.set_xlabel('Predicted Labels')
    ax.set_ylabel('True Labels')
    ax.set_title('Confusion Matrix')
    ax.xaxis.set_ticklabels(list(attacks))
    ax.yaxis.set_ticklabels(list(attacks))

"""## SECTION I 
### Using Imbalanced Dataset

### Create Features and Labels
labels contains all the labels from the dataset and features contains the dataframe except the values from label.
"""

from sklearn.utils import shuffle
data_encoded = shuffle(data_encoded)
labels = data_encoded['label']
features = data_encoded.drop('label', axis=1)

"""### Train and Test Data Split

It is absolutely necessary to split the data into training, testing, and validation to make sure Machine Learning algorithms are learning well and can make predictions as accurately as possible. Here we use train_test_split to split 80% of the data as the train, 10% as the test and the rest 10% as the validation dataset.
"""

from sklearn.model_selection import train_test_split 

train_features, rem_features, train_labels, rem_labels = train_test_split(features, labels, train_size=0.8, shuffle=True)
valid_features, test_features, valid_labels, test_labels = train_test_split(rem_features, rem_labels, test_size=0.5, shuffle=True)

print("Train Dataset Feature Shape: ")
print(train_features.shape)
print("Test Dataset Feature Shape: ")
print(test_features.shape)
print("Valid Dataset Feature Shape: ")
print(valid_features.shape)
print("Train Dataset label Shape: ")
print(train_labels.shape)
print("Test Dataset label Shape: ")
print(test_labels.shape)
print("Valid Dataset label Shape: ")
print(valid_labels.shape)

"""### Visualize labels 
As we  can see below, the labels present in the dataframe only belong to select few types of attack. The proportion of the attacks present in the dataset is not uniform.
"""

lst = []
for i in range(valid_labels.shape[0]):
    lst.append(int(valid_labels.iloc[i]))

print("Labels: ", lst)

print(label_mapping)

"""### Fit model
Fit the model with the features and labels dataframe created from the train_test_split.
"""

rf.fit(train_features, train_labels)

"""### Testing

The test features and train features are used to predict the labels and test the performance of the Random Forest model.

The accuracy of the model using the training data.
"""

train_pred_labels = rf.predict(train_features)
accuracy, matrix, precision, recall, f1 = get_model_performance(train_labels, train_pred_labels)
print("The accuracy of the model: ", accuracy)
print("The precision of the model: ", precision)
print("The recall of the model: ", recall)
print("The f1 score of the model: ", f1)

"""The accuracy of the model using the test data."""

test_pred_labels = rf.predict(test_features)
accuracy, matrix, precision, recall, f1 = get_model_performance(test_labels, test_pred_labels)
print("The accuracy of the model: ", accuracy)
print("The precision of the model: ", precision)
print("The recall of the model: ", recall)
print("The f1 score of the model: ", f1)

"""The training accuracy and test accuracy doesn't seem to have a lot of difference. Hence, it shows that the model was not overfit."""

plot_model_performance(matrix)

"""### Randomly selected instances for validation
The code below creates a list of lists named 'data' consisting of randomly selected instances from the validation dataset, where only features are included. It also creates a list of it's corresponding true labels named true_labels.
"""

import random
data = []
true_labels = []

for i in range(10):
  temp = random.randint(0, valid_features.shape[0])
  data.append(valid_features.iloc[temp].tolist())
  true_labels.append(valid_labels.iloc[temp])

for index, ele in enumerate(true_labels):
  true_labels[index] = label_mapping[int(ele)]

print(data)
print(true_labels)

"""### Create Dataframe
Create a pandas dataframe called new_data out of the list of lists of instances generated in the code cell above.
"""

new_data = pd.DataFrame(data)
print(new_data)
new_data.columns = valid_features.columns.tolist()
new_data

"""### Validate results
The randomly selected instances of data not used in the training and testing are used to make preidctions of it's label. 
"""

features_new = np.array(new_data)
pred_labels = rf.predict(features_new)
pred_labels = pred_labels.tolist()

for index, ele in enumerate(pred_labels):
  temp = label_mapping[int(ele)]
  pred_labels[index] = label_mapping[int(ele)]

print("True labels: ", true_labels)
print("Pred labels: ", pred_labels)

"""## SECTION II
### Using balanced Dataset

### Create Features and Labels
Separate features and labels into two different dataset to create Synthetic data and further split into train and test dataset.
"""

from imblearn.over_sampling import SMOTE
from collections import Counter
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline

data_encoded = shuffle(data_encoded)
features_SMOTE = data_encoded.iloc[:, data_encoded.columns != 'label']
labels_SMOTE = data_encoded.iloc[:, data_encoded.columns == 'label']

X_SMOTE = features.to_numpy()
y_SMOTE = labels.to_numpy()
counter_orig = Counter(y_SMOTE)
print(y_SMOTE)

"""### Visualize count of Attack types
The bar graph below shows the number of instances for each attack type in the original dataset before creating synthetic instances.
"""

from matplotlib import pyplot
attack_types = []
for c in counter_orig.keys():
  attack_types.append(label_mapping[c])
  
pyplot.figure(figsize=(8,7))
pyplot.bar(attack_types, counter_orig.values())
pyplot.show()

"""### SMOTE
Imbalanced classification involves developing predicitve models on classification datasets that have a class inbalance. Synthetic Minority Oversampling Technique, or SMOTE is an approach to address imbalanced dataset where minority class is oversampled. It creates new synthetic instances according to the neighbourhood of each example of the minority class.

https://machinelearningmastery.com/smote-oversampling-for-imbalanced-classification/
"""

strategy_over = {0:201862, 1:187396, 2:239604, 4:178387, 5:195267, 3:216522, 7:173021}
strategy_under = {6:242063}
over = SMOTE(sampling_strategy = strategy_over)
under = RandomUnderSampler(sampling_strategy = strategy_under)

steps = [('o', over),('u', under)]
pipeline = Pipeline(steps=steps)
X_SMOTE, y_SMOTE = pipeline.fit_resample(X_SMOTE, y_SMOTE)

counter = Counter(y_SMOTE)
print(counter)

"""### Visualize count of Attack types after SMOTE
The bar graph below shows the number of instances for each attack type in the dataset after creating synthetic instances using SMOTE.
"""

from matplotlib import pyplot
attack_types = []
for c in counter.keys():
  attack_types.append(label_mapping[c])

pyplot.figure(figsize=(8,7))  
pyplot.bar(attack_types, counter.values())
pyplot.show()

X_SMOTE = pd.DataFrame(X_SMOTE, columns=features_SMOTE.columns)
y_SMOTE = pd.DataFrame(y_SMOTE, columns=labels_SMOTE.columns)

"""### Train and Test Data Split

It is absolutely necessary to split the data into training, testing, and validation to make sure Machine Learning algorithms are learning well and can make predictions as accurately as possible. Here we use train_test_split to split 80% of the data as the train, 10% as the test and the rest 10% as the validation dataset.
"""

from sklearn.model_selection import train_test_split 

train_features_SMOTE, rem_features, train_labels_SMOTE, rem_labels = train_test_split(X_SMOTE, y_SMOTE, train_size=0.8, shuffle=True)
valid_features_SMOTE, test_features_SMOTE, valid_labels_SMOTE, test_labels_SMOTE = train_test_split(rem_features, rem_labels, test_size=0.5, shuffle=True)

print("Train Dataset Feature Shape: ")
print(train_features_SMOTE.shape)
print("Test Dataset Feature Shape: ")
print(test_features_SMOTE.shape)
print("Valid Dataset Feature Shape: ")
print(valid_features_SMOTE.shape)
print("Train Dataset label Shape: ")
print(train_labels_SMOTE.shape)
print("Test Dataset label Shape: ")
print(test_labels_SMOTE.shape)
print("Valid Dataset label Shape: ")
print(valid_labels_SMOTE.shape)

print(label_mapping)

"""### Visualize labels 
As we  can see below, the labels present in the dataframe belong to various types of attack. The proportion of the attacks present in the dataset are more uniform after creating synthetic data.
"""

lst = []
for i in range(valid_labels_SMOTE.shape[0]):
    lst.append(int(valid_labels_SMOTE.iloc[i]))

print(lst)

print(label_mapping)

"""### Fit model
Fit the model with the features and labels dataframe created from the train_test_split from the new dataset.
"""

rf.fit(train_features_SMOTE, train_labels_SMOTE)



"""### Testing

The test features are used to predict the labels and  test the performance of the Random Forest model.

The accuracy of the model using the training data.
"""

train_pred_labels_SMOTE = rf.predict(train_features_SMOTE)
accuracy, matrix, precision, recall, f1 = get_model_performance(train_labels_SMOTE, train_pred_labels_SMOTE)
print("The accuracy of the model: ", accuracy)
print("The precision of the model: ", precision)
print("The recall of the model: ", recall)
print("The f1 score of the model: ", f1)

"""The accuracy of the model using the test data."""

test_pred_labels_SMOTE = rf.predict(test_features_SMOTE)
accuracy, matrix, precision, recall, f1 = get_model_performance(test_labels_SMOTE, test_pred_labels_SMOTE)
print("The accuracy of the model: ", accuracy)
print("The precision of the model: ", precision)
print("The recall of the model: ", recall)
print("The f1 score of the model: ", f1)

"""The training accuracy and test accuracy doesn't seem to have a lot of difference. Hence, it shows that the model was not overfit."""

plot_model_performance(matrix)

print(valid_features_SMOTE.shape)

"""### Randomly selected instances for validation
The code below creates a list of lists named 'data' consisting of randomly selected instances from the validation dataset, where only features are included. It also creates a list of it's corresponding true labels named true_labels.
"""

import random
data = []
true_labels_SMOTE = []

for i in range(10):
  temp = random.randint(0, valid_features_SMOTE.shape[0])
  data.append(valid_features_SMOTE.iloc[temp].tolist())
  true_labels_SMOTE.append(valid_labels_SMOTE.iloc[temp])

for index, ele in enumerate(true_labels_SMOTE):
  true_labels_SMOTE[index] = label_mapping[int(ele)]

print(data)
print(true_labels_SMOTE)

"""### Create Dataframe
Create a pandas dataframe called new_data out of the list of lists of instances generated in the code cell above.
"""

new_data = pd.DataFrame(data)
print(new_data)
new_data.columns = valid_features_SMOTE.columns.tolist()
new_data

"""### Validate results
The randomly selected instances of data not used in the training and testing are used to make preidctions of it's label. 
"""

features_new_SMOTE = np.array(new_data)
pred_labels_SMOTE = rf.predict(features_new_SMOTE)
pred_labels_SMOTE = pred_labels_SMOTE.tolist()

for index, ele in enumerate(pred_labels_SMOTE):
  temp = label_mapping[int(ele)]
  pred_labels_SMOTE[index] = label_mapping[int(ele)]

print("True labels: ", true_labels_SMOTE)
print("Pred labels: ", pred_labels_SMOTE)

"""**In Confusion matrices, what differences did you observe? How do you think they are similar or dissimilar? Explain. (6 points)**

**What are imbalanced and balanced datasets? What are their roles in Machine Learning? (4 points)**

## Extra Credit

**What other classifiers can you use? Use one other classifier and compare the result from above.**
"""