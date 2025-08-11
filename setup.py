from distutils.core import setup
import py2exe

setup(
    options={'py2exe': {'compressed': True}},
    windows=[{
        'script': 'daily_journal_pyqt6.py',
        'icon_resources': [(1, 'Assets/TourminalIcon.ico')]
    }]
)
