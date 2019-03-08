import iptc
import logging
import subprocess
import re


_logger = logging.getLogger(__name__)


class RuleNotFoundException(Exception):
    pass


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
            raise RuleNotFoundException(f"Regular expression '{regex}' found multiple matching rules in chain '{chain}'!")
            return i
        rule_no = i

    if rule_no is None:
        raise RuleNotFoundException(f"Could not find rule in chain '{chain}' that matches regular expression: '{regex}'")
    return rule_no


def get_rule_counters(chain_name, regex):
    try:
        rule_no = _find_rule_idx(chain_name, regex)

        table = iptc.Table(iptc.Table.FILTER)
        if table.is_chain(chain_name):
            chain = iptc.Chain(table, chain_name)
            rules = list(chain.rules)
            counters = rules[rule_no].get_counters()
        else:
            _logger.debug(f"Chain '{chain_name}' does not exist")
            counters = (0, 0)  # return 0 for non-existing chains
    except RuleNotFoundException:
        _logger.debug(f"Chain '{chain_name}' does not exist (reported by exception)")
        counters = (0, 0)

    return dict(packet_count=counters[0], byte_count=counters[1])


def get_rule_count(chain_name, offset=0):
    _logger.debug(f"Querying rule count in chain '{chain_name}' using offset {offset}")
    table = iptc.Table(iptc.Table.FILTER)
    if table.is_chain(chain_name):
        chain = iptc.Chain(table, chain_name)
        rule_count = len(chain.rules) + offset
    else:
        _logger.debug(f"Chain '{chain_name}' does not exist")
        rule_count = 0  # we return 0 for non-existing chains
    _logger.debug(f"Rule count in '{chain_name}' is {rule_count} (offset applied)")
    return dict(rule_count=rule_count)
