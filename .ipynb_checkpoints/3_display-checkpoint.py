import os
import json
import datetime




start_date = "20201117"
end_date = "20210521"
start_date_datetime = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_datetime = datetime.datetime.strptime(end_date, '%Y%m%d')
proc_date = start_date_datetime
duration = 300   #

data_check_list = os.listdir("Data/")
data_check_dic = {i:1 for i in data_check_list}

for _ in range(duration):
    # process the data in this date
    proc_date_str = proc_date.strftime("%Y-%m-%d")

    input_data_folder_path = "Tmp/"+proc_date_str+"/"
    output_data_folder_path =  "Cluster/"+proc_date_str+"/"

    if not proc_date_str in data_check_dic.keys():
        proc_date = proc_date+datetime.timedelta(days=1)
        if proc_date == end_date_datetime:
            break
        continue

    if not os.path.exists(output_data_folder_path):
        os.makedirs(output_data_folder_path)



    input_data_cluster = input_data_folder_path+'cluster'
    input_data_text = input_data_folder_path+'tweet_text'
    output_data_file = output_data_folder_path+"tweets.txt"

    cluster_dic = {}
    with open (input_data_cluster, 'r') as file_in:
        for line in file_in:
            line_split = line.strip().split(":")

            cluster_dic[line_split[0]] = len(line_split)

    with open(input_data_text, 'r') as file_in, \
        open(output_data_file, 'w') as file_out:
        for line in file_in:
            line_split = line.strip().split("\t")
            tweet_id = line_split[0]
            user_id = line_split[1]
            tweet_text = line_split[2]

            if tweet_id in cluster_dic.keys():
                file_out.write('N'+'\t')
                file_out.write(str(cluster_dic[tweet_id])+'\t')
                file_out.write(tweet_id+'\t')
                file_out.write(user_id+'\t')
                file_out.write(tweet_text+'\n')
                file_out.flush()

    proc_date = proc_date+datetime.timedelta(days=1)
    if proc_date == end_date_datetime:
        break


