from multiprocessing import *

from src.constants import *
from src.Tools.utils import *
from src.gRPC import system_pb2, system_pb2_grpc

import sys
import time
import grpc
import json
from rdkit import Chem

channel = grpc.insecure_channel(f'{SERVER_IP}:50051')
stub = system_pb2_grpc.SDDFactoryStub(channel)

def take_task_process_write_loop(args):
    process_id, worker_count = args

    scratch_dir = REPO_DIR / "scratches" / f"{process_id}"

    os.makedirs(scratch_dir, exist_ok=True)
    os.environ["PSI_SCRATCH"] = scratch_dir.as_posix()

    os.chdir(scratch_dir)

    print(f"[Process {process_id}] Worker initialized.", flush=True)
    psikit_driver = create_runner(worker_count)
    metadata = [("authorization", f"Bearer {TOKEN}")]

    while True:
        sleep_time = FAILURE_SLEEP_TIME

        try:
            response = stub.GetTask(
                system_pb2.GetTaskRequest(client_identifier=CLIENT_ID), 
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

                raise Exception(f"Server Responded With {status} status, cause - {response.task.task_content}")

            task_id = response.task.task_identifier
            print(f"[Process {process_id}] Received Task with ID:", task_id, flush=True)

            mol_block = response.task.task_content
            psikit_driver.mol = Chem.MolFromMolBlock(mol_block, removeHs=False)
            id_mapping = get_obj_to_block_mapping(psikit_driver.mol, mol_block)

            results = {}

            if response.task.task_type != system_pb2.NONE:
                try:
                    energy = psikit_driver.energy(**DEFAULT_CONF)
                    if (response.task.task_type & system_pb2.ENERGY) > 0:
                        results["energy"] = energy

                    if (response.task.task_type & system_pb2.RESP_CHARGES) > 0:
                        try:
                            resp_charges = psikit_driver.calc_resp_charges()[id_mapping]
                            print("Calculating charges")
                            results["resp_charges"] = list(resp_charges)
                        except Exception as ex:
                            print(f"[Process {process_id}] Error during RESP charges calculation: {ex}", flush=True)
                except Exception as ex:
                    print(f"[Process {process_id}] Error during task consumption: {ex}", flush=True)


            response = stub.PutResult(
                system_pb2.PutResultRequest(status=system_pb2.SUCCESS,
                                            task_result=system_pb2.TaskResult(
                                                task_type=response.task.task_type,
                                                task_identifier=task_id, 
                                                task_result=json.dumps(results))),
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
