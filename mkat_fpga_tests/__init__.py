import os
import logging
import subprocess

# Config using nose-testconfig plugin, set variables with --tc on nose command line
from testconfig import config as test_config

from corr2 import fxcorrelator
from corr2 import utils

LOGGER = logging.getLogger(__name__)


class CorrelatorFixture(object):

    def __init__(self, config_filename=None):
        if config_filename is None:
            config_filename = os.environ['CORR2INI']
        self.config_filename = config_filename
        os.environ['CORR2INI'] = config_filename
        self._correlator = None
        """Assume correlator is already running if this flag is True.
        IOW, don't do start_correlator() if set."""

    @property
    def correlator(self):
        if self._correlator is not None:
            return self._correlator
        else:
            if int(test_config.get('start_correlator', False)):
                # Is it not easier to just call a self._correlator method?
                self.start_correlator()

            # get config file from /etc/corr/{array-name}-{instrument-name}, e.g.
            # /etc/corr/array0-c8n856M4k
            self._correlator = fxcorrelator.FxCorrelator(
                'test correlator', config_source=self.config_filename)
            self.correlator.initialise(program=False)
            return self._correlator

    def start_stop_data(self, start_or_stop, engine_class):
        assert start_or_stop in ('start', 'stop')
        assert engine_class in ('xengine', 'fengine')
        # kcpcmd -s localhost:{array-port} capture-destination c856M4k 10.100.201.1
        #subprocess.check_call(['/usr/local/bin/kcpcmd' ,'-s' ,
            #'localhost:{}'.format(array_port) ,'capture-destination' ,
                #'{}'.format(instrument-name), '{}'.format(destination)])

        # kcpcmd -s localhost:{array-port} capture-start c856M4k
        # or
        # kcpcmd -s localhost:{array-port} capture-stop c856M4k
        #subprocess.check_call(['/usr/local/bin/kcpcmd' ,'-s' ,
            #'localhost:{}'.format(array_port) ,'capture-{}'.format(start_or_stop) ,
                #'{}'.format('c856M4k')]

        #subprocess.check_call([
            #'corr2_start_stop_tx.py', '--{}'.format(start_or_stop),
            #'--class', engine_class])


    def start_x_data(self):
        # On array interf
        self.start_stop_data('start', 'xengine')

    def stop_x_data(self):
        self.start_stop_data('stop', 'xengine')

    def start_correlator(self, retries=5, loglevel='INFO'):
        success = False
        retries_requested = retries

        # Read deng multicast groups from config
        # multcast_ip
        # Build list of 8

        subprocess.check_call(['/usr/local/bin/kcpcmd', '-t', '30', '-s',
            'localhost:7147', 'array-assign', 'array{}'.format(array_no),
                '{}'.format(multcast_ip)])

        #'kcpcmd -t 30 -s localhost:7147 array-assign array0 239.0.1.68+1:8888 239.0.1.70+1:8888 239.0.1.68+1:8888 239.0.1.70+1:8888 239.0.1.68+1:8888 239.0.1.70+1:8888 239.0.1.68+1:8888 239.0.1.70+1:8888'

        # kcpcmd array-assign array0 [list of deng multicast groups]
        # Do something to get katcp port of array interface and store it
        if (subprocess.Popen("kcpcmd -s localhost:7147 array-list array{0}\
            | grep array{0} | cut -f3 -d ' '".format(array_no)
                , shell=True, stdout=subprocess.PIPE).stdout.read().rstrip()) != int :

        katcp_port = int(subprocess.Popen("kcpcmd -s localhost:7147 array-list array{0}\
            | grep array{0} | cut -f3 -d ' '".format(array_no)
                , shell=True, stdout=subprocess.PIPE).stdout.read())


        while retries and not success:

            subprocess.check_call(['kcpcmd' '-s' 'localhost:{}'.format(array_port), 'instrument-activate', '{}'.format(instrument_name)])

            subprocess.check_call(['kcpcmd', '-t', '30', '-s', 'localhost:{}'.format(port),
                'array-assign', 'array{}'.format(array_no)] + '{}'.format(multicast_ip).split())

                        # Will create a correlator config file in
            success = 0 == subprocess.call(
                ['corr2_startcorr.py', '--loglevel', loglevel])
            retries -= 1
            if success:
                LOGGER.info('Correlator started succesfully')
            else:
                LOGGER.warn('Failed to start correlator, {} attempts left'
                            .format(retries))

        if not success:
            raise RuntimeError('Could not successfully start correlator within {} retries'
                               .format(retries_requested))

    def issue_metadata(self):
        subprocess.check_call('corr2_issue_spead_metadata.py')

correlator_fixture = CorrelatorFixture()
