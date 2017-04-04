#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Recommenders: abstract classes
"""

from __future__ import (
    print_function,
    division,
    absolute_import,
    unicode_literals)
from six.moves import xrange

# =============================================================================
# Imports
# =============================================================================

import logging
from abc import ABCMeta, abstractmethod
from six import with_metaclass
import numpy as np
import scipy.sparse as sparse
from sklearn.base import BaseEstimator
from sklearn.utils import check_random_state, check_array

from .data import BaseData, EventData, EventWithScoreData, EventUtilMixin

# =============================================================================
# Module metadata variables
# =============================================================================

# =============================================================================
# Public symbols
# =============================================================================

__all__ = ['BaseRecommender',
           'BaseEventRecommender',
           'BaseEventItemFinder',
           'BaseEventScorePredictor']

# =============================================================================
# Constants
# =============================================================================

# =============================================================================
# Module variables
# =============================================================================

# =============================================================================
# Classes
# =============================================================================


class BaseRecommender(with_metaclass(ABCMeta, BaseEstimator)):
    """
    Abstract class for all recommenders

    Attributes
    ----------
    n_otypes : int
        the number of object types, succeed from training data sets
    n_objects : array_like, shape=(n_otypes), dtype=int
        the number of different objects in each type, succeed from training
        data sets
    eid : array_like, shape=(n_otypes,), dtype=(array_like)
        conversion table to external ids, succeed from training data sets
    iid : dictionary
        conversion table to internal ids, succeed from training data sets
    fit_results_ : dict
        Side information about results of fitting
    random_state : RandomState or an int seed (None by default)
        A random number generator instance

    Raises
    ------
    ValueError
        if n_otypes < 1
    """

    def __init__(self, random_state=None):
        self.n_otypes = 0
        self.n_objects = None
        self.eid = None
        self.iid = None
        self.random_state = random_state
        self._rng = None
        self.fit_results_ = {}

    def fit(self, random_state=None):
        """
        fitting model

        Parameters
        ----------
        random_state: RandomState or an int seed (None by default)
            A random number generator instance
        """

        # set random state
        if random_state is None:
            random_state = self.random_state
        self._rng = check_random_state(random_state)

    @abstractmethod
    def predict(self, eev, **kwargs):
        """
        abstract method: predict score of given event represented by external
        ids

        Parameters
        ----------
        eev : array_like, shape=(s_event,) or (n_events, s_event)
            events represented by external id

        Returns
        -------
        sc : float or array_like, shape=(n_events,), dtype=float
            predicted scores for given inputs
        """
        pass

    def to_eid(self, otype, iid):
        """
        convert an internal id to the corresponding external id
        (Copied from data.BaseData)

        Parameters
        ----------
        otype : int
            object type
        iid : int
            an internal id

        Returns
        -------
        eid : int
            the corresponding external id
        
        Raises
        ------
        ValueError
            an internal id is out of range
        """
        try:
            return self.eid[otype][iid]
        except IndexError:
            raise ValueError("Illegal internal id")

    def to_iid(self, otype, eid):
        """
        convert an external id to the corresponding internal id.
        (Copied from data.BaseData)

        Parameters
        ----------
        otype : int
            object type
        eid : int
            an external id
        
        Returns
        -------
        iid : int
            the corresponding internal id
        
        Raises
        ------
        ValueError
            an external id is out of range
        """
        try:
            return self.iid[otype][eid]
        except KeyError:
            raise ValueError("Illegal external id")

    def _set_object_info(self, data):
        """
        import object meta information of input data to recommenders

        Parameters
        ----------
        data : :class:`kamrecsys.data.BaseData`
            input data
        
        Raises
        ------
        TypeError
            if input data is not :class:`kamrecsys.data.BaseData` class
        """
        if not isinstance(data, BaseData):
            raise TypeError("input data must data.BaseData class")

        self.n_otypes = data.n_otypes
        self.n_objects = data.n_objects
        self.eid = data.eid
        self.iid = data.iid


class BaseEventRecommender(
        with_metaclass(ABCMeta, BaseRecommender, EventUtilMixin)):
    """
    Recommenders using a data.EventData class or its subclasses
    
    Attributes
    ----------
    event_otypes : array_like, shape=(variable,), optional
        see attribute event_otypes. as default, a type of the i-th element of
        each event is the i-th object type.
    s_event : int
        the size of event, which is the number of objects to represent a
        rating event
    """

    def __init__(self, random_state=None):
        super(BaseEventRecommender, self).__init__(random_state=random_state)

    def _set_event_info(self, data):
        """
        import event meta information of input data to recommenders

        Parameters
        ----------
        data : :class:`kamrecsys.data.EventData`
            input data

        Raises
        ------
        TypeError
            if input data is not :class:`kamrecsys.data.EventData` class
        """
        if not isinstance(data, EventData):
            raise TypeError("input data must data.EventData class")

        self.event_otypes = data.event_otypes
        self.s_event = data.s_event

    def fit(self, random_state=None):
        """
        fitting model
        """
        super(BaseEventRecommender, self).fit(random_state=random_state)

    @abstractmethod
    def raw_predict(self, ev, **kwargs):
        """
        abstract method: predict score of given one event represented by
        internal ids

        Parameters
        ----------
        ev : array_like, shape=(n_events, s_event)
            events represented by internal id

        Returns
        -------
        sc : float or array_like, shape=(n_events,), dtype=float
            predicted scores for given inputs
        """

    def predict(self, eev):
        """
        predict score of given event represented by external ids

        Parameters
        ----------
        eev : array_like, shape=(s_event,) or (n_events, s_event)
            events represented by external id

        Returns
        -------
        sc : float or array_like, shape=(n_events,), dtype=float
            predicted scores for given inputs
        """

        eev = check_array(np.atleast_2d(eev), dtype=int)
        if eev.shape[1] != self.s_event:
            raise TypeError("unmatched sized of events")

        return np.squeeze(self.raw_predict(self.to_iid_event(eev)))


class BaseEventItemFinder(with_metaclass(ABCMeta, BaseEventRecommender)):
    """
    Recommenders to find good items from event data
    """

    def __init__(self, random_state=None):
        super(BaseEventItemFinder, self).__init__(
            random_state=random_state)

    def fit(self, random_state=None):
        """
        fitting model
        """
        super(BaseEventItemFinder, self).fit(random_state=random_state)

    def _get_event_array(self, data, event_index=(0,1), sparse_type='csr'):
        """
        Set statistics of input dataset, and generate a matrix representing
        implicit feedbacks.

        Parameters
        ----------
        data : :class:`kamrecsys.data.EventData`
            data to fit
        event_index : array_like, shape=(variable,)
            a set of indexes to specify the elements in events that are used
            in a recommendation model
        sparse_type: str
            type of sparse matrix: 'csr', 'csc', 'lil', or 'array'
            default='csr'

        Returns
        -------
        event_array: array, shape=(n_users, n_items), dtype=int
            return rating matrix that takes 1 if it is consumed, 0 otherwise.
            if event data are not available, return None
        n_objects : array_like, shape=(event_index.shape[0],), dtype=int
            the number of objects corresponding to elements tof an extracted
            events
        """

        # varidity of arguments
        if sparse_type not in ['csr', 'csc', 'lil', 'array']:
            raise TypeError("illigal type of sparse matrices")

        if not isinstance(data, EventData):
            raise TypeError("input data must data.EventData class")

        # import meta information of objects and events to this recommender
        self._set_object_info(data)
        self._set_event_info(data)
        event_index = np.asarray(event_index)

        # get number of objects
        n_objects = self.n_objects[self.event_otypes[event_index]]

        # get event data
        users = data.event[:, event_index[0]]
        items = data.event[:, event_index[1]]
        scores = np.ones_like(users, dtype=int)

        # generate array
        event = sparse.coo_matrix((scores, (users, items)), shape=n_objects)
        if sparse_type == 'csc':
            event = event.tocsc()
        elif sparse_type == 'csr':
            event = event.tocsr()
        elif sparse_type == 'lil':
            event = event.tolil()
        else:
            event = event.toarray()

        return event, n_objects


class BaseEventScorePredictor(with_metaclass(ABCMeta, BaseEventRecommender)):
    """
    Recommenders to predict preference scores from event data
    """

    def __init__(self, random_state=None):
        super(BaseEventScorePredictor, self).\
            __init__(random_state=random_state)

    def fit(self, random_state=None):
        """
        fitting model
        """
        super(BaseEventScorePredictor, self).fit(random_state=random_state)

    def _get_event_and_score(self, data, event_index, score_index):
        """
        Parameters
        ----------
        data : :class:`kamrecsys.data.EventWithScoreData`
            data to fit
        event_index : array_like, shape=(variable,)
            a set of indexes to specify the elements in events that are used in
            a recommendation model
        score_index : int
            Ignored if score of data is a single criterion type. In a multi-
            criteria case, specify the position of the target score in a score
            vector. (default=0)

        Returns
        -------
        event : array_like, shape=(n_events, event_index.shape[0])
            an extracted set of events
        score : array_like, shape=(n_events,)
            scores for each event
        n_objects : array_like, shape=(event_index.shape[0],), dtype=int
            the number of objects corresponding to elements tof an extracted
            events

        Raises
        ------
        TypeError
            if input data is not :class:`kamrecsys.data.EventWithScoreData`
            class
        """
        if not isinstance(data, EventWithScoreData):
            raise TypeError("input data must data.EventWithScoreData class")

        # import meta information of objects and events to this recommender
        self._set_object_info(data)
        self._set_event_info(data)
        event_index = np.asarray(event_index)

        # get event data
        event = np.atleast_2d(data.event)[:, event_index]

        # get score information
        if data.n_stypes == 1:
            score = data.score
        else:
            score = data.score[:, score_index]

        # get number of objects
        n_objects = self.n_objects[self.event_otypes[event_index]]

        return event, score, n_objects

# =============================================================================
# Functions
# =============================================================================

# =============================================================================
# Module initialization
# =============================================================================

# init logging system ---------------------------------------------------------
logger = logging.getLogger('kamrecsys')
if not logger.handlers:
    logger.addHandler(logging.NullHandler())

# =============================================================================
# Test routine
# =============================================================================


def _test():
    """ test function for this module
    """

    # perform doctest
    import sys
    import doctest

    doctest.testmod()

    sys.exit(0)

# Check if this is call as command script -------------------------------------

if __name__ == '__main__':
    _test()
