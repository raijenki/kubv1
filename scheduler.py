import logging
import uuid
import grpc
import mpi_monitor_pb2
import mpi_monitor_pb2_grpc

from kubernetes import client
from kubernetes import config

total_clients = 0

logging.basicConfig(level=logging.INFO)
config.load_incluster_config()

PVC_NAME = 'task-pv-claim'
MOUNT_PATH = '/data'
VOLUME_KEY  = 'volume-kctl'

class Kubernetes:
    def __init__(self):

        # Init Kubernetes
        self.core_api = client.CoreV1Api()
        self.batch_api = client.BatchV1Api()

    @staticmethod
    def create_container(image, name, pull_policy):
        volume = client.V1Volume(
            name=VOLUME_KEY,
            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=PVC_NAME),
        )
        volume_mount = client.V1VolumeMount(mount_path=MOUNT_PATH, name=VOLUME_KEY)

        container = client.V1Container(
            image=image,
            name=name,
            image_pull_policy=pull_policy,
            volume_mounts=[volume_mount],
            command=["/bin/sleep", "7200"],
        )

        logging.info(
            f"Created container with name: {container.name}, "
            f"image: {container.image} and args: {container.args}"
        )

        return container

    @staticmethod
    def create_pod_template(pod_name, container):
        pod_template = client.V1PodTemplateSpec(
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
            metadata=client.V1ObjectMeta(name=pod_name, labels={"pod_name": pod_name}),
        )

        return pod_template

    @staticmethod
    def create_job(job_name, pod_template):
        metadata = client.V1ObjectMeta(name=job_name, labels={"job_name": job_name})

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=metadata,
            spec=client.V1JobSpec(backoff_limit=0, template=pod_template),
        )

        return job

def create_additional_pod():
    job_id = uuid.uuid4()
    pod_id = job_id

    # Kubernetes instance
    k8s = Kubernetes()

    # STEP1: CREATE A CONTAINER
    _image = "raijenki/mpik8s:cm1"
    _name = "shuffler"
    _pull_policy = "Never"

    shuffler_container = k8s.create_container(_image, _name, _pull_policy)

    # STEP2: CREATE A POD TEMPLATE SPEC
    _pod_name = f"cm1-job-scale-{pod_id}"
    _pod_spec = k8s.create_pod_template(_pod_name, shuffler_container)

    # STEP3: CREATE A JOB
    _job_name = f"my-job-{job_id}"
    _job = k8s.create_job(_job_name, _pod_spec)

    # STEP4: EXECUTE THE JOB
    batch_api = client.BatchV1Api()
    batch_api.create_namespaced_job("default", _job)

if __name__ == "__main__":
    pass