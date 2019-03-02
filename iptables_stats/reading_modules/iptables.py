import iptc
import subprocess
import re


def _find_rule_idx(chain, regex):
    """Return the index of the rule matching "regex". Raises exceptions if multiple rules are matching."""
    output = subprocess.check_output(["iptables", "--list-rules", chain])

    output = output.decode()
    rule_lines = [x for x in output.splitlines() if not x.startswith('-N')]

    rule_no = None
    regex = re.compile(regex)
    for i, rule in enumerate(rule_lines):
        if not regex.match(rule):
            continue
        if rule_no is not None:
            raise Exception(f"Regular expression '{regex}' found multiple matching rules in chain '{chain}'!")
            return i
        rule_no = i

    if rule_no is None:
        raise Exception(f"Could not find rule in chain '{chain}' that matches regular expression: '{regex}'")
    return rule_no


def get_rule_counters(chain, regex):
    rule_no = _find_rule_idx(chain, regex)

    table = iptc.Table(iptc.Table.FILTER)
    chain = iptc.Chain(table, chain)
    rules = list(chain.rules)
    counters = rules[rule_no].get_counters()

    return dict(packet_count=counters[0], byte_count=counters[1])


def get_rule_count(chain, offset=0):
    table = iptc.Table(iptc.Table.FILTER)
    chain = iptc.Chain(table, chain)
    return dict(rule_count=len(chain.rules) + offset)
