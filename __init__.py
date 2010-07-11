'''
Getline - A library to get text from the console
Author: Tim Henderson
Contact: tim.tadh@hackthology.com
Copyright (c) 2010 All Rights Reserved.
Licensed under a BSD style license see the LICENSE file.

File: __init__
'''

__all__ = ['getline', 'excepts']
import platform, warnings
import excepts

if platform.system() == 'Linux':
	from __linux_impl import getline, Getlines
	pass
else:
	warnings.warn("Platform %s not supported." % platform.system())
	from __dumb_impl import getline, Getlines

del platform
del warnings
