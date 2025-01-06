import os
import sys
import random
import datetime
import binascii




start_date = "20210301"
end_date = "20210521"
start_date_datetime = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_datetime = datetime.datetime.strptime(end_date, '%Y%m%d')
proc_date = start_date_datetime
duration = 300   #
future_days = 5

data_check_list = os.listdir("Data/")
data_check_dic = {i:1 for i in data_check_list}

for _ in range(duration):
    # process the data in this date
    proc_date_str = proc_date.strftime("%Y-%m-%d")

    print(proc_date_str)

    input_data_folder_path = "Tmp/"+proc_date_str+"/"
    output_data_folder_path =   "Tmp/"+proc_date_str+"/"

    if not proc_date_str in data_check_dic.keys():
        proc_date = proc_date+datetime.timedelta(days=1)
        if proc_date == end_date_datetime:
            break
        continue

    input_data_file_list = []
    for i in range(future_days):
        future_date =  proc_date+datetime.timedelta(days=i)
        future_date_str = future_date.strftime("%Y-%m-%d")

        if not future_date_str in data_check_dic.keys():
            continue
        future_data_folder_path = "Tmp/"+future_date_str+"/"
        future_data_file = future_data_folder_path+"tweet_text"
        input_data_file_list.append(future_data_file)


    numtweets = 0
    numHashes = 10
    curtweets = 0

    print('Shingling tweets...')

    # The current shingle ID value to assign to the next new shingle we 
    # encounter. When a shingle gets added to the dictionary, we'll increment this
    # value.
    curShingleID = 0

    # Create a dictionary of the articles, mapping the article identifier (e.g., 
    # "t8470") to the list of shingle IDs that appear in the document.
    tweetAsShingleSets = {}
    tweetNames = []
    totalShingles = 0

    # if not os.path.exists(output_data_folder_path):
    #     os.makedirs(output_data_folder_path)

    # tweet_limit = 10000
    for input_data_file in input_data_file_list:
        with open(input_data_file, 'r', encoding='utf-8', errors='ignore') as file_in:
            for line in file_in:
                # tweet_limit -= 1
                # if tweet_limit < 0:
                #     break
                
                tweet_id = line.strip().split('\t')[0]
                try:
                    tweet_text =  line.strip().split('\t')[2]
                except:
                    continue
                tweet_token = tweet_text.strip().split()
                
                # Maintain a list of all tweet IDs.
                tweetNames.append(tweet_id)

                curtweets = curtweets + 1

                # 'shinglesInDoc' will hold all of the unique shingle IDs present in the 
                # current document. If a shingle ID occurs multiple times in the document,
                # it will only appear once in the set (this is a property of Python sets).
                shinglesInTweet = set()

                # For each word in the document...
                for index in range(0, len(tweet_token) - 2):
                    # Construct the shingle text by combining three words together.
                    shingle =tweet_token[index] + ' ' + tweet_token[index + 1] + ' ' + tweet_token[index + 2]
                    # shingle = tweet_text[index] + ' ' + tweet_text[index + 1] + ' ' + tweet_text[index + 2]
    

                    # Hash the shingle to a 32-bit integer.
                    crc = binascii.crc32(bytes(shingle, encoding="ascii")) & 0xffffffff

            
                    # Add the hash value to the list of shingles for the current document. 
                    # Note that set objects will only add the value to the set if the set 
                    # doesn't already contain it. 
                    shinglesInTweet.add(crc)

                # Store the completed list of shingles for this document in the dictionary.
                tweetAsShingleSets[tweet_id] = shinglesInTweet
    numtweets = curtweets


    # =============================================================================
    #                     Define Triangle Matrices
    # =============================================================================

    # Define virtual Triangle matrices to hold the similarity values. For storing
    # similarities between pairs, we only need roughly half the elements of a full
    # matrix. Using a triangle matrix requires less than half the memory of a full
    # matrix, and can protect the programmer from inadvertently accessing one of
    # the empty/invalid cells of a full matrix.

    # Calculate the number of elements needed in our triangle matrix
    numElems = int(numtweets * (numtweets - 1) / 2)

    # Initialize two empty lists to store the similarity values. 
    # 'JSim' will be for the actual Jaccard Similarity values. 
    # 'estJSim' will be for the estimated Jaccard Similarities found by comparing
    # the MinHash signatures.
    JSim = [0 for x in range(numElems)]
    estJSim = [0 for x in range(numElems)]

    def getTriangleIndex(i, j):
    # If i == j that's an error.
        if i == j:
            sys.stderr.write("Can't access triangle matrix with i == j")
            sys.exit(1)
        # If j < i just swap the values.
        if j < i:
            i, j = j, i
            # temp = i
            # i = j
            # j = temp

        # Calculate the index within the triangular array.
        # This fancy indexing scheme is taken from pg. 211 of:
        # http://infolab.stanford.edu/~ullman/mmds/ch6.pdf
        # But I adapted it for a 0-based index.
        # Note: The division by two should not truncate, it
        #       needs to be a float. 
        k = int(i * (numtweets - (i + 1) / 2.0) + j - i) - 1

        return k

    # =============================================================================
    #                 Generate MinHash Signatures
    # =============================================================================
    print ('Generating random hash functions...')

    # Record the maximum shingle ID that we assigned.
    maxShingleID = 2**32-1

    # We need the next largest prime number above 'maxShingleID'.
    # I looked this value up here: 
    # http://compoasso.free.fr/primelistweb/page/prime/liste_online_en.php
    nextPrime = 4294967311


    # Our random hash function will take the form of:
    #   h(x) = (a*x + b) % c
    # Where 'x' is the input value, 'a' and 'b' are random coefficients, and 'c' is
    # a prime number just greater than maxShingleID.

    # Generate a list of 'k' random coefficients for the random hash functions,
    # while ensuring that the same value does not appear multiple times in the 
    # list.
    def pickRandomCoeffs(k):
        # Create a list of 'k' random values.
        randList = []
    
        while k > 0:
            # Get a random shingle ID.
            randIndex = random.randint(0, maxShingleID) 
    
            # Ensure that each random number is unique.
            while randIndex in randList:
                randIndex = random.randint(0, maxShingleID) 
        
            # Add the random number to the list.
            randList.append(randIndex)
            k = k - 1
        
        return randList

    # For each of the 'numHashes' hash functions, generate a different coefficient 'a' and 'b'.   
    coeffA = pickRandomCoeffs(numHashes)
    coeffB = pickRandomCoeffs(numHashes)


    print ('Generating MinHash signatures for all documents...')

    # List of documents represented as signature vectors
    signatures = []

    # Rather than generating a random permutation of all possible shingles, 
    # we'll just hash the IDs of the shingles that are *actually in the document*,
    # then take the lowest resulting hash code value. This corresponds to the index 
    # of the first shingle that you would have encountered in the random order.

    # For each tweet...
    for tweetID in tweetNames:
    
        # Get the shingle set for this document.
        shingleIDSet = tweetAsShingleSets[tweetID]
    
        # The resulting minhash signature for this document. 
        signature = []
    
        # For each of the random hash functions...
        for i in range(0, numHashes):
        
            # For each of the shingles actually in the document, calculate its hash code
            # using hash function 'i'. 
        
            # Track the lowest hash ID seen. Initialize 'minHashCode' to be greater than
            # the maximum possible value output by the hash.
            minHashCode = nextPrime + 1
        
            # For each shingle in the document...
            for shingleID in shingleIDSet:
                # Evaluate the hash function.
                hashCode = (coeffA[i] * shingleID + coeffB[i]) % nextPrime 
        
                # Track the lowest hash code seen.
                if hashCode < minHashCode:
                    minHashCode = hashCode

            # Add the smallest hash code value as component number 'i' of the signature.
            signature.append(minHashCode)
        # Store the MinHash signature for this document.
        signatures.append(signature)


    # =============================================================================
    #                     Compare All Signatures
    # =============================================================================  
    print ('Comparing all signatures...')

    # Creates a N x N matrix initialized to 0.
    # For each of the test documents...
    for i in range(0, numtweets):
   
        # Get the MinHash signature for document i.
        signature1 = signatures[i]
        # if i%100==0:
        #     print(i)
        
        # For each of the other test documents...
        for j in range(i + 1, numtweets):
        
            # Get the MinHash signature for document j.
            try:
                signature2 = signatures[j]
            except:
                print("warning on comparing signatures")
                continue
        
            count = 0
            # Count the number of positions in the minhash signature which are equal.
            for k in range(0, numHashes):
                count = count + (signature1[k] == signature2[k])
        
            # Record the percentage of positions which matched.    
            estJSim[getTriangleIndex(i, j)] = (count / numHashes)


    # =============================================================================
    #                   Display Similar Document Pairs
    # =============================================================================  




    threshold = 0.5
    # For each of the document pairs...
    with open(output_data_folder_path+'cluster','w') as same_file, open(output_data_folder_path+'non_cluster','w') as unique_file:
        same_dict = {}
        same_list = []
        for i in range(0, numtweets):
            if not tweetNames[i] in same_list:
                value = ''
                for j in range(i + 1, numtweets):
                    if not tweetNames[j] in same_list:
                        # Retrieve the estimated similarity value for this pair.
                        estJ = estJSim[getTriangleIndex(i, j)]
                
                        # If the similarity is above the threshold...
                        if estJ > threshold:

                            if tweetNames[i] in same_dict.keys():
                                value = same_dict[tweetNames[i]]+':'+str(tweetNames[j])
                                same_dict[tweetNames[i]] = value
                                same_list.append(tweetNames[j])
                            else:
                                value = str(tweetNames[j])
                                same_dict[tweetNames[i]] = value
                                same_list.append(tweetNames[i])
                                same_list.append(tweetNames[j])
                # unique
                if not value:
                    unique_file.write(str(tweetNames[i])+':')             
                            

        
        for k, v in same_dict.items():
            same_file.write(k+':'+v+'\n')


    proc_date = proc_date+datetime.timedelta(days=1)
    if proc_date == end_date_datetime:
        break