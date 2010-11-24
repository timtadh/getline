'''
Getline - A library to get text from the console
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: abstract
Purpose: The abstract interface
'''

class AbstractGetlines(object):

	def __init__(self, histfile=None):
		self.histfile = histfile

	def getline(self, prompt=''):
		pass