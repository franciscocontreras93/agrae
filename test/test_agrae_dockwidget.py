# coding=utf-8
"""DockWidget test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'info@agrae.es'
__date__ = '2021-12-03'
__copyright__ = 'Copyright 2021,  aGrae Solutions, S.L.'

import unittest

from qgis.PyQt.QtGui import QDockWidget

from agrae_dockwidget import agraeDockWidget

from utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class agraeDockWidgetTest(unittest.TestCase):
    """Test dockwidget works."""

    def setUp(self):
        """Runs before each test."""
        self.dockwidget = agraeDockWidget(None)

    def tearDown(self):
        """Runs after each test."""
        self.dockwidget = None

    def test_dockwidget_ok(self):
        """Test we can click OK."""
        pass

if __name__ == "__main__":
    suite = unittest.makeSuite(agraeDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

