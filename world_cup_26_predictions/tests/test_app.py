import sys
import os
import unittest
from streamlit.testing.v1 import AppTest

class TestStreamlitApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.insert(0, project_root)

    def test_streamlit_homepage(self):
        app = AppTest.from_file("../Homepage.py").run()
        assert not app.exception
        assert app.markdown[0].value == "# World Cup 2026 Analysis and Predictions ⚽️"

    def test_analytics_page(self):
        app = AppTest.from_file("../pages/analysis_tool.py").run()
        assert app.title[0].value == "World Cup 2026 Player Analytics"
        assert len(app.header) == 2
        assert app.header[0].value == "Player Analytics"
        assert app.header[1].value == "Team Analytics"
        assert len(app.selectbox) == 3
        assert app.selectbox._list[0].label == "Filter by Gender:"
        assert app.selectbox._list[1].label == "Filter by Continent:"
        assert app.selectbox._list[2].label == "Filter by Position:"

if __name__ == "__main__":
    unittest.main()
