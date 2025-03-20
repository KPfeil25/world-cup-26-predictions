"""
This file contains unit tests for the UI.
"""

import sys
import os
import unittest
from streamlit.testing.v1 import AppTest

class TestStreamlitApp(unittest.TestCase):
    """
    Unit tests for the UI.
    """

    @classmethod
    def setUpClass(cls):
        """
        This setup function is necessary so that AppTest knows where to look
        to find the modules that it needs
        """
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.insert(0, project_root)

    def test_streamlit_homepage(self):
        """
        Unit tests for the homepage UI
        """
        app = AppTest.from_file("../Homepage.py", default_timeout=10).run()
        assert not app.exception
        assert app.markdown[0].value == "# World Cup 2026 Analysis and Predictions ⚽️"

    def test_analytics_page(self):
        """
        Unit tests for the analytics page
        """
        app = AppTest.from_file("../pages/analysis_tool.py", default_timeout=10).run()
        assert app.title[0].value == "World Cup 2026 Player Analytics"
        assert len(app.header) == 1
        assert app.header[0].value == "Player Analytics"

    def test_predictions_page(self):
        """
        Unit tests for the predictions page
        """
        app = AppTest.from_file("../pages/prediction_tool.py", default_timeout=10).run()
        assert len(app.button) == 1
        assert len(app.header) == 1
        assert app.markdown[0].value == "# World Cup 2026 Prediction Tool"

if __name__ == "__main__":
    unittest.main()
