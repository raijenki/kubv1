# This launcher script is supposed to replace application calls and forward SIGTERM signals to them
import time
import signal
import os
import sys
import time
import subprocess
import shlex
import shutil
from concurrent import futures
from multiprocessing import Process
import logging
import grpc
import mpi_monitor_pb2
import mpi_monitor_pb2_grpc

STOP_TIMEOUT = 20
app = None
app_ssh = None
MPI_HOST = None
startedRanks = 0
concludedRanks = 0
#MASTER_CMD = "mpiexec --allow-run-as-root -wdir /home/hpc-tests/cm1/ --host " +  str(MPI_HOST) + " -np 4 /home/hpc-tests/cm1/cm1.exe"
WORKER_CMD = "/usr/sbin/sshd -D"

#
# Signal handling
#
def signal_handler(sig, _frame):
    """Handling the SIGTERM event"""
    print(f'Received signal {sig} - stopping gracefully in 30 seconds')
    os.killpg(os.getpgid(app.pid), sig)
    count = STOP_TIMEOUT
    while count > 0:
        time.sleep(1)
        count -= 1
    print('Finished cleanup...')
#
# This deals with gRPC protocols
#
class Monitor(mpi_monitor_pb2_grpc.MonitorServicer):
    # This is to react according to how scheduler sends the scaling message to us
    def Scale(self, request, context):
        global app
        global startedRanks
        startedRanks = startedRanks + request.additionalNodes

        # SIGTERM the app
        os.killpg(os.getpgid(app.pid), signal.SIGTERM)
        # Wait few seconds so app can deal with whatever it needs
        count = 30
        while count > 0:
            time.sleep(1)
            count -= 1
        os.killpg(os.getpgid(app.pid), signal.SIGKILL) # Kill it
        app.wait() # Wait the app to be killed

        checkpoint() # Checkpoint, applicantion-based
        wait_signal()
        start_mpi() # Restart our mpi job
        return mpi_monitor_pb2.Confirmation(confirmMessage='All jobs are stopped, waiting for new replicas!', confirmId=1)

    def JobInit(self, request, context):
        global startedRanks
        startedRanks += 1
        return mpi_monitor_pb2.Confirmation(confirmMessage='Job is confirmed as started!', confirmId=2)

    def RetrieveKeys(self, request, context):
        with open("/root/.ssh/authorized_keys", "r") as auth_keys:
            key = auth_keys.readlines()
        return mpi_monitor_pb2.SSHKeys(pubJobKey=key, confirmId=3)

    def activeServer(self, request, context):
        return mpi_monitor_pb2.Confirmation(confirmMessage='Server is active!', confirmId=4)

def getNumberOfRanks():
    with open("/root/mpiworker.host", 'r') as fp:
        length = len(fp.readlines())
    return length

def copyRanks():
    original = "/etc/volcano/mpiworker.host"
    target = "/root/mpiworker.host"
    shutil.copyfile(original, target)
    return 0

def wait_signal():
   # Wait all workers to send a message saying that they are active
    while startedRanks != getNumberOfRanks():
        time.sleep(20)
    return 0

def checkpoint():
    return 0

def start_mpi():
    global app
    ssh_hosts = open("/root/mpiworker.host")
    MPI_HOST = ','.join(line.strip() for line in ssh_hosts)
    os.environ["MPI_HOST"] = MPI_HOST
    MASTER_CMD = "mpiexec --allow-run-as-root -wdir /home/hpc-tests/cm1/ --host " +  str(MPI_HOST) + " -np " + str(getNumberOfRanks()) + " /home/hpc-tests/cm1/cm1.exe"
    app = subprocess.Popen(shlex.split(MASTER_CMD), preexec_fn=os.setsid)
    return 0

def main_worker(podname):
    """Opening subprocesses"""
    global app
    # kubectl get pod airflow-worker-0 --template '{{.status.podIP}}' -n airflow
    if not "worker" in podname: # This means this is a node that was scaled
        master_ip = os.env['IP']
        with grpc.insecure_channel('grpc-server.default:50051') as channel:
            stub = mpi_monitor_pb2_grpc.MonitorStub(channel)
            nodename = open("/etc/hostname").readline()
            response = stub.SendResources(mpi_monitor_pb2.RetrieveKeys(nodeName=nodename))
            f = open("/root/.ssh/authorized_keys", "w")
            f.writelines(response.SSHKey)
        return 0
    
    app = subprocess.Popen(shlex.split(WORKER_CMD), preexec_fn=os.setsid)
    signal.signal(signal.SIGTERM, signal_handler)
    app.wait()
    print("Finish execution...")
    return 0

def main_master():
    """Opening subprocesses"""
    global app
    global startedRanks
    global concludedRanks
    #global MPI_HOST

    app_ssh = subprocess.Popen("/usr/sbin/sshd", preexec_fn=os.setsid)
    #time.sleep(30) # Ensure all workers will be spawned first

    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mpi_monitor_pb2_grpc.add_MonitorServicer_to_server(Monitor(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    
    # Avoid the locked /etc/volcano fs
    copyRanks()

    # Reuse the function that waits all pods to be active
    wait_signal()

    # Reuse the function to restart mpi
    start_mpi()

    print("Application started!")

    # We wait application to be done    
    while concludedRanks != getNumberOfRanks():
        #print("Waiting")
        time.sleep(20)

    #app.wait()
    #server.wait_for_termination()
    print("Finishing execution...")

if __name__ == "__main__":
    """Defines whether we should follow the master or work router"""
    f = open('/etc/hostname')
    podname = f.read()
    if "master" in podname:
        main_master()
    else:
        main_worker(podname)  # This will also work when the pod has not a defined name