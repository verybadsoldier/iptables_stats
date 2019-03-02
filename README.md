# Overview

Periodically gathers stats about iptables rules and sends them to different sinks (while currently only MQTT is supported). It is possible to count rules in chains, count number of packets/bytes processed by a rule and to count unique IPs in a ipset.

# Usage
Start `iptables_stat` and it will run constantly, generate readings periodically and publish them to configured sinks.

## Configuration
The program is configured using a configuration file in YAML format. Default location is `/etc/iptable_stats.yml` but a different location can be configured using the command line parameter `--config`.

The config file consists of the section `general` and a variable number of configuration sections for input modules and output sinks.

*Example:*
```
general:
  interval: 120

mqtt:
  host: myHost
  topic_root: home/myHost/iptables_stats

iptables_pkg_count:
  firehol_level1:
    chain: FIREHOL_BLACKLIST
    rule_regex: .*match-set.firehol_level3.src.*

  firehol_level2:
    chain: FIREHOL_BLACKLIST
    rule_regex: .*match-set.firehol_level2.src.*

  firehol_level3:
    chain: FIREHOL_BLACKLIST
    rule_regex: .*match-set.firehol_level3.src.*

ipset_count:
  firehol_level1:
    setname: firehol_level1

  firehol_level2:
    setname: firehol_level2

  firehol_level3:
    setname: firehol_level3

iptables_rule_count:
  f2b-traefik-auth:
    chain: f2b-traefik-auth
    offset: -1

  f2b-traefik-botsearch:
    chain: f2b-traefik-botsearch
    offset: -1
```

This configuration contains three `iptables_pkg_count` objects that will report iptables counters for the rules matching the given regular expressions. Also three `ipset_count` objects that count the number of unique IPs in the ipsets `firehol_level1`, `firehol_level2` and `firehol_level3`.
Last but not least two `iptables_rule_count` objects that count the rules in the chains `f2b-traefik-auth` and `f2b-traefik-botsearch`. `fail2ban` injects rules into these chains in case of a IP ban. Each rule represents a single IP. Both objects use an `offset` of `-1` cause both chains contain a fixed `DROP` rule that should not be counted.

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
Every module has a section in the configuration. In each of these sections object configurations can be defined using a user-defined object name. Every object configuration can override the gobal `interval` parameter so it is possible to configure `interval` for objects individually.

## iptable_pkt_count
Reads counter statistics for a given rule and chain from `iptables` and generates the readings `packet_count` and `byte_count`. Those represent the number of blocked packets and bytes.

Configuration:
* *chain* - Name of the chain
* *rule_regex* - Regex that matches the rule in question. It is matched against a string as the rule appears in the output of `iptables-save`. The regex is not allowed to match more than one rule.

## iptables_rule_count
Counts the number of rules in a given chain and generates the reading `rule_count`.

Configuration:
* *chain* - Name of the chain
* *offset* (optional) - An integer that is added to the value before publishing. This is useful to account for rules that should be ignored. E.g. there might be a drop rule which should not account towards the value. Set `offset` to `-1` to adjust to that.
