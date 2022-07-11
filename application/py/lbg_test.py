#!/usr/bin/python
# coding: utf-8

# # Linde-Buzo-Gray Lib Tests
# 
# ## Generate codebooks of different size from fixed 3D-data

# In[2]:

from speech_features import lbg 

testdata = [(-1.5, 2.0, 5.0),
            (-2.0, -2.0, 0.0),
            (1.0, 1.0, 2.0),
            (1.5, 1.5, 1.2),
            (1.0, 2.0, 5.6),
            (1.0, -2.0, -2.0),
            (1.0, -3.0, -2.0),
            (1.0, -2.5, -4.5)]

for cb_size in (1, 2, 4, 8):
    print('generating codebook for size', cb_size)
    cb, cb_abs_w, cb_rel_w = lbg.generate_codebook(testdata, cb_size)
    print('output:')
    for i, c in enumerate(cb):
        print('> %s, abs_weight=%d, rel_weight=%f' % (c, cb_abs_w[i], cb_rel_w[i]))


# ## Generate codebook for random Gauss distribution

# In[8]:

import matplotlib.pyplot as plt

import random
from speech_features import lbg

get_ipython().magic('matplotlib inline')

N = 40   # population size
SIZE_CODEBOOK = 8

random.seed(0)

# generate random Gauss distribution with µ=0, sigma=1
population = [(random.gauss(0, 1), random.gauss(0, 1))
              for _ in range(N)]

# display population as blue crosses
plt.scatter([p[0] for p in population], [p[1] for p in population], marker='x', color='blue')

# generate codebook
get_ipython().magic('time cb, cb_abs_w, cb_rel_w = lbg.generate_codebook(population, SIZE_CODEBOOK)')

# display codebook as red filled circles
# codevectors with higher weight (more points near them) get bigger radius
plt.scatter([p[0] for p in cb], [p[1] for p in cb], s=[((w+1) ** 5) * 40 for w in cb_rel_w], marker='o', color='red')

plt.show()


# ## Generate codebook for population that is centered in several areas

# In[10]:

import random
import matplotlib.pyplot as plt

import lbg

get_ipython().magic('matplotlib inline')

NUM_AREAS = 8
NUM_POINTS_PER_AREA = 10
SIZE_CODEBOOK = 8
AREA_MIN_MAX = ((-20, 20), (-20, 20))

random.seed(0)

# create random centroids for NUM_AREAS areas
area_centroids = [(random.uniform(*AREA_MIN_MAX[0]), random.uniform(*AREA_MIN_MAX[1]))
                  for _ in range(NUM_AREAS)]

# display random centroids as orange cicles
plt.scatter([p[0] for p in area_centroids], [p[1] for p in area_centroids], marker='o', color='orange')

# create whole population
population = []
for c in area_centroids:
    # create random points around the centroid c
    area_points = [(random.gauss(c[0], 1.0), random.gauss(c[1], 1.0)) for _ in range(NUM_POINTS_PER_AREA)]
    population.extend(area_points)

# display the population as blue crosses
plt.scatter([p[0] for p in population], [p[1] for p in population], marker='x', color='blue')

# generate codebook
get_ipython().magic('time cb, cb_abs_w, cb_rel_w = lbg.generate_codebook(population, SIZE_CODEBOOK)')

# display codebook as red filled circles
# codevectors with higher weight (more points near them) get bigger radius
plt.scatter([p[0] for p in cb], [p[1] for p in cb], s=[((w+1) ** 5) * 40 for w in cb_rel_w], marker='o', color='red')

plt.show()


# In[ ]:



