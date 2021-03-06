import argparse
import json
import requests
import stix2
from os import path


def get_data_from_branch(domain, branch="master"):
    dest = "https://raw.githubusercontent.com/" \
        "mitre/cti/%s/%s/%s" \
        ".json" % (branch, domain, domain)
    stix_json = requests.get(dest).json()
    return stix2.MemoryStore(stix_data=stix_json["objects"])


if __name__ == '__main__':
    print("Running...\n")
    # Setup Arguments ...
    parser = argparse.ArgumentParser()
    '''
    Example File:

    https://raw.githubusercontent.com/scythe-io/community-threats/93f4e07c6792499153be2702f4f8ea23c3666cb9/Orangeworm/orangeworm_layer.json
    '''
    parser.add_argument(
        '--jsonfile', required=True,
        help='''
            The target ATT&CK Navigator JSON file. Can be local file or URL.
        ''',
    )
    args = parser.parse_args()
    # Load custom layer JSON
    # First, try for a local file
    if path.exists(args.jsonfile) and path.isfile(args.jsonfile):
        with open(args.jsonfile) as f:
            custom_layer = json.load(f)
    # If not a local file, try URL
    else:
        try:
            custom_layer = requests.get(args.jsonfile).json()
        except requests.exceptions.MissingSchema as e:
            print("Error: could not find '%s' local/URL!" % args.jsonfile)
            print(e)
            print("\n ...Exiting.\n")
            exit()
    # Load ATT&CK Data from internet
    src = get_data_from_branch("enterprise-attack")
    # Gather data into single object
    data = {}
    for technique in custom_layer['techniques']:
        # Query for Technique information
        cur_tec = src.query([
            stix2.Filter(
                "external_references.external_id", "=",
                technique['techniqueID']
            ),
            stix2.Filter("type", "=", "attack-pattern")
        ])[0]
        # Get the Tactic
        cur_tactic = cur_tec["kill_chain_phases"][0]["phase_name"]
        # Sort by tactic
        if data.get(cur_tactic) is None:
            data[cur_tactic] = []
        data[cur_tactic].append(
            (
                technique['techniqueID'],
                cur_tec["name"]
            )
        )
    # End FOR
    # Present Data ...
    for tactic in data:
        print("\n%s" % tactic.title())
        for technique in data[tactic]:
            print("%s - %s" % (technique[0], technique[1]))
        # End technique FOR
    # End tactic FOR
    # Done!
    print("\n ...Exiting.\n")
    exit()
