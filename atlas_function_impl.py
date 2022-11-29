# coding=utf-8
""""Atlas Export Function

.. note. This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2021-11-17'
__copyright__ = 'Copyright 2021, ItOpen'

import os

from qgis.core import (
    qgsfunction,
    QgsProject,
    QgsExpression,
    QgsExpressionFunction,
    QgsLayoutExporter,
    QgsExpressionFunction,
    QgsUnitTypes,
    QgsMessageLog,
)

from qgis.PyQt.QtCore import QTemporaryDir, QSize, QByteArray

class AtlasImageFunction(QgsExpressionFunction):

    def __init__(self):
        params = (
            QgsExpressionFunction.Parameter('feature_id', True, None),
            QgsExpressionFunction.Parameter('layout_name', True, None),
            QgsExpressionFunction.Parameter('layout_page', True, 1),
            QgsExpressionFunction.Parameter('image_format', True, 'PNG'),
            QgsExpressionFunction.Parameter('dpi', True, -1),
        )

        helpText = """
        <h3>function atlas_image</h3>
        <div class="description"><p>Renders an atlas page to an image and returns the binary content of the image.</p></div>
        <h4>Syntax</h4>
        <div class="syntax">
        <code><span class="functionname">atlas_image</span>([<span class="argument">feature_id</span>],[<span class="argument">layout_name</span>],[<span class="argument">layout_page</span>],[<span class="argument">image_format</span>],[<span class="argument">dpi</span>])</code>
        <br/><br/>[ ] marks optional components
        <h4>Arguments</h4>
        <div class="arguments">
        <table>
        <tr><td class="argument">feature_id</td><td>feature id (optional, defaults to the current feature id)</td></tr>
        <tr><td class="argument">layout_name</td><td>layout name (optional, defaults to the first layout)</td></tr>
        <tr><td class="argument">layout_page</td><td>layout page (optional, defaults to the first page)</td></tr>
        <tr><td class="argument">image_format</td><td>image format (optional, defaults to 'PNG', valid values: PNG, JPG, TIF)</td></tr>
        <tr><td class="argument">dpi</td><td>DPI (optional, defaults the DPI configured in the layout)</td></tr>
        </div>
        <h4>Examples</h4>
        <div class="examples">
        <ul>
        <li><code>atlas_image()</code> &rarr; <code>'PNG binary image'</code></li>
        <li><code>atlas_image(1, dpi:=72)</code> &rarr; <code>'PNG binary image' of feature 1 at 72 DPI</code></li>
        <li><code>atlas_image(1, 'a4_form', 2)</code> &rarr; <code>'PNG binary image' of feature 1 from second page of template 'a4_form'</code></li>
        </ul>
        </div>
        """

        super().__init__('atlas_image', params, 'Atlas', helpText=helpText)

    def func(self, args, context, parent, node):

        feature_id, layout_name, layout_page, image_format, dpi = args

        if feature_id is not None:
            try:
                feature_id = int(feature_id)
            except:
                return None
        else:
            feature = context.feature()
            if not feature.isValid():
                return None

            feature_id = feature.id()

        if layout_page is not None:
            try:
                layout_page = int(layout_page)
            except:
                return None
        else:
            layout_page = 1

        if dpi is None:
            dpi = -1

        try:
            dpi = int(dpi)
        except:
            return None

        if dpi < -1:
            return None

        if image_format is None:
            image_format = 'PNG'

        if image_format.upper() not in ('PNG', 'JPEG', 'JPG', 'TIFF', 'TIF'):
            return None

        p = QgsProject.instance()
        lm = p.layoutManager()

        if layout_name is not None:
            layout = lm.layoutByName(layout_name)
        else:
            if len(lm.layouts()) == 0:
                return None
            layout = lm.layouts()[0]

        if not layout:
            return None

        atlas = layout.atlas()
        if not atlas or not atlas.enabled():
            return None

        if layout_page > layout.pageCollection().pageCount():
            return None

        if dpi == -1:
            dpi = layout.renderContext().dpi()

        layoutSize = layout.pageCollection().page(layout_page - 1).sizeWithUnits()
        width = layout.convertFromLayoutUnits(layoutSize.width(), QgsUnitTypes.LayoutUnit.LayoutMillimeters)
        height = layout.convertFromLayoutUnits( layoutSize.height(), QgsUnitTypes.LayoutUnit.LayoutMillimeters )

        imageSize = QSize(int(width.length() * dpi / 25.4), int(height.length() * dpi / 25.4))

        if image_format.upper() == 'PNG':
            extension = 'png'
        elif image_format.upper().startswith('J'):
            extension = 'jpg'
        else:
            extension = 'tif'

        tmp_dir = QTemporaryDir()
        tmp_file = os.path.join(tmp_dir.path(), 'atlas.{}'.format(extension))

        exportSettings = QgsLayoutExporter.ImageExportSettings()
        exportSettings.dpi = dpi
        exportSettings.imageSize = imageSize
        exportSettings.pages.append(layout_page - 1)

        filter_expression = atlas.filterExpression()
        filter_features = atlas.filterFeatures()

        atlas.setFilterExpression('$id = {}'.format(feature_id))
        atlas.setFilterFeatures(True)

        atlas.beginRender()
        if atlas.next():
            exporter = QgsLayoutExporter(atlas.layout())
            exporter.exportToImage(tmp_file, exportSettings)
        else:
            atlas.endRender()
            atlas.setFilterExpression(filter_expression)
            atlas.setFilterFeatures(filter_features)
            return None

        atlas.endRender()

        with open(tmp_file, 'rb') as output:
            image = output.read()

        atlas.setFilterExpression(filter_expression)
        atlas.setFilterFeatures(filter_features)

        # QgsMessageLog.logMessage('Atlas exported {}'.format(len(image)))
        return QByteArray(image)

