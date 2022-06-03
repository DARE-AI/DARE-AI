# -*- coding: utf-8 -*-
"""SPIE Credit Bias
Dataset: Benchmark Statlog "Australian Credit Approval"
Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LveexqVSuBFmfP7neFuH8XyNusTuyv1g
"""

!pip install aif360

# Load all necessary packages
import sys
sys.path.insert(1, "../")  

import numpy as np
import pandas as pd
np.random.seed(0)

# Graphs libraries
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
plt.style.use('seaborn-white')
import seaborn as sns

import plotly.offline as py
py.init_notebook_mode(connected=False)
import plotly.graph_objs as go
import plotly.tools as tls
import plotly.figure_factory as ff
from plotly import tools

from aif360.datasets import StandardDataset
from aif360.metrics import BinaryLabelDatasetMetric
from aif360.algorithms.preprocessing import Reweighing

from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, roc_curve, auc
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier

from IPython.display import Markdown, display

from google.colab import drive
drive.mount('/content/drive')

mydata = pd.read_csv('/content/drive/My Drive/australian.csv', names = ['Sex', 'Age', 'TimeAdd', 'HomeSta', 'CurOCu', 'CurJobSta', 'MeanTImeJob', 'otherInvs', 'BankAcc', 'TimeBank', 'Liab', 'AccRef', 'MnthHsngExp', 'SaveAccBal', 'Class'])

mydata.shape

mydata.head(100)

mydata.head().T

mydata.columns

"""### Drop Features
As a part of the model training, we have to preprocess the dataset in order to discard features which may not be useful for our training purpose. In the cell below, we discard every features except 'City', 'State', 'Year', 'Month' 'Perpetrator Sex', 'Perpetrator Age', 'Perpetrator Race'. 
"""

mydata_orig = mydata.copy()

mydata.columns

"""### Rename columns
Rename columns to represent new synthetic data. 
"""

# mydata = mydata.rename(columns={'Perpetrator Sex': 'Person Sex','Perpetrator Age': 'Person Age','Perpetrator Race': 'Person Race'})

mydata["Sex"].replace({1: "Male", 0: "Female"}, inplace=True)

mydata.head(100)

"""### Identify missing values
As we preprocess the data, it is necessary for us to identify the features which have missing values in between. Below we create a count of missing values in each features of the dataset. 

The plot display shows the number of data missing in each of the dataset feature.
"""

def print_missing_values(data):
    data_null = pd.DataFrame(len(data) - data.notnull().sum(), columns = ['Count'])
    data_null = data_null[data_null['Count'] > 0].sort_values(by='Count', ascending=False)
    data_null = data_null/len(data)*100
    data_null.reset_index(inplace=True)
    data_null = data_null.rename(columns = {'index':'Features'})
    print(data_null)

    plt.style.use('ggplot')
    x = data_null['Features']
    y = data_null['Count']
    x_pos = [i for i, _ in enumerate(x)]

    plt.figure(figsize=(4,4))
    plt.bar(x_pos, y, color='green')
    plt.xlabel('Features')
    plt.ylabel('Percentage of missing data')
    plt.title("Column with missing values in the dataset")

    plt.xticks(x_pos, x)
    plt.show()

"""### Print missing values
Display the features with the percentage of missing values in each of them. 
"""

print('Number total of rows : '+ str(mydata.shape[0]))
print_missing_values(mydata)

"""### Numerical and Categorical Features
In the code below, we split the features used to train the model to split into numerical and categorical category. All the integers are categorized as numerical feature and all rest are categorized as categorical feature. 
"""

def categorize(data):
  num_columns = []
  cat_columns = []

  for col in data.columns.values:
      if data[col].dtypes == 'int64' or data[col].dtypes == 'float64':
          num_columns += [col]
      else:
          cat_columns += [col]
  return [cat_columns, num_columns]

cat_columns, num_columns = categorize(mydata)[0], categorize(mydata)[1]
print(cat_columns, num_columns)

"""### Median value
For each of the numerical feature, find the median value and save it as median value of the feature.
"""

median_val = pd.Series()
for col in num_columns:
  median_val[col] = mydata[col].median()
print("Median values for each Numerical features \n\n", median_val)

"""### Handle missing values
As each features have missing datas in it, these missing values should be replaced before we can train the model. These missing values are replaced by median value generatead in the previous code for numerical features. Missing values for categorical features should be replaced by "Missing value".
"""

def handle_missing_values(data, median_val):
    df = data.copy()
    for col in df:
        if col in median_val.index.values:
            df[col] = df[col].fillna(median_val[col])
        else:
            df[col] = df[col].fillna("Missing value")
    
    return df

mydata = handle_missing_values(mydata, median_val)
mydata.head(10)

"""### Display function
The display function below uses matplotlib to create bar graph and pie chart to diplay the Perpetrator characteristics.
"""

def target_distribution(y_var, data):
    val = data[y_var]

    plt.style.use('seaborn-whitegrid')
    plt.rcParams.update({'font.size': 13})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

    cnt = val.value_counts().sort_values(ascending=True)
    labels = cnt.index.values

    sizes = cnt.values
    colors = sns.color_palette("PuBu", len(labels))

    #------------COUNT-----------------------
    ax1.barh(cnt.index.values, cnt.values, color=colors)
    ax1.set_title('Count plot of '+y_var)

    #------------PERCENTAGE-------------------
    ax2.pie(sizes, labels=labels, colors=colors,autopct='%1.0f%%', shadow=True, startangle=130)
    ax2.axis('equal')
    ax2.set_title('Distribution of '+y_var)
    plt.show()

var = 'Sex'
target_distribution(y_var=var, data=mydata)

var = 'Class'
target_distribution(y_var=var, data=mydata)

"""### One hot encoding 
Categorical variables are not readable to ML algorithms. Hence, it is necessary to convert them into integer based binary format.
"""

def label_encode(data, categorical_features):
  data_encoded = data.copy()
  categorical_names = {}

# Use Label Encoder for categorical columns
  for feature in categorical_features:
      le = LabelEncoder()
      le.fit(data_encoded[feature])
      data_encoded[feature] = le.fit_transform(data_encoded[feature])
      categorical_names[feature] = le.classes_

  return (data_encoded, categorical_names)

"""###Feature Scaling
Data normalization is important in Machine learning as it is used to standardize the range of features of data. We transform the data such that the features are within a specific range [0,1].
"""

def scale_data(data, numerical_features):
  data_encoded = data.copy()
  for feature in numerical_features:
      val = data_encoded[feature].values[:, np.newaxis]
      mms = MinMaxScaler()
      data_encoded[feature] = mms.fit_transform(val)
      
  data_encoded = data_encoded.astype(float)
  return data_encoded

"""### Format dataset
Use the functions above to split dataset into categorical and numerical feature, label encode, and scale the data. 
"""

data_category = categorize(mydata)
categorical_features, numerical_features = data_category[0], data_category[1]

data_encoded, categorical_names = label_encode(mydata, categorical_features)
data_encoded = scale_data(data_encoded, numerical_features)

print(categorical_names)

data_encoded.head(15)

privileged_sex = np.where(categorical_names['Sex'] == 'Male')[0]

data_orig_sex = StandardDataset(data_encoded, 
                               label_name='Class', 
                               favorable_classes=[1], 
                               protected_attribute_names=['Sex'], 
                               privileged_classes=[privileged_sex])

def meta_data(dataset):
    # print out some labels, names, etc.
    display(Markdown("#### Dataset shape"))
    print(dataset.features.shape)
    display(Markdown("#### Favorable and unfavorable labels"))
    print(dataset.favorable_label, dataset.unfavorable_label)
    display(Markdown("#### Protected attribute names"))
    print(dataset.protected_attribute_names)
    display(Markdown("#### Privileged and unprivileged protected attribute values"))
    print(dataset.privileged_protected_attributes, dataset.unprivileged_protected_attributes)
    display(Markdown("#### Dataset feature names"))
    print(dataset.feature_names)

meta_data(data_orig_sex)

np.random.seed(42)

data_orig_sex_train, data_orig_sex_test = data_orig_sex.split([0.9], shuffle=True)

display(Markdown("#### Train Dataset shape"))
print("Perpetrator Sex :",data_orig_sex_train.features.shape)
display(Markdown("#### Test Dataset shape"))
print("Perpetrator Sex :",data_orig_sex_test.features.shape)

privileged_groups = [{'Sex': 1}]
unprivileged_groups = [{'Sex': 0}]

metric_orig_train = BinaryLabelDatasetMetric(data_orig_sex_train, 
                                             unprivileged_groups=unprivileged_groups,
                                             privileged_groups=privileged_groups)
display(Markdown("#### Original training dataset"))
print("Difference in mean outcomes between unprivileged and privileged groups Statistical Parity Difference = %f" % metric_orig_train.mean_difference())

display(Markdown("#### Original training dataset"))
print("Difference in mean outcomes between unprivileged and privileged groups Disparate_Impact = %f" % metric_orig_train.disparate_impact())

rf_orig_sex = RandomForestClassifier().fit(data_orig_sex_train.features, 
                     data_orig_sex_train.labels.ravel(), 
                     sample_weight=data_orig_sex_train.instance_weights)

from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, roc_curve, auc, precision_score, recall_score

def get_model_performance(test_labels, predicted_labels, probs):
  accuracy = accuracy_score(test_labels, predicted_labels)
  matrix = confusion_matrix(test_labels, predicted_labels)/test_labels.shape[0]
  precision = precision_score(test_labels, predicted_labels, average='macro')
  recall = recall_score(test_labels, predicted_labels, average='macro')
  f1 = f1_score(test_labels, predicted_labels, average='macro')
  return accuracy, matrix, precision, recall, f1

predicted_labels = rf_orig_sex.predict(data_orig_sex_test.features)
probs = rf_orig_sex.predict_proba(data_orig_sex_test.features)
accuracy, matrix, precision, recall, f1 = get_model_performance(data_orig_sex_test.labels, predicted_labels, probs)
print("The accuracy of the model: ", accuracy)
print("The precision of the model: ", precision)
print("The recall of the model: ", recall)
print("The f1 score of the model: ", f1)

def plot_model_performance():
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    sns.heatmap(matrix, annot=True, cmap='Blues', fmt='g')
    ax.set_xlabel('Predicted Labels')
    ax.set_ylabel('True Labels')
    ax.set_title('Confusion Matrix')
    ax.xaxis.set_ticklabels(['Rejected', 'Approved'])
    ax.yaxis.set_ticklabels(['Rejected', 'Approved'])

plot_model_performance()

RW = Reweighing(unprivileged_groups=unprivileged_groups,
                privileged_groups=privileged_groups)
dataset_transf_train = RW.fit_transform(data_orig_sex_train)
dataset_transf_test = RW.fit_transform(data_orig_sex_test)

metric_transf_train = BinaryLabelDatasetMetric(dataset_transf_train, 
                                               unprivileged_groups=unprivileged_groups,
                                               privileged_groups=privileged_groups)
display(Markdown("#### Transformed training dataset"))
print("Difference in mean outcomes between unprivileged and privileged groups = %f" % metric_transf_train.mean_difference())

display(Markdown("#### Original training dataset"))
print("Difference in mean outcomes between unprivileged and privileged groups Disparate_Impact = %f" % metric_transf_train.disparate_impact())

rf_weighted_sex = RandomForestClassifier().fit(dataset_transf_train.features, 
                     dataset_transf_train.labels.ravel(), 
                     sample_weight=dataset_transf_train.instance_weights)

predicted_labels = rf_weighted_sex.predict(dataset_transf_test.features)
probs = rf_weighted_sex.predict_proba(dataset_transf_test.features)
accuracy, matrix, precision, recall, f1 = get_model_performance(dataset_transf_test.labels, predicted_labels, probs)
print("The accuracy of the model: ", accuracy)
print("The precision of the model: ", precision)
print("The recall of the model: ", recall)
print("The f1 score of the model: ", f1)

plot_model_performance()

from aif360.metrics import BinaryLabelDatasetMetric, ClassificationMetric

def fair_metrics(dataset, pred, pred_is_dataset=False):
    if pred_is_dataset:
        dataset_pred = pred
    else:
        dataset_pred = dataset.copy()
        dataset_pred.labels = pred
    
    cols = ['statistical_parity_difference','disparate_impact']
    obj_fairness = [[0,1]]
    
    fair_metrics = pd.DataFrame(data=obj_fairness, index=['objective'], columns=cols)
   
    for attr in dataset_pred.protected_attribute_names:
        idx = dataset_pred.protected_attribute_names.index(attr)
        
        privileged_groups =  [{attr:dataset_pred.privileged_protected_attributes[idx][0]}] 
        unprivileged_groups = [{attr:dataset_pred.unprivileged_protected_attributes[idx][0]}] 
  
        classified_metric = ClassificationMetric(dataset, 
                                                     dataset_pred,
                                                     unprivileged_groups=unprivileged_groups,
                                                     privileged_groups=privileged_groups)

        metric_pred = BinaryLabelDatasetMetric(dataset_pred,
                                                     unprivileged_groups=unprivileged_groups,
                                                     privileged_groups=privileged_groups)

        acc = classified_metric.accuracy()

        row = pd.DataFrame([[metric_pred.mean_difference(),
                                metric_pred.disparate_impact()]],
                           columns  = cols,
                           index = [attr]
                          )
        fair_metrics = fair_metrics.append(row)    
    
    fair_metrics = fair_metrics.replace([-np.inf, np.inf], 2)
        
    # print(fair_metrics)
    return fair_metrics

def plot_fair_metrics(fair_metrics):
    fig, ax = plt.subplots(figsize=(7,4), ncols=2, nrows=1)

    plt.subplots_adjust(
        left    =  0.125, 
        bottom  =  0.1, 
        right   =  0.9, 
        top     =  0.9, 
        wspace  =  .5, 
        hspace  =  1.1
    )

    y_title_margin = 1.2

    plt.suptitle("Fairness metrics", y = 1.09, fontsize=20)
    sns.set(style="dark")

    cols = fair_metrics.columns.values
    obj = fair_metrics.loc['objective']
    size_rect = [0.0,0.0]
    rect = [0.0,0.0]
    bottom = [-1,0]
    top = [1,2]
    bound = [[0.0,0.0],[1.0,1.0]]

    display(Markdown("### Check bias metrics :"))
    display(Markdown("A model can be considered bias if just one of these two metrics show that this model is biased."))
    for attr in fair_metrics.index[1:len(fair_metrics)].values:
        display(Markdown("#### For the %s attribute :"%attr))
        check = [bound[i][0] < fair_metrics.loc[attr][i] < bound[i][1] for i in range(0,2)]
        display(Markdown("With default thresholds, bias against unprivileged group detected in **%d** out of 2 metrics"%(2 - sum(check))))

    for i in range(0,2):
        plt.subplot(1, 2, i+1)
        ax = sns.barplot(x=fair_metrics.index[1:len(fair_metrics)], y=fair_metrics.iloc[1:len(fair_metrics)][cols[i]])
        
        for j in range(0,len(fair_metrics)-1):
            a, val = ax.patches[j], fair_metrics.iloc[j+1][cols[i]]
            marg = -0.2 if val < 0 else 0.1
            ax.text(a.get_x()+a.get_width()/5, a.get_y()+a.get_height()+marg, round(val, 3), fontsize=15,color='black')

        plt.ylim(bottom[i], top[i])
        plt.setp(ax.patches, linewidth=0)
        ax.add_patch(patches.Rectangle((-5,rect[i]), 10, size_rect[i], alpha=0.3, facecolor="green", linewidth=1, linestyle='solid'))
        plt.axhline(obj[i], color='black', alpha=0.3)
        plt.title(cols[i])
        ax.set_ylabel('')    
        ax.set_xlabel('')

def get_fair_metrics_and_plot(data, model, plot=True, model_aif=False):
    pred = model.predict(data).labels if model_aif else model.predict(data.features)
    # fair_metrics function available in the metrics.py file
    fair = fair_metrics(data, pred)

    if plot:
        # plot_fair_metrics function available in the visualisations.py file
        # The visualisation of this function is inspired by the dashboard on the demo of IBM aif360 
        plot_fair_metrics(fair)
        display(fair)
    
    return fair

display(Markdown('### Bias metrics for the protected attribute Sex'))
fair = get_fair_metrics_and_plot(data_orig_sex_train, rf_orig_sex)

display(Markdown('### Bias metrics for the protected attribute Sex'))
fair = get_fair_metrics_and_plot(dataset_transf_train, rf_orig_sex)
