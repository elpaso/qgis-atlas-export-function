# coding=utf-8
""""Atlas Export Function Test

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2021-11-18'
__copyright__ = 'Copyright 2021, ItOpen'

import os

from unittest import TestCase, main, skipIf, main

from atlas_function_impl import AtlasImageFunction

from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsExpression,
    QgsExpressionContext,
)

from qgis.PyQt.QtGui import QImage, QColor
from qgis.PyQt.QtCore import QTemporaryDir, QSize

class AtlasFunctionTest(TestCase):

    @classmethod
    def setUpClass(cls):

        cls.qgs = QgsApplication([], False)
        cls.qgs.initQgis()
        cls.atlas_func = AtlasImageFunction()
        QgsExpression.registerFunction(cls.atlas_func)
        QgsProject.instance().read(os.path.join(os.path.dirname(__file__), 'data', 'project.qgs'))

    @classmethod
    def tearDownClass(cls):

        cls.qgs.exitQgis()

    def _test_color(self, image_data, extension, expected_color):

        tmp_dir = QTemporaryDir()
        tmp_path = os.path.join(tmp_dir.path(), 'out.' + extension)
        with open(tmp_path, 'wb+') as out_file:
            out_file.write(image_data)

        img = QImage(tmp_path)
        color = img.pixelColor(int(img.size().width() / 2), int(img.size().height() / 2))
        self.assertEqual(color.red(), expected_color[0])
        self.assertEqual(color.green(), expected_color[1])
        self.assertEqual(color.blue(), expected_color[2])
        return img

    def test_func(self):

        args = (1, 'layout_one', 1, 'PNG', 20)
        image_data = self.atlas_func.func(args, None, None, None)
        self.assertIsNotNone(image_data)
        self._test_color(image_data, 'png', [255, 0, 0])

        args = (0, 'layout_one', 1, 'PNG', 20)
        image_data = self.atlas_func.func(args, None, None, None)
        self.assertIsNotNone(image_data)
        self._test_color(image_data, 'png', [0, 0, 255])

        args = (None, None, None, None, None)
        context = QgsExpressionContext()
        context.setFeature(QgsProject.instance().mapLayersByName('data')[0].getFeature(0))
        image_data = self.atlas_func.func(args, context, None, None)
        self.assertIsNotNone(image_data)
        self._test_color(image_data, 'png', [0, 0, 255])

    def test_expression(self):

        context = QgsExpressionContext()

        feature_id = 1
        layout_name='layout_one'

        valid, error = QgsExpression.checkExpression('atlas_image({feature_id}, \'{layout_name}\', dpi:=20)'.format(feature_id=feature_id, layout_name=layout_name), context)
        self.assertTrue(valid, error)

        exp = QgsExpression('atlas_image({feature_id}, \'{layout_name}\', dpi:=96)'.format(feature_id=feature_id, layout_name=layout_name))
        image_data = exp.evaluate(context)
        self.assertIsNotNone(image_data)
        img = self._test_color(image_data, 'png', [255, 0, 0])
        self.assertEqual(img.size(), QSize(1066, 753))

        feature_id = 0
        exp = QgsExpression('atlas_image({feature_id}, \'{layout_name}\', dpi:=72)'.format(feature_id=feature_id, layout_name=layout_name))
        image_data = exp.evaluate(context)
        self.assertIsNotNone(image_data)
        img = self._test_color(image_data, 'png', [0, 0, 255])
        self.assertEqual(img.size(), QSize(799, 565))

        # Test invalid args
        self.assertIsNone(QgsExpression('atlas_image(2, \'layout_one\')').evaluate(context))
        self.assertIsNone(QgsExpression('atlas_image(0, \'layout_undefined\')').evaluate(context))
        self.assertIsNone(QgsExpression('atlas_image(0, \'layout_one\', image_format:=\'unsupported\')').evaluate(context))
        self.assertIsNone(QgsExpression('atlas_image(0, \'layout_one\', layout_page:=2)').evaluate(context))

        # Test no args and feature in context
        exp = QgsExpression('atlas_image()')
        context.setFeature(QgsProject.instance().mapLayersByName('data')[0].getFeature(0))
        image_data = exp.evaluate(context)
        self.assertIsNotNone(image_data)
        img = self._test_color(image_data, 'png', [0, 0, 255])
        self.assertEqual(img.size(), QSize(3331, 2355))


if __name__ == '__main__':
    main()

