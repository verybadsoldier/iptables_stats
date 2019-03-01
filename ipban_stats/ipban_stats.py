import argparse
import logging
import time
import logging

from ipban_stats.config import load_config
from ipban_stats.sinks import MqttSink
import functools
import schedule

from .reading_modules import ipset
from .reading_modules import iptables


_logger = logging.getLogger()


class JobFactory:
    def __init__(self, sinks):
        self._sinks = sinks

    class Job:
        def __init__(self, sinks, obj_name, module_name, reading_fnc):
            self._sinks = sinks
            self._obj_name = obj_name
            self._module_name = module_name
            self._reading_fnc = reading_fnc

        def __call__(self):
            try:
                readings = self._reading_fnc()

                for sink in self._sinks:
                    for reading_name, value in readings.items():
                        sink.publish(self._obj_name, reading_name, value)
            except Exception as e:
                logging.error(f'Error processing object "{self._obj_name}" in module "{self._module_name}": {e}')

    def build_job(self, obj_name, module_name, reading_fnc):
        return JobFactory.Job(self._sinks, obj_name, module_name, reading_fnc)


_def_interval = 5


def _get_interval(cfg):
    return _def_interval if 'interval' not in cfg else int(cfg['interval'])


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Publish IP statistic values periodically.')
    parser.add_argument('--config_file', type=str, default='/etc/ipstatistics.yml',
                        help='Path to config file')
    args = parser.parse_args()

    config = load_config(args.config_file)

    if 'general' in config:
        if 'interval' in config['general']:
            global _def_interval
            _def_interval = int(config['general']['interval'])
            logging.info(f"Read generl config parameter 'interval={_def_interval}'")

    sinks = []
    if 'mqtt' in config:
        cfg = config['mqtt']
        port = 1883 if 'port' not in cfg else int(cfg['port'])
        topic_root = None if 'topic_root' not in cfg else cfg['topic_root']
        mqtt = MqttSink(cfg['host'], port, topic_root)
        sinks.append(mqtt)

    if len(sinks) == 0:
        _logger.warning('Invalid config! No sinks defined!')

    job_factory = JobFactory(sinks)

    if 'iptables_pkg_count' in config:
        for name, cfg in config['iptables_pkg_count'].items():
            fnc = functools.partial(iptables.get_rule_counters, cfg['chain'], cfg['rule_regex'])
            job = job_factory.build_job(name, 'iptables_pkg_count', fnc)
            schedule.every(_get_interval(cfg)).seconds.do(job)

    if 'iptables_rule_count' in config:
        for name, cfg in config['iptables_rule_count'].items():
            offset = 0 if 'offset' not in cfg else int(cfg['offset'])
            fnc = functools.partial(iptables.get_num_rules, cfg['chain'], offset)
            job = job_factory.build_job(name, 'iptables_rule_count', fnc)
            schedule.every(_get_interval(cfg)).seconds.do(job)

    if 'ipset_count' in config:
        for name, cfg in config['ipset_count'].items():
            fnc = functools.partial(ipset.get_ip_count, cfg['setname'])
            job = job_factory.build_job(name, 'ipset_count', fnc)
            schedule.every(_get_interval(cfg)).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
