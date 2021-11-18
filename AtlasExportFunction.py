# coding=utf-8
""""Atlas Export Plugin

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2021-11-17'
__copyright__ = 'Copyright 2021, ItOpen'

from qgis.core import QgsExpression

from .atlas_function_impl import AtlasImageFunction

class AtlasExportFunction():

    def __init__(self, iface):

        super().__init__()
        self.atlas_func = AtlasImageFunction()
        QgsExpression.registerFunction(self.atlas_func)


    def initGui(self):

        pass

    def unload(self):

        QgsExpression.unregisterFunction(self.atlas_func.name())
        del self.atlas_func

