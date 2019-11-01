import boto3
import botocore
import os
import json
import sys

from datetime import datetime

NEEDED_ENVIRONMENT_VARIABLES = ['REGION', 'CLUSTER_NAME', 'EKS_ROLE_ARN', 'SSH_KEY_NAME',
                                'WORKERS_AMI']

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

    check_environment_variables()

    create_or_update_stack("K8S-cluster-network", cluster_network_template,
                           cluster_network_parameters)


def _parse_template(template):
    with open(template) as template_fileobj:
        template_data = template_fileobj.read()
        cloudformation.validate_template(TemplateBody=template_data)

        return template_data


def _stack_exists(stack_name):
    stacks = cloudformation.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name == stack['StackName']:
            return True
    return False


def create_or_update_stack(stack_name, template, parameters):
    template_data = _parse_template(template)
    parameter_data = parameters

    params = {
        'StackName': stack_name,
        'TemplateBody': template_data,
        'Parameters': parameter_data,
    }

    try:
        if _stack_exists(stack_name):
            print('Updating {}'.format(stack_name))
            stack_result = cloudformation.update_stack(**params)
            waiter = cloudformation.get_waiter('stack_update_complete')
        else:
            print('Creating {}'.format(stack_name))
            stack_result = cloudformation.create_stack(**params)
            waiter = cloudformation.get_waiter('stack_create_complete')
        print("...waiting for stack to be ready...")
        waiter.wait(StackName=stack_name)
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        if error_message == 'No updates are to be performed.':
            print("No changes")
        else:
            raise
    else:
        print(json.dumps(
            cloudformation.describe_stacks(StackName=stack_result['StackId']),
            indent=2,
            default=json_serial
        ))


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


def check_environment_variables():
    passed = True
    for env in NEEDED_ENVIRONMENT_VARIABLES:
        if env in os.environ:
            pass
        else:
            print('Please set the environment variable: {}'.format(env))
            passed = False

    if not passed:
        sys.exit(1)


if __name__ == '__main__':
    main()
