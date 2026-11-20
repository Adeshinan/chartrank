"""ChartRank: suggests and explains the right chart for your data and intent."""

from chartrank.gallery import Chart, Gallery, suggest
from chartrank.profile import profile

__version__ = "0.1.0"

__all__ = ["Chart", "Gallery", "__version__", "profile", "suggest"]
