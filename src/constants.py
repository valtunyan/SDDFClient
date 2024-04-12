import psutil
import uuid
import os

# Use half of both memory and compute resources
# ! You can update these constants, based on your preferences
AVAILABLE_MEMORY_IN_GB = psutil.virtual_memory().total / (1024 ** 3) // 2
AVAILABLE_CPU_COUNT = os.cpu_count() // 2

# Divide by two for each task to use at least 3 threads
DEFAULT_WORKER_COUNT = max(1, AVAILABLE_CPU_COUNT // 3)
DEFAULT_ENERGY_CONF = {'basis_sets' : 'wB97x/6-31G(d)'}

SUCCESS_SLEEP_TIME = 10
FAILURE_SLEEP_TIME = 60

CLIENT_UUID = str(uuid.uuid4())

CURRENT_SERVER_IP = "34.125.252.122"
