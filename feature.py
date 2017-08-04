# -*- coding: utf-8 -*-
# Copyright 2017 The Xiaoyu Fang. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import os
from chart1 import extract_feature
import  pandas as pd
def extract_from_file(filepath, output_prefix,
                      days_for_test = 700,
                      input_shape = [30, 61] ,
                      selector = ["ROCP", "OROCP", "HROCP", "LROCP", "MACD", "RSI", "VROCP", "BOLL", "MA", "VMA", "PRICE_VOLUME"]):
    window = input_shape[0]
    #first column  must  date
    df=pd.read_csv(filepath,sep='\s+' ,parse_dates = True )
    df.sort_index(inplace=True)
    moving_features, moving_labels = extract_feature(raw_data=df, selector=selector, window=input_shape[0],with_label=True, flatten=True)
    print("feature extraction done, start writing to file...")
    train_end_test_begin = moving_features.shape[0] - days_for_test
    if train_end_test_begin < 0:
        train_end_test_begin = 0
    moving_features=pd.DataFrame(moving_features)
    print(moving_features.head(100))
    moving_labels = pd.DataFrame(moving_labels)
    moving_features[0:train_end_test_begin].to_csv(output_prefix+"_feature."+str(window),header=None,index=False)
    moving_labels[0:train_end_test_begin].to_csv(output_prefix+"_label."+str(window), header=None, index=False)
    moving_features[train_end_test_begin: moving_features.shape[0]].to_csv(output_prefix+"_feature.test."+str(window),header=None,index=False)
    moving_labels[train_end_test_begin: moving_features.shape[0]].to_csv(output_prefix+"_label.test."+str(window), header=None, index=False)
if __name__ == '__main__':
    dataset_dir = "./dataset"
    for filename in os.listdir(dataset_dir):
        if filename != '000001.csv':
           continue
        print("processing file: " + filename)
        extract_from_file(dataset_dir+"//"+filename,filename.split(".")[0],
                          days_for_test=700,
                          input_shape=[30, 61],
                          selector=["ROCP", "OROCP", "HROCP", "LROCP", "MACD", "RSI", "VROCP", "BOLL", "MA", "VMA","PRICE_VOLUME"])
