"""Various helpers for backwards and forwards compatibility."""

import numpy as np

np_trapezoid = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
