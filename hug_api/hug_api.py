#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 12:18:46 2017

@author: metamatical
"""

import hug
import getMPmemberships
import getMPpersons
import MP_geoloc


@hug.extend_api()
def getMPs():
    
    return [MP_geoloc, getMPmemberships, getMPpersons]