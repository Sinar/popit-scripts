#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import hug
import getMPmemberships
import getMPpersons
import MP_geoloc


@hug.extend_api()
def getMPs():
    
    return [MP_geoloc, getMPmemberships, getMPpersons]
