'''
Getline - A library to get text from the console
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: __linux_impl
Purpose: The linux implementation of getline
'''

class Getlines(object):

	def __init__(self, histfile='.hist'):
		pass

	def getline(self, prompt):
		return raw_input(prompt)
