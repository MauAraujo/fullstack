import json
import os
import urllib.request

import boto3

IPSET_NAME = os.environ.get("IPSET_NAME", "github-actions-runners_IPV4")
SCOPE = "REGIONAL"
REGION = os.environ.get("AWS_REGION", "us-east-1")


def main():
    print("Fetching GitHub meta API...")
    req = urllib.request.Request(
        "https://api.github.com/meta",
        headers={"User-Agent": "waf-ip-sync"},
    )
    meta = json.loads(urllib.request.urlopen(req).read())

    ipv4 = [ip for ip in meta["actions"] if ":" not in ip]
    print(f"Found {len(ipv4)} IPv4 CIDRs from GitHub Actions")

    waf = boto3.client("wafv2", region_name=REGION)

    ipsets = waf.list_ip_sets(Scope=SCOPE).get("IPSets", [])
    existing = next((s for s in ipsets if s["Name"] == IPSET_NAME), None)

    if existing:
        resp = waf.get_ip_set(Name=IPSET_NAME, Scope=SCOPE, Id=existing["Id"])
        waf.update_ip_set(
            Name=IPSET_NAME,
            Scope=SCOPE,
            Id=existing["Id"],
            LockToken=resp["LockToken"],
            Addresses=ipv4,
        )
        print(f"Updated IPSet '{IPSET_NAME}' ({existing['Id']}) with {len(ipv4)} CIDRs")
    else:
        resp = waf.create_ip_set(
            Name=IPSET_NAME,
            Scope=SCOPE,
            Description="GitHub Actions runner IP ranges",
            IPAddressVersion="IPV4",
            Addresses=ipv4,
        )
        print(f"Created IPSet '{IPSET_NAME}' with {len(ipv4)} CIDRs")
        print(f"IPSet ARN: {resp['Summary']['ARN']}")
        print(f"IPSet ID: {resp['Summary']['Id']}")


if __name__ == "__main__":
    main()
