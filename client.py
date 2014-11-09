#!/usr/bin/env python3

from plc.client.netclient import Client
from plc.core.settings import Configuration

client = Client()
conf = Configuration()
conf.load("clientsettings.json")

if __name__ == "__main__":
    client.launch(conf)
