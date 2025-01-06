import pickle
from sklearn.model_selection import train_test_split

output_data_folder_path = "Label/All/"
output_model_folder_path = "Model/"

load_model_path = output_model_folder_path+"rf.p"
loaded_clf = pickle.load(open(load_model_path, 'rb'))


load_data_path = output_data_folder_path+"label.p"
dataset_X, dataset_y = pickle.load(open(load_data_path, 'rb'))


data_train, data_test, labels_train, labels_test = train_test_split(dataset_X, dataset_y, test_size=0.20, random_state=42)

result = loaded_clf.score(data_test, labels_test)

print(result)





