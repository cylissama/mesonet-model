import os
import json
import datetime




start_date = "20220101"
end_date = "20220102"
start_date_datetime = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_datetime = datetime.datetime.strptime(end_date, '%Y%m%d')
proc_date = start_date_datetime
duration = 300   #

data_check_list = os.listdir("Data/")
data_check_dic = {i:1 for i in data_check_list}


for _ in range(duration):
    # process the data in this date
    proc_date_str = proc_date.strftime("%Y-%m-%d")

    input_data_tmp_path = "Tmp/"+proc_date_str+"/"
    input_data_folder_path = "Cluster/"+proc_date_str+"/"
    output_data_folder_path =  "Label/"+proc_date_str+"/"

    if not proc_date_str in data_check_dic.keys():
        proc_date = proc_date+datetime.timedelta(days=1)
        if proc_date == end_date_datetime:
            break
        continue

    if not os.path.exists(output_data_folder_path):
        os.makedirs(output_data_folder_path)

    input_data_text = input_data_tmp_path+"tweet_text"
    input_data_cluster = input_data_tmp_path+'cluster'
    input_data_label = input_data_folder_path+'tweets.txt'
    output_data_file = output_data_folder_path+"labeled_tweets.txt"

    cluster_reverse = {}
    with open(input_data_cluster, 'r') as file_in:
        for line in file_in:
            line_split = line.strip().split(":")
            for lc in line_split:
                cluster_reverse[lc] = line_split[0]

    label_dic = {}
    with open(input_data_label, 'r') as file_in:
        for line in file_in:
            line_split = line.strip().split("\t")
            if not line_split[0] == 'N':
                label_dic[line_split[2]] = line_split[0]

    with open(input_data_text, 'r') as file_in, \
        open(output_data_file, 'w') as file_out:
        for line in file_in:
            line_split = line.strip().split("\t")
            tweet_id = line_split[0]
            user_id = line_split[1]
            tweet_text = line_split[2]

            if not tweet_id in cluster_reverse.keys():
                continue
            cluster_id = cluster_reverse[tweet_id]

            if not cluster_id in label_dic.keys():
                continue

            label = label_dic[cluster_id]
      

            file_out.write(tweet_id+'\t')
            file_out.write(user_id+'\t')
            file_out.write(tweet_text+'\t')
            file_out.write(label+'\n')
            file_out.flush()

    proc_date = proc_date+datetime.timedelta(days=1)
    if proc_date == end_date_datetime:
        break

