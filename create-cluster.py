import boto3
import os

CLUSTER_NAME = os.environ("CLUSTER_NAME")
EKS_ROLE_ARN = os.environ("EKS_ROLE_ARN")
WORKERS_SSH_KEY_NAME = os.environ("SSH_KEY_NAME")
WORKERS_AMI_ID = os.environ("WORKERS_AMI")

cluster_network_parameters = [
    {
        "ParameterKey": "EnvironmentName",
        "ParameterValue": CLUSTER_NAME
    }
]

cluster_control_panel_parameters = [
    {
        "ParameterKey": "EnvironmentName",
        "ParameterValue": CLUSTER_NAME
    },
    {
        "ParameterKey": "EKSRoleARN",
        "ParameterValue": EKS_ROLE_ARN
    }
]

cluster_worker_nodes_parameters = [
    {
        "ParameterKey": "EnvironmentName",
        "ParameterValue": CLUSTER_NAME
    },
    {
        "ParameterKey": "KeyName",
        "ParameterValue": WORKERS_SSH_KEY_NAME
    },
    {
        "ParameterKey": "NodeImageId",
        "ParameterValue": WORKERS_AMI_ID
    },
    {
        "ParameterKey": "ClusterName",
        "ParameterValue": CLUSTER_NAME
    },
    {
        "ParameterKey": "NodeGroupName",
        "ParameterValue": CLUSTER_NAME
    }
]


def main():
    cloudformation = boto3.client('cloudformation')
