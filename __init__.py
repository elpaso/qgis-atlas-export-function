# coding=utf-8
""""Atlas Export Function

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2021-11-17'
__copyright__ = 'Copyright 2021, ItOpen'



def classFactory(iface):
    from .AtlasExportFunction import AtlasExportFunction
    return AtlasExportFunction(iface)
