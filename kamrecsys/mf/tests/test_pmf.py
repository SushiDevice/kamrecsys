#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from numpy.testing import assert_array_equal, assert_array_almost_equal
import unittest

##### Test Classes #####

class TestEventScorePredictor(unittest.TestCase):

    def test_class(self):
        import numpy as np
        from ...datasets import load_movielens_mini
        from ..pmf import EventScorePredictor

        np.random.seed(1234)
        data = load_movielens_mini()

        with self.assertRaises(ValueError):
            EventScorePredictor(C=0.1, k=0)

        recommender = EventScorePredictor(C=0.1, k=2)
        self.assertDictEqual(
            vars(recommender),
                {'C': 0.1, 'n_otypes': 0, 'bu_': None, 'bi_': None, 'k': 2,
                 'p_': None, 'q_': None, '_coef': None, 'f_loss_': np.inf,
                 'iid': None, 'i_loss_': np.inf, 'eid': None,
                 'n_objects': None, '_dt': None, 'mu_': None})

        recommender.fit(data, disp=False, gtol=1e-03)

        self.assertAlmostEqual(recommender.i_loss_,
                               0.74652578358324106, places=5)
        self.assertAlmostEqual(recommender.f_loss_,
                               0.025638738121075231, places=5)

        self.assertAlmostEqual(recommender.predict((1, 7)),
                               3.9873641434545979, places=5)
        self.assertAlmostEqual(recommender.predict((1, 9)),
                               4.9892118821609106, places=5)
        self.assertAlmostEqual(recommender.predict((1, 11)),
                               3.6480799850368273, places=5)
        self.assertAlmostEqual(recommender.predict((3, 7)),
                               3.6336318795279228, places=5)
        self.assertAlmostEqual(recommender.predict((3, 9)),
                               4.2482001235634943, places=5)
        self.assertAlmostEqual(recommender.predict((3, 11)),
                               3.7236984083417841, places=5)
        self.assertAlmostEqual(recommender.predict((5, 7)),
                               3.4141968145802597, places=5)
        self.assertAlmostEqual(recommender.predict((5, 9)),
                               3.9818882049478654, places=5)
        self.assertAlmostEqual(recommender.predict((5, 11)),
                               3.4710520150321895, places=5)
        x = np.array([[1, 7], [1, 9], [1, 11],
            [3, 7], [3, 9], [3, 11],
            [5, 7], [5, 9], [5, 11]])
        assert_array_almost_equal(
            recommender.predict(x),
            [3.98736414, 4.98921188, 3.64807999, 3.63363188, 4.24820012,
             3.72369841, 3.41419681, 3.9818882, 3.47105202])

##### Main routine #####
if __name__ == '__main__':
    unittest.main()