import os
import datetime
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from sklearn.ensemble import RandomForestClassifier



start_date = "20220101"
end_date = "20220102"
start_date_datetime = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_datetime = datetime.datetime.strptime(end_date, '%Y%m%d')
proc_date = start_date_datetime
duration = 300   # t

data_check_list = os.listdir("Data/")
data_check_dic = {i:1 for i in data_check_list}


dataset_X = []
dataset_y = []

for _ in range(duration):
    # process the data in this date
    proc_date_str = proc_date.strftime("%Y-%m-%d")

    input_data_tmp_path = "Tmp/"+proc_date_str+"/"
    input_data_label_path = "Label/"+proc_date_str+"/"
    output_data_folder_path = "Label/All/"
    output_model_folder_path = "Model/"

    if not proc_date_str in data_check_dic.keys():
        proc_date = proc_date+datetime.timedelta(days=1)
        if proc_date == end_date_datetime:
            break
        continue
    
    if not os.path.exists(output_data_folder_path):
        os.makedirs(output_data_folder_path)

    if not os.path.exists(output_model_folder_path):
        os.makedirs(output_model_folder_path)

    input_data_feature = input_data_tmp_path+"tweet_feature"
    input_data_label = input_data_label_path+"labeled_tweets.txt"
    

    label_dic = {}

    with open(input_data_label, 'r', encoding="utf-8", errors="ignore") as file_label_in:
        for label_line in file_label_in:
            label_line_split = label_line.strip().split('\t')
            label_tweet_id = label_line_split[0]
            label_dic[label_tweet_id] = int(label_line_split[-1])

    with open(input_data_feature, 'r', encoding="utf-8", errors="ignore") as file_feature_in:
        for feature_line in file_feature_in:
            feature_line_split = feature_line.strip().split('\t')
            feature_tweet_id = feature_line_split[0]
            if feature_tweet_id in label_dic.keys():
                dataset_X.append([float(i) for i in feature_line_split[2:-1]])
                dataset_y.append(label_dic[feature_tweet_id])

 

    proc_date = proc_date+datetime.timedelta(days=1)
    if proc_date == end_date_datetime:
        break


dataset_X = np.array(dataset_X)
dataset_y = np.array(dataset_y)

scaler = MinMaxScaler()
dataset_X = scaler.fit_transform(dataset_X)



data_train, data_test, labels_train, labels_test = train_test_split(dataset_X, dataset_y, test_size=0.20, random_state=42)

clf = RandomForestClassifier()

clf.fit(data_train, labels_train)



save_model_path = output_model_folder_path+"rf.p"
pickle.dump(clf, open(save_model_path, 'wb'))

save_data_path = output_data_folder_path+"label.p"
pickle.dump([dataset_X, dataset_y], open(save_data_path, 'wb'))
