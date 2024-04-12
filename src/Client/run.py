from multiprocessing import *

from src.constants import *
from src.Tools.utils import *
from src.Client import system_pb2, system_pb2_grpc

import sys
import json
import time
import rdkit
from rdkit import Chem

channel = system_pb2_grpc.grpc.insecure_channel(f'{CURRENT_SERVER_IP}:50051')
stub = system_pb2_grpc.EnergyCalculationStub(channel)

def take_task_process_write_loop(args):
    process_id, worker_count = args

    print(f"[Process {process_id}] Worker initialized.", flush=True)
    psikit_driver = create_runner(worker_count)
    metadata = [("authorization", f"Bearer {CLIENT_UUID}")]

    while True:
        sleep_time = FAILURE_SLEEP_TIME

        try:
            response = stub.GetTask(
                system_pb2.GetTaskRequest(client_identifier=CLIENT_UUID), 
                metadata=metadata
            )

            if response.status != system_pb2.SUCCESS:
                status = None

                if response.status == system_pb2.TRY_LATER:
                    sleep_time = FAILURE_SLEEP_TIME
                    status = "TRY_LATER"
                elif response.status == system_pb2.INTERNAL_ERROR:
                    sleep_time = 2 * FAILURE_SLEEP_TIME
                    status = "INTERNAL_ERROR"

                raise Exception(f"Server Responded With {status} status, cause - {response.task_content}")

            task_id = response.task_identifier
            print(f"[Process {process_id}] Received Task with ID:", task_id, flush=True)

            task_content = json.loads(response.task_content)
            energy_conf = task_content.get("energy_conf", DEFAULT_ENERGY_CONF)
            mol_blocks = task_content["mol_blocks"]
            results = []

            for (id, block) in enumerate(mol_blocks):
                try:
                    psikit_driver.mol = Chem.MolFromMolBlock(block, removeHs=False)
                    energy = psikit_driver.energy(**energy_conf)
                    print(f"[Process {process_id}] Calculated Energy for Conformation #{id}:", energy)
                    results.append(energy)
                except Exception as ex:
                    results.append(str(ex))

            stub.PutResult(
                system_pb2.PutResultRequest(task_identifier=task_id, 
                                            results=json.dumps(results)),
                metadata=metadata)
            
            sleep_time = SUCCESS_SLEEP_TIME
        except Exception as ex:
            print(f"[Process {process_id}] Error: {ex}", flush=True)

        time.sleep(sleep_time)

class ClientManager:
    def __init__(self):
        self.worker_count = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_WORKER_COUNT
        self.process_pool = Pool(processes=self.worker_count)

    def start(self):
        args = [(i, self.worker_count) for i in range(self.worker_count)]
        self.process_pool.map(take_task_process_write_loop, args)

if __name__ == "__main__":
    manager = ClientManager()
    manager.start()
