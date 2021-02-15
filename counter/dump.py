#!/usr/bin/python
"""
Project : Project3
File Name: dump.py
Author: Venkata Pranathi Immaneni
Date: 21st Oct 2020
Email: ivpranathi@csu.fullerton.edu

"""


import requests

#get all the keys and values from session store
response = requests.get("http://localhost:5100")
if response.status_code != 200:
	print("API Error")

#Iterate each of the keys and display the key (session id) and corresponding values(counter values)
for key in response.json()['keys']:
	getval = requests.get("http://localhost:5100/"+key)
	print(getval.text)


