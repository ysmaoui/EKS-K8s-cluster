import boto3
import botocore
import os

REGION = os.getenv("REGION")
CLUSTER_NAME = os.getenv("CLUSTER_NAME")
EKS_ROLE_ARN = os.getenv("EKS_ROLE_ARN")
WORKERS_SSH_KEY_NAME = os.getenv("SSH_KEY_NAME")
WORKERS_AMI_ID = os.getenv("WORKERS_AMI")

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

cluster_network_template = os.path.join(".", "cluster_network.yml")

cloudformation = boto3.client('cloudformation', region_name='us-west-2')


def main():

    template_data = _parse_template(cluster_network_template)
    parameter_data = cluster_network_parameters

    params = {
        'StackName': CLUSTER_NAME,
        'TemplateBody': template_data,
        'Parameters': parameter_data
    }

    try:
        response = cloudformation.create_stack(**params)

        print(response)

        waiter = cloudformation.get_waiter('stack_create_complete')

        print("...waiting for stack to be ready...")
        waiter.wait(StackName=CLUSTER_NAME)
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        if error_message == 'No updates are to be performed.':
            print("No changes")
        else:
            raise


def _parse_template(template):
    with open(template) as template_fileobj:
        template_data = template_fileobj.read()
        cloudformation.validate_template(TemplateBody=template_data)

        return template_data


if __name__ == '__main__':
    main()
