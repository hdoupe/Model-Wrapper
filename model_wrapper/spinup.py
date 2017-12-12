from boto import ec2
import os
import time
import argparse


def create_boxes(ec2_conn, ami_id, keyname, node_count, security_groups,
               instance_type):
    # get existing ID's
    old_ids = set(inst.id for reservation in ec2_conn.get_all_instances() for inst in reservation.instances)
    print("OLD IDS", old_ids)
    machine = ec2_conn.run_instances(ami_id,
                                key_name=keyname,
                                min_count=node_count,
                                max_count=node_count,
                                security_groups=security_groups,
                                instance_type=instance_type)

    new_instances = [inst for inst in machine.instances if inst.id not in old_ids]
    print("NEW INSTANCES", new_instances)
    # make sure machines are up and running
    is_running = [False] * len(new_instances)
    while not all(is_running):
        for count, new_instance in enumerate(new_instances):
            is_running[count] = new_instance.state == u'running'
        time.sleep(3)
        # get new info on all instances
        for new_instance in new_instances:
            new_instance.update()

    # make sure machines are reachable
    is_reachable = [False] * len(new_instances)
    while not all(is_reachable):
        instance_ids = [new_instance.id for new_instance in new_instances]
        inst_statuses = ec2_conn.get_all_instance_status(instance_ids=instance_ids)
        is_reachable = [inst_status.system_status.details['reachability'] != 'passed' for inst_status in inst_statuses]
        time.sleep(3)

    # make sure we have dns_names
    time.sleep(1)
    for new_instance in new_instances:
        assert new_instance.public_dns_name
        print("public dns name:", new_instance.public_dns_name)

    return new_instances


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyname", default=None, help="AWS keyname")
    parser.add_argument("--security_group", default=None, help="AWS security group")
    # default is ubuntu t2.xlarge, 8GB mem
    parser.add_argument("--ami_id", default=None, help="AWS AMI")
    parser.add_argument("--instance_type", default=None, help="AWS instance type, e.g. t1.micro")
    parser.add_argument("--node_count", default=None, help="Number of AWS machines to spinup")
    parser.add_argument("--region", default=None, help="AWS region to use")
    parser.add_argument("--aws_id", default=None, help="AWS ID")
    parser.add_argument("--aws_secret", default=None, help="AWS secret key")
    args = parser.parse_args()

    # read arguments from commandline or get from envrionement
    keyname = args.handle or os.environ.get("KEYNAME")
    security_group = args.security_group or os.environ.get("SECURITY_GROUP")
    ami_id = args.ami_id or os.environ.get("AMI_ID")
    instance_type = args.instance_type or os.environ.get("INSTANCE_TYPE")
    node_count = args.node_count or os.environ.get("NODE_COUNT")

    region = args.region or os.environ.get("REGION")
    aws_id = args.aws_id or os.environ["AWS_ID"]
    aws_secret = args.aws_secret or os.environ["AWS_SECRET"]

    ec2_conn = ec2.connect_to_region(
        region, #N. Virginia
        aws_access_key_id=aws_id,
        aws_secret_access_key=aws_secret
    )

    create_boxes(ec2_conn, ami_id, keyname, node_count, [security_group, ],
                 instance_type)
