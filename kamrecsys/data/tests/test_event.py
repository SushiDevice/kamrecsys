#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    division,
    absolute_import)
from six.moves import xrange

# =============================================================================
# Imports
# =============================================================================

from numpy.testing import (
    assert_array_equal,
    assert_array_less,
    assert_allclose,
    assert_array_max_ulp,
    assert_array_almost_equal_nulp)
import unittest

import os
import numpy as np

from kamrecsys.datasets import load_movielens_mini

# =============================================================================
# Module variables
# =============================================================================

# =============================================================================
# Functions
# =============================================================================


def load_test_data():
    from kamrecsys.data import EventWithScoreData
    from kamrecsys.datasets import SAMPLE_PATH

    infile = os.path.join(SAMPLE_PATH, 'pci.event')
    dtype = np.dtype([('event', 'U18', 2), ('score', np.float)])
    x = np.genfromtxt(fname=infile, delimiter='\t', dtype=dtype)
    data = EventWithScoreData(n_otypes=2, event_otypes=np.array([0, 1]))
    data.set_events(x['event'], x['score'], score_domain=(1.0, 5.0, 0.5))
    return data, x


# =============================================================================
# Test Classes
# =============================================================================


class TestEventUtilMixin(unittest.TestCase):

    def test_to_eid_event(self):
        data, x = load_test_data()

        # test to_eid_event
        check = data.to_eid_event(data.event)
        assert_array_equal(x['event'], check)

        # test to_eid_event / per line conversion
        check = np.empty_like(data.event, dtype=x['event'].dtype)
        for i, j in enumerate(data.event):
            check[i, :] = data.to_eid_event(j)
        assert_array_equal(x['event'], check)

    def test_to_iid_event(self):
        from kamrecsys.data import EventWithScoreData
        data, x = load_test_data()

        # test EventData.to_iid_event
        assert_array_equal(data.event, data.to_iid_event(x['event']))

        # test EventData.to_iid_event / per line conversion
        check = np.empty_like(x['event'], dtype=np.int)
        for i, j in enumerate(x['event']):
            check[i, :] = data.to_iid_event(j)
        assert_array_equal(data.event, check)


class TestEventData(unittest.TestCase):

    def test_filter_event(self):
        data = load_movielens_mini()

        data.filter_event(np.arange(data.n_events) % 3 == 0)
        assert_array_equal(
            data.event_feature, np.array(
            [(875636053,), (877889130,), (891351328,), (879362287,),
             (878543541,), (875072484,), (889751712,), (883599478,),
             (883599205,), (878542960,)], dtype=[('timestamp', '<i8')]))
        assert_array_equal(
            data.to_eid(0, data.event[:, 0]),
            [5, 10, 7, 8, 1, 1, 1, 6, 6, 1])
        assert_array_equal(
            data.to_eid(1, data.event[:, 1]),
            [2, 4, 8, 7, 9, 8, 5, 1, 9, 3])

# =============================================================================
# Main Routines
# =============================================================================

if __name__ == '__main__':
    unittest.main()
