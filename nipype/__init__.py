"""
Nipype provides imaging Python interfaces and an analysis pipeline.
"""
import os

__version__ = '0.9.0.pre'
"""The major.minor.patch[.extra] version designator. An empty *extra*
qualifier corresponds to a production release. Other *extra* qualifiers
signify a development release.
"""

from .utils.config import NipypeConfig
config = NipypeConfig()
from .utils.logger import Logging
logging = Logging(config)

from .fixes.numpy.testing import nosetester

# Set up package information function
from .pkg_info import get_pkg_info as _get_pkg_info
get_info = lambda: _get_pkg_info(os.path.dirname(__file__))

from .pipeline import Node, MapNode, JoinNode, Workflow
from .interfaces import (fsl, spm, freesurfer, afni, ants, slicer, dipy, nipy,
                         mrtrix, camino, DataGrabber, DataSink, SelectFiles,
                         IdentityInterface, Rename, Function, Select, Merge)
