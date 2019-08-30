import os

from rfapi import ConnectApiClient
from argparse import ArgumentParser


def iplookup(args):
    api = ConnectApiClient(auth=args.rf_token)
    print(api.lookup_ip(args.ipaddress))

def domainLookup(args):
    api = ConnectApiClient(auth=args.rf_token)
    print(api.lookup_domain(args.domainname))


parser = ArgumentParser()
parser.add_argument('--token',
                    dest="rf_token",
                    default=os.environ.get("RF_TOKEN"))
subparsers = parser.add_subparsers()

ipLookupParser = subparsers.add_parser('iplookup')
ipLookupParser.add_argument('ipaddress')
ipLookupParser.set_defaults(func=iplookup)

domainNameLookupParser = subparsers.add_parser('domainnamelookup')
domainNameLookupParser.add_argument('domainname')
domainNameLookupParser.set_defaults(func=domainLookup)


if __name__ == "__main__":
    parser_args = parser.parse_args()
    parser_args.func(parser_args)
