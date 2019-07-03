import argparse
import googleapiclient.discovery
import google.auth
from google.oauth2 import service_account


def get_credentials(service_account_filename=None):
    if service_account_filename:
        return service_account.Credentials.from_service_account_file(service_account_filename)
    else:
        credentials, _ = google.auth.default()
        return credentials


def create_file_store_api(credentials):
    return googleapiclient.discovery.build('file', 'v1', credentials=credentials)


class FileStoreSettings(object):
    def __init__(self, file_store_id, file_share_name, file_share_capacity_gb, tier="STANDARD", network_name="default"):
        self.id = file_store_id
        self.file_share_name = file_share_name
        self.file_share_capacity_gb = file_share_capacity_gb
        self.tier = tier
        self.network_name = network_name

    def body_dict(self):
        return {
            "tier": self.tier,
            "fileShares": [
                {
                    "name": self.file_share_name,
                    "capacityGb": self.file_share_capacity_gb
                }
            ],
            "networks": [
                {"network": self.network_name}
            ]
        }


def create_file_store_instance(file_store_api, project_id, region_zone, file_store_settings):
    parent = "projects/{}/locations/{}".format(project_id, region_zone)
    file_store_instances = file_store_api.projects().locations().instances()
    request = file_store_instances.create(
        parent=parent,
        instanceId=file_store_settings.id,
        body=file_store_settings.body_dict())
    return request.execute()


def delete_file_store_instance(file_store_api, project_id, region_zone, instance_id):
    name = "projects/{}/locations/{}/instances/{}".format(project_id, region_zone, instance_id)
    file_store_instances = file_store_api.projects().locations().instances()
    request = file_store_instances.delete(name=name)
    return request.execute()


def create_file_store(args):
    credentials = get_credentials(args.service_account_credential_file)
    file_store_api = create_file_store_api(credentials)
    file_store_settings = FileStoreSettings(
        args.file_store_id,
        args.file_share_name,
        args.file_share_capacity_gb,
        args.tier,
        args.network
    )
    instance = create_file_store_instance(file_store_api, args.project_id, args.region_zone, file_store_settings)
    print("Created file share {}".format(instance))


def delete_file_store(args):
    credentials = get_credentials(args.service_account_credential_file)
    file_store_api = create_file_store_api(credentials)
    result = delete_file_store_instance(file_store_api, args.project_id, args.region_zone, args.file_store_id)
    print("Delete fs {}".format(result))


def create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    create_parser = subparsers.add_parser('create', description='Create file share')
    create_parser.add_argument('--project_id', required=True)
    create_parser.add_argument('--region_zone', required=True)
    create_parser.add_argument('--service_account_credential_file')
    create_parser.add_argument('--file_store_id', required=True)
    create_parser.add_argument('--file_share_name', required=True)
    create_parser.add_argument('--file_share_capacity_gb', required=True)
    create_parser.add_argument('--tier', default='STANDARD')
    create_parser.add_argument('--network', default='default')
    create_parser.set_defaults(func=create_file_store)

    delete_parser = subparsers.add_parser('delete', description='Delete file share')
    delete_parser.add_argument('--project_id', required=True)
    delete_parser.add_argument('--region_zone', required=True)
    delete_parser.add_argument('--service_account_credential_file')
    delete_parser.add_argument('--file_store_id')
    delete_parser.set_defaults(func=delete_file_store)

    return parser


def main():
    parser = create_parser()
    parsed_args = parser.parse_args()
    if hasattr(parsed_args, 'func'):
        parsed_args.func(parsed_args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
