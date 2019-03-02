# Overview

Generates readings periodically and publishes them using different protocols (e.g. MQTT).

# Usage
Start `iptables_stat` and it will run constantly, generate readings periodically and publish them to configured sinks.

## Configuration
The program is configured using a configuration file in YAML format. Default location is `/etc/iptable_stats.yml` but a different location can be configured using the command line parameter `--config`.

The config file consists of the section `general` and a variable number of configuration sections for input modules and output sinks.

# Output Sinks
Currntly only one sink is implemented

## MQTT

*Example:*
```
mqtt:
  host: myHost
  port: 1883
  topic_root: home/myhost/iptables_stats
```

* *host*
* *port* (optional) - defaults to 1883
* *topic_root* - string that defines the root topic that is used for publishing readings

# Reading Modules
Every module has a section in the configuration. In each of these sections object configurations can be defined using a custom object name.

## iptable_pkt_count
Reads counter statistics for a given rule and chain from `iptables` and generates the readings `packet_count` and `byte_count`. Those represent the number of blocked packets and bytes.

Configuration:
* *chain* - Name of the chain
* *rule* - Name of the rule

## iptables_rule_count
Counts the number of rules in a given chain and generates the reading `rule_count`.

Configuration:
* *chain* - Name of the chain
* *offset* (optional) - An integer that is added to the value before publishing. This is useful to account for rules that should be ignored. E.g. there might be a drop rule which should not account towards the value. Set `offset` to `-1` to adjust to that.
