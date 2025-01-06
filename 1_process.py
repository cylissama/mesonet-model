import os
import re
import json
import datetime
# from nltk.corpus import stopwords

url_pattern = re.compile(r'http\S+')
hashtag_pattern = re.compile(r'#\S+')
mention_pattern = re.compile(r'@\S+')
rule = re.compile(r'[^a-zA-Z\s]')


def extract_text(tw):
    if is_extended(tw):
        return tw["extended_tweet"]["full_text"]
    else:
        return tw["text"]

def is_en(tw):
    return tw["lang"]=="en"


def get_tweet_id(tw):
    return tw["id_str"]

def get_user_id(tw):
    return tw["user"]["id_str"]

def is_extended(tw):
    if "extended_tweet" in tw:
        return True
    else:
        return False    

def text_filter(text):
    if text == None:
        return ''

    new_text = text

    
    #filter url
    new_text = re.sub(url_pattern,'',new_text)

    #filter hashtag
    new_text = re.sub(hashtag_pattern,'',new_text)

    #filter mention
    new_text = re.sub(mention_pattern,' ',new_text)

    # filter \t \n
    new_text = re.sub('\t|\n|\r|\v',' ', new_text)
    # filter multi spaces
    new_text = re.sub(' +', ' ', new_text)

    # remove space of head or tail
    new_text = re.sub('^ | $','', new_text)

    # keep number and char
    new_text = re.sub(rule, '', new_text)
    return new_text


start_date = "20201117"
end_date = "20210521"
start_date_datetime = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_datetime = datetime.datetime.strptime(end_date, '%Y%m%d')
proc_date = start_date_datetime
duration = 300   # t

data_check_list = os.listdir("Data/")
data_check_dic = {i:1 for i in data_check_list}

for _ in range(duration):
    # process the data in this date
    proc_date_str = proc_date.strftime("%Y-%m-%d")

    input_data_folder_path = "Data/"+proc_date_str+"/"
    output_data_folder_path =   "Tmp/"+proc_date_str+"/"


    if not proc_date_str in data_check_dic.keys():
        proc_date = proc_date+datetime.timedelta(days=1)
        if proc_date == end_date_datetime:
            break
        continue
    
    if not os.path.exists(output_data_folder_path):
        os.makedirs(output_data_folder_path)

    output_data_file = output_data_folder_path+"tweet_text"
    with open(output_data_file, 'w', encoding='utf-8') as file_out:


        for filename in os.listdir(input_data_folder_path):
            input_data_path = input_data_folder_path+filename

            with open(input_data_path, 'r', encoding='utf-8', errors='ignore') as file_in:
                
        
                for line in file_in:
                    try:
                        tweet = json.loads(line)
                    except:
                        print(tweet)
                        continue
                    if is_en(tweet):
                        tweet_id = get_tweet_id(tweet)
                        user_id = get_user_id(tweet)
                        text = extract_text(tweet)
                        text = text_filter(text)
                        # if len(text) < 20:
                        #     continue
                        file_out.write(tweet_id+'\t'+user_id+'\t'+text+'\t')
                        file_out.write('\n')
                        file_out.flush()


    proc_date = proc_date+datetime.timedelta(days=1)
    if proc_date == end_date_datetime:
        break



