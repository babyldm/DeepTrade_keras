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
import sys
import numpy
from keras.callbacks import TensorBoard, ModelCheckpoint
import pandas as pd
from windpuller1 import WindPuller
from dataset import DataSet
from feature1 import extract_from_file

def read_ultimate(path, input_shape,code="000001"):
    ultimate_features = pd.read_csv(path +code+ "_feature." + str(input_shape[0])).values
    ultimate_features = ultimate_features.reshape(-1, input_shape[0], input_shape[1])
    ultimate_labels =  pd.read_csv(path +code+ "_label." + str(input_shape[0])).values
    train_set = DataSet(ultimate_features, ultimate_labels)
    test_features = pd.read_csv(path + code+"_feature.test." + str(input_shape[0])).values
    test_features = test_features.reshape(-1, input_shape[0], input_shape[1])
    test_labels = pd.read_csv(path +code+ "_label.test." + str(input_shape[0])).values
    test_set = DataSet(test_features, test_labels)
    return train_set, test_set

def read_feature(path, input_shape, prefix):
    ultimate_features = numpy.loadtxt("%s/%s_feature.%s" % (path, prefix, str(input_shape[0])))
    ultimate_features = numpy.reshape(ultimate_features, [-1, input_shape[0], input_shape[1]])
    ultimate_labels = numpy.loadtxt("%s/%s_label.%s" % (path, prefix, str(input_shape[0])))
    # ultimate_labels = numpy.reshape(ultimate_labels, [-1, 1])
    train_set = DataSet(ultimate_features, ultimate_labels)
    test_features = numpy.loadtxt("%s/%s_feature.test.%s" % (path, prefix, str(input_shape[0])))
    test_features = numpy.reshape(test_features, [-1, input_shape[0], input_shape[1]])
    test_labels = numpy.loadtxt("%s/%s_label.test.%s" % (path, prefix, str(input_shape[0])))
    # test_labels = numpy.reshape(test_labels, [-1, 1])
    test_set = DataSet(test_features, test_labels)
    return train_set, test_set
'''
def read_ultimate(path, input_shape):
    ultimate_features = pd.read_csv(path + "ultimate_feature." + str(input_shape[0])).values
    ultimate_features = ultimate_features.reshape(-1, input_shape[0], input_shape[1])
    ultimate_labels =  pd.read_csv(path + "ultimate_label." + str(input_shape[0])).values
    train_set = DataSet(ultimate_features[:len(ultimate_features) * 9 // 10, :, :],
                       ultimate_labels[:len(ultimate_labels) * 9 // 10])
    test_set = DataSet(ultimate_features[len(ultimate_features) * 9 // 10:, :, :],
                      ultimate_labels[len(ultimate_labels) * 9 // 10:])
    return train_set, test_set
'''

def calculate_cumulative_return(labels, pred):
    cr = []
    if len(labels) <= 0:
        return cr
    cr.append(1. * (1. + labels[0] * pred[0]))
    for l in range(1, len(labels)):
        cr.append(cr[l-1] * (1 + labels[l] * pred[l]))
    for i in range(len(cr)):
        cr[i] = cr[i] - 1
    return cr


def evaluate_model(model_path, code, input_shape=[30, 61]):
    extract_from_file("dataset/%s.csv" % code, code)
    train_set, test_set =read_ultimate("./", input_shape,code=code)
    saved_wp = WindPuller(input_shape).load_model(model_path)
    scores = saved_wp.evaluate(test_set.images, test_set.labels, verbose=0)
    print('Test loss:', scores[0])
    print('test accuracy:', scores[1])
    pred = saved_wp.predict(test_set.images, 1024)
    cr = calculate_cumulative_return(test_set.labels, pred)
    print("changeRate\tpositionAdvice\tprincipal\tcumulativeReturn")
    for i in range(len(test_set.labels)):
        print(str(test_set.labels[i]) + "\t" + str(pred[i]) + "\t" + str(cr[i] + 1.) + "\t" + str(cr[i]))
def make_model(input_shape, nb_epochs=100, batch_size=128, lr=0.01, n_layers=1, n_hidden=16, rate_dropout=0.3,code="000001"):
    model_path = 'model.%s' % input_shape[0]
    wp = WindPuller(input_shape=input_shape, lr=lr, n_layers=n_layers, n_hidden=n_hidden, rate_dropout=rate_dropout)
    train_set, test_set = read_ultimate("./", input_shape,code=code)

    wp.fit(train_set.images, numpy.squeeze(train_set.labels), batch_size=batch_size,
           nb_epoch=nb_epochs, shuffle=True, verbose=1,
           validation_data=(test_set.images, test_set.labels),
           callbacks=[TensorBoard(histogram_freq=1),
                      ModelCheckpoint(filepath=model_path+'.best', save_best_only=True, mode='min')])
    scores = wp.evaluate(test_set.images, test_set.labels, verbose=0)
    print('Test loss:', scores[0])
    print('Test accuracy:', scores[1])
    wp.model.save(model_path)
    saved_wp = wp.load_model(model_path)
    scores = saved_wp.evaluate(test_set.images, test_set.labels, verbose=0)
    print('Test loss:', scores[0])
    print('test accuracy:', scores[1])
    pred = saved_wp.predict(test_set.images, 1024)
    pred = numpy.reshape(pred, [-1])
    pred=numpy.array(pred)
    labels=numpy.squeeze(test_set.labels)
    result = numpy.array([pred, labels]).transpose()
    reslut=pd.DataFrame(result)
    reslut.to_csv('output.' + str(input_shape[0]), header=None, index=False)

if __name__ == '__main__':
    operation = "predict"
    if len(sys.argv) > 1:
        operation = sys.argv[1]
    if operation == "train":
        make_model([30, 61], 1, 512, lr=0.002,code="000001")
    elif operation == "predict":
        evaluate_model("model.30.best", "000001")
    else:
        print("Usage: gossip.py [train | predict]")
