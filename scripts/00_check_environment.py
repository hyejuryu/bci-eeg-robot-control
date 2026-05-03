import sys
import platform

import numpy as np
import scipy
import pandas as pd
import matplotlib
import mne

print("Python:", sys.version)
print("Platform:", platform.platform())
print("NumPy:", np.__version__)
print("SciPy:", scipy.__version__)
print("Pandas:", pd.__version__)
print("Matplotlib:", matplotlib.__version__)
print("MNE:", mne.__version__)

print("\nEnvironment check complete.")
