import argparse
import logging
import time

import schedule

from .config import load_config
from .sinks import MqttSink

from .reading_modules import ipset
from .reading_modules import iptables
from .reading_modules import dummy


_logger = logging.getLogger(__name__)


class JobFactory:
    def __init__(self, sinks, def_interval=5):
        self._sinks = sinks
        self._def_interval = def_interval

    class Job:
        def __init__(self, sinks, obj_name, module_name, reading_fnc, *fnc_args, **fnc_kwargs):
            self._sinks = sinks
            self._obj_name = obj_name
            self._module_name = module_name
            self._reading_fnc = reading_fnc
            self._fnc_args = fnc_args
            self._fnc_kwargs = fnc_kwargs

        def __call__(self):
            logging.info(f"Starting job on object '{self._obj_name}' (module '{self._module_name}')")
            try:
                readings = self._reading_fnc(*self._fnc_args, **self._fnc_kwargs)

                for sink in self._sinks:
                    for reading_name, value in readings.items():
                        logging.info(f"Publishing reading '{reading_name}' with value '{value}'")
                        sink.publish(self._obj_name, reading_name, value)
            except Exception as e:
                logging.warn(f'Error processing object "{self._obj_name}" in module "{self._module_name}": {e}')

    def build_job(self, obj_name, module_name, reading_fnc, cfg, *fnc_args, **fnc_kwargs):
        if cfg is not None and 'interval' in cfg:
            interval = cfg['interval']
        else:
            interval = self._def_interval
        job = JobFactory.Job(self._sinks, obj_name, module_name, reading_fnc, *fnc_args, **fnc_kwargs)

        logging.info(f"Queueing periodic job (interval {interval} s) with object name '{obj_name}' on module "
                     f"'{module_name}'")
        schedule.every(interval).seconds.do(job)


def main():
    logging.basicConfig(level=logging.DEBUG)

    # shutup schedule
    logger = logging.getLogger('schedule')
    logger.setLevel(logging.ERROR)

    parser = argparse.ArgumentParser(description='Publish IP statistic values periodically.')
    parser.add_argument('--config_file', type=str, default='/etc/iptables_stats.yml',
                        help='Path to config file')
    args = parser.parse_args()

    config = load_config(args.config_file)

    def_interval = 5
    if 'general' in config:
        if 'interval' in config['general']:
            def_interval = int(config['general']['interval'])
            logging.info(f"Read general config parameter 'interval={def_interval}'")

    sinks = []
    if 'mqtt' in config:
        cfg = config['mqtt']
        port = 1883 if 'port' not in cfg else int(cfg['port'])
        topic_root = None if 'topic_root' not in cfg else cfg['topic_root']
        mqtt = MqttSink(cfg['host'], port, topic_root)
        sinks.append(mqtt)

    if len(sinks) == 0:
        _logger.warning('Invalid config! No sinks defined!')

    job_factory = JobFactory(sinks, def_interval)

    module_name = 'iptables_pkt_count'
    if module_name in config:
        for obj_name, obj_cfg in config[module_name].items():
            job_factory.build_job(obj_name, module_name, iptables.get_rule_counters, obj_cfg, obj_cfg['chain'],
                                  obj_cfg['rule_regex'])

    module_name = 'iptables_rule_count'
    if module_name in config:
        for obj_name, obj_cfg in config[module_name].items():
            offset = 0 if 'offset' not in obj_cfg else int(obj_cfg['offset'])
            job_factory.build_job(obj_name, module_name, iptables.get_rule_count, obj_cfg, obj_cfg['chain'], offset)

    module_name = 'ipset_count'
    if module_name in config:
        for obj_name, obj_cfg in config[module_name].items():
            job_factory.build_job(obj_name, module_name, ipset.get_ip_count, obj_cfg, obj_cfg['setname'])

    module_name = 'dummy'
    if module_name in config:
        for obj_name, obj_cfg in config[module_name].items():
            job_factory.build_job(obj_name, module_name, dummy.get_dummy, obj_cfg)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
