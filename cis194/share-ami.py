"""
Share the Windows AMIs with Class Accounts
"""

import boto3
import argparse

images = ['ami-089900441acecb80c', 'ami-0a98bc37f5116dee3']

def main():
    parser = argparse.ArgumentParser(description='Add accounts to AMI ACLs.')
    parser.add_argument('accounts', nargs='+',
                        help='Accounts to add to the AMIs')

    args = parser.parse_args()
    client = boto3.client('ec2', region_name='us-east-1')

    for ami in images:
        for user in args.accounts:
            resp = client.modify_image_attribute(ImageId=ami, Attribute='launchPermission',
                LaunchPermission = {
                    'Add': [
                        {
                            'UserId': user
                        },
                    ],
                })
            print(resp)
    #print(args.accounts)


if __name__ == '__main__':
    main();