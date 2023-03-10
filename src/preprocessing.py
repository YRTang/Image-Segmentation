# -*- coding: utf-8 -*-
"""preprocessing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QStxbjbCYFPeaVcOywSTl6MA6KnPpuEk

### Understand Run Length Encoding
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import skimage.io

def rle_encode(masked_image):
  pixel = masked_image.flatten()
  pixel = np.concatenate([[0], pixel, [0]]) 
  runs = np.where(pixel[1:] != pixel[:-1])[0] + 1
  runs[1::2] -= runs[::2]
  return " ".join(str(x) for x in runs)

test_mask = np.asarray([[0,0,0,0], [0,0,1,1], [0,0,1,1], [0,0,0,0]])
rle_encode(test_mask)

"""### Understanding Data"""

from glob import glob
from PIL import Image
import cv2

train_data = pd.read_csv('/content/drive/Shareddrives/CS 184A Project/train.csv')

train_data.head()

train_data[225:230]

train_images = glob('/content/drive/Shareddrives/CS 184A Project/train/*/*/*/*')

print(len(train_images))

print(train_images[0])

image = cv2.imread(train_images[0], cv2.IMREAD_UNCHANGED)
plt.imshow(image, cmap='gray')

image = cv2.imread('/content/drive/Shareddrives/CS 184A Project/train/case123/case123_day20/scans/slice_0030_266_266_1.50_1.50.png', cv2.IMREAD_UNCHANGED)
plt.imshow(image, cmap='gray')

image = cv2.imread('/content/drive/Shareddrives/CS 184A Project/train/case9/case9_day22/scans/slice_0068_360_310_1.50_1.50.png', cv2.IMREAD_UNCHANGED)
plt.imshow(image)

print(image.shape)

# reference: https://www.kaggle.com/code/paulorzp/rle-functions-run-lenght-encode-decode

def rle2mask(mask_rle, shape):
    '''
    mask_rle: run-length as string formated (start length)
    shape: (width,height) of array to return 
    Returns numpy array, 1 - mask, 0 - background

    '''
    if mask_rle == '':
        return np.zeros(shape[0] * shape[1], dtype=np.uint8).reshape(shape)
    s = mask_rle.split()
    starts, lengths = [np.asarray(x, dtype=int) for x in (s[0:][::2], s[1:][::2])]
    starts -= 1
    ends = starts + lengths
    img = np.zeros(shape[0]*shape[1], dtype=np.uint8)
    for lo, hi in zip(starts, ends):
        img[lo:hi] = 1
    return img.reshape(shape)

print(train_data.info())

train_seg = train_data.dropna()

print(train_seg.head())

print(train_seg['segmentation'].iloc[17])

mask_la = rle2mask(train_seg['segmentation'][33802], image.shape)
mask_sm = rle2mask(train_seg['segmentation'][33803], image.shape)
mask_st = rle2mask(train_seg['segmentation'][33804], image.shape)
print(mask_la)
print(mask_la.shape)
plt.imshow(mask_la)

plt.imshow(mask_sm)

plt.imshow(mask_st)

mask_stack = [mask_la, mask_sm, mask_st]
mask_all = np.stack(mask_stack, axis=0)
print(mask_all.shape)

mask_all = mask_la + mask_sm + mask_st
print(mask_all.shape)
plt.imshow(mask_all)

updated_train = pd.read_csv('/content/drive/Shareddrives/CS 184A Project/train_data.csv')
wu = updated_train['width'].unique()
print(wu)

"""### Data Preprocessing 

Create a new dataframe with paths of input images and combined masks in three different categories (stomache, large bowel, small bowel) as the labels of the images.
"""

train_fd_name = '/content/drive/Shareddrives/CS 184A Project/train'
train_fd = glob(train_fd_name)

print(train_data.head())

unique_ids = train_data['id'].unique()

columns = ['id', 'large_bowel_rle', 'small_bowel_rle', 'stomache_rle', 'image_path', 'height', 'width', 'h_pix_spacing', 'w_pix_spacing']
updated_train = pd.DataFrame(columns = columns)

for i in range(0,len(train_data),3):
  classes = {'large_bowel': '', 'small_bowel': '', 'stomach': ''}

  tr_i = train_data.loc[i, 'id'].split('_')

  case_fd = tr_i[0]
  day_fd = tr_i[0] + '_' + tr_i[1]
  slice_fl_prefix = tr_i[2] + '_' + tr_i[3]
  inc_fl = train_fd_name + '/' + case_fd + '/' + day_fd + '/scans/' + slice_fl_prefix
  image_path = glob(inc_fl + '*')[0]
  rest_info = image_path[len(inc_fl)+1:].rstrip('.png')
  rest_info = rest_info.split('_')
  height, width, h_pix_spacing, w_pix_spacing = rest_info

  for j in range(3):
    classes[train_data.loc[i+j, 'class']] = train_data.loc[i+j, 'segmentation']

  data = {
      'id': train_data.loc[i, 'id'],
      'large_bowel_rle': classes['large_bowel'],
      'small_bowel_rle': classes['small_bowel'],
      'stomache_rle': classes['stomach'],
      'image_path': image_path,
      'height': int(height),
      'width': int(width),
      'h_pix_spacing': float(h_pix_spacing),
      'w_pix_spacing': float(w_pix_spacing)
  }
  
  updated_train = updated_train.append(data, ignore_index=True)

  #j = json.dumps(data)
  #with open('train_data.json', 'a') as f:
  #  f.write(j)
  #  f.write('\n')

print(updated_train.head())

"""!!!DON'T RUN THE LINE BELOW!!!"""

import os  
updated_train.to_csv('/content/drive/Shareddrives/CS 184A Project/train_data.csv')

updated_train = pd.read_csv('/content/drive/Shareddrives/CS 184A Project/train_data.csv')

import os
os.mkdir('/content/drive/Shareddrives/CS 184A Project/label2')

"""!!!DON'T RUN THE LINE BELOW!!!"""

os.mkdir('/content/drive/Shareddrives/CS 184A Project/label')

path = r"/content/drive/Shareddrives/CS 184A Project/label"
for file_name in os.listdir(path):
    file = path + '/' + file_name
    os.remove(file)

"""Generate masks for images in .png format without differentiation of 3 classes"""

for i in range(len(updated_train)):
  if type(updated_train['large_bowel_rle'][i]) == float and type(updated_train['small_bowel_rle'][i]) == float and type(updated_train["stomache_rle"][i]) == float:
    continue
  else:
    print(i)
    image = cv2.imread(updated_train['image_path'][i], cv2.IMREAD_UNCHANGED)
    mask_la = np.zeros(image.shape[0] * image.shape[1], dtype=np.uint8).reshape(image.shape)
    mask_sm = np.zeros(image.shape[0] * image.shape[1], dtype=np.uint8).reshape(image.shape)
    mask_st = np.zeros(image.shape[0] * image.shape[1], dtype=np.uint8).reshape(image.shape)
    if type(updated_train['large_bowel_rle'][i]) != float:
      mask_la = rle2mask(updated_train['large_bowel_rle'][i], image.shape)
      plt.imshow(mask_la)
    if type(updated_train['small_bowel_rle'][i]) != float:
      mask_sm = rle2mask(updated_train['small_bowel_rle'][i], image.shape)
      plt.imshow(mask_sm)
    if type(updated_train['stomache_rle'][i]) != float:
      mask_st = rle2mask(updated_train['stomache_rle'][i], image.shape)
      plt.imshow(mask_st)
    plt.show()
    mask = mask_la + mask_sm + mask_st
    filename = '/content/drive/Shareddrives/CS 184A Project/label/' + updated_train['id'][i] + '.png'
    plt.imsave(filename, mask, cmap='gray')
    plt.clf()

import os

train_data = pd.read_csv("/content/drive/Shareddrives/CS 184A Project/train_data.csv")
print(train_data.head())

# 266*266, 276*276, 360*310, 234*234
img1 = np.zeros([266, 266, 3], dtype = np.uint8)
img2 = np.zeros([276, 276, 3], dtype = np.uint8)
img3 = np.zeros([360, 310, 3], dtype = np.uint8)
img4 = np.zeros([234, 234, 3], dtype = np.uint8)

fn1 = '/content/drive/Shareddrives/CS 184A Project/label/empty_266.png'
fn2 = '/content/drive/Shareddrives/CS 184A Project/label/empty_276.png'
fn3 = '/content/drive/Shareddrives/CS 184A Project/label/empty_360.png'
fn4 = '/content/drive/Shareddrives/CS 184A Project/label/empty_234.png'

plt.imsave(fn1, img1, cmap='gray')
plt.imsave(fn2, img2, cmap='gray')
plt.imsave(fn3, img3, cmap='gray')
plt.imsave(fn4, img4, cmap='gray')

img5 = np.zeros([200, 200, 3], dtype = np.uint8)
fn5 = '/content/drive/Shareddrives/CS 184A Project/empty_200.png'
plt.imsave(fn5, img5)

img5 = np.zeros([200, 200], dtype = np.uint8)
img6 = np.zeros([200, 200], dtype = np.uint8)
img7 = np.zeros([200, 200], dtype = np.uint8)
img_stack = [img5, img6, img7]
img_stack = np.stack(img_stack, axis=0)
print(img_stack.shape)
plt.imshow(img5, cmap='gray')

os.path.exists(fn2)

mask_paths = []
is_empty = []
for i in range(len(train_data)):
  mp = '/content/drive/Shareddrives/CS 184A Project/label/' + train_data["id"][i] + '.png'
  if os.path.exists(mp):
    mask_paths.append(mp)
    is_empty.append(False)
  else:
    is_empty.append(True)
    if train_data["height"][i] == 266 and train_data["width"][i] == 266:
      mask_paths.append(fn1)
    elif train_data["height"][i] == 276 and train_data["width"][i] == 276:
      mask_paths.append(fn2)
    elif train_data["height"][i] == 360 and train_data["width"][i] == 310:
      mask_paths.append(fn3)
    elif train_data["height"][i] == 234 and train_data["width"][i] == 234:
      mask_paths.append(fn4)
    
train_data['mask_path'] = mask_paths
train_data['empty'] = is_empty

print(train_data['empty'][65])

print(train_data.head())

one = '0001'
print(int(one))

cases, days, slices = [], [], []
for i in range(len(train_data)):
  sid = train_data['id'][i]
  info = sid.split('_')
  case, day, slic = int(info[0][4:]), int(info[1][3:]), int(info[3])
  cases.append(case)
  days.append(day)
  slices.append(slic)

train_data.insert(loc=2, column='case', value=cases)
train_data.insert(loc=3, column='day', value=days)
train_data.insert(loc=4, column='slice', value=slices)

print(train_data.head())

train_data.to_csv('/content/drive/Shareddrives/CS 184A Project/train_data2.csv')

"""#### Generate Stacked Labels

Generate 2D labeled images with 3 channels stored in .npy files
"""

import os
os.mkdir('/content/drive/Shareddrives/CS 184A Project/label2')

updated_train = pd.read_csv('/content/drive/Shareddrives/CS 184A Project/train_data.csv')
print(updated_train.head())

image = cv2.imread(updated_train['image_path'][74], cv2.IMREAD_UNCHANGED)
mask_la = np.zeros(image.shape[0] * image.shape[1], dtype=np.uint8).reshape(image.shape)
mask_sm = np.zeros(image.shape[0] * image.shape[1], dtype=np.uint8).reshape(image.shape)
mask_st = np.zeros(image.shape[0] * image.shape[1], dtype=np.uint8).reshape(image.shape)
#mask_la = rle2mask(updated_train['large_bowel_rle'][74], image.shape)
print(mask_la.shape)
plt.imshow(mask_la)

for i in range(len(updated_train)):
  print(i)
  image = cv2.imread(updated_train['image_path'][i], cv2.IMREAD_UNCHANGED)
  if type(updated_train['large_bowel_rle'][i]) == float:
    mask_la = np.zeros(image.shape[0] * image.shape[1], dtype=np.uint8).reshape(image.shape)
  else:
    mask_la = rle2mask(updated_train['large_bowel_rle'][i], image.shape)
  print(f"mask_la's shape: {mask_la.shape}")
  #plt.imshow(mask_la)
  #plt.show()
  if type(updated_train['small_bowel_rle'][i]) == float: 
    mask_sm = np.zeros(image.shape[0] * image.shape[1], dtype=np.uint8).reshape(image.shape)
  else:
    mask_sm = rle2mask(updated_train['small_bowel_rle'][i], image.shape)
  print(f"mask_sm's shape: {mask_sm.shape}")
  #plt.imshow(mask_sm)
  #plt.show()
  if type(updated_train["stomache_rle"][i]) == float:
    mask_st = np.zeros(image.shape[0] * image.shape[1], dtype=np.uint8).reshape(image.shape)
  else:
    mask_st = rle2mask(updated_train['stomache_rle'][i], image.shape)
  print(f"mask_st's shape: {mask_st.shape}")
  #plt.imshow(mask_st)
  #plt.show()

  mask_stack = [mask_la, mask_sm, mask_st]
  mask_all = np.stack(mask_stack, axis=2)
  print(f"mask_all's shape: {mask_all.shape}")

  filename = '/content/drive/Shareddrives/CS 184A Project/label2/' + updated_train['id'][i]
  np.save(filename, mask_all)
  plt.clf()

train_data2 = pd.read_csv("/content/drive/Shareddrives/CS 184A Project/train_data2.csv")
print(train_data2.head())

train_data2 = train_data2.drop('mask_path', axis=1)

print(train_data2.head())

mask_paths = []
for i in range(len(train_data2)):
  mp = '/content/drive/Shareddrives/CS 184A Project/label2/' + train_data2["id"][i] + '.npy'
  mask_paths.append(mp)
train_data2.insert(loc=14, column='mask_path', value=mask_paths)

print(train_data2.head())

print(train_data2['mask_path'][513])

train_data2.to_csv('/content/drive/Shareddrives/CS 184A Project/train_data3.csv')

#path = r"/content/drive/Shareddrives/CS 184A Project/label2"
#for file_name in os.listdir(path):
    #file = path + '/' + file_name
    #os.remove(file)