#!/usr/bin/env python
 
from distutils.core import setup
 
setup(name = "evecal",
    version = '0.1',
    description = "EVE API Calendar abstraction library",
    author = "Andrew Williams",
    author_email = "andy@tensixtyone.com",
    url = "https://github.com/nikdoof/evecal/",
    keywords = "eve api eveonline calendar ics",
    py_modules = ['evecal',],
    scripts = ['scripts/evetoics'],
)
