from psikit import Psikit
from src.constants import *

def get_argument_suggestion(pool_processes=1):
    return {
        'threads' : max(1, AVAILABLE_CPU_COUNT // pool_processes), 
        'memory' : AVAILABLE_MEMORY_IN_GB / pool_processes
    }

def create_runner(pool_processes=1):
    return Psikit(**get_argument_suggestion(pool_processes))
