from collections import deque
import json
import re
import threading
import time
if __name__ == "__main__":
    import kafka_utils
else:
    import wapps.mef18.kafka_utils as kafka_utils

LOGGING = True


class ParseUtils:
    # States matched exactly
    STATES = {
        "TRU_DISCOVERED": {
            "id": 2,
        },
        "TRU_INIT_DONE": {
            "id": 3,
        },
        "CPE_DISCOVERED": {
            "id": 7,
        },
        "TRU_AAI": {
            "id": 4,
        },
        "CPE_INIT_DONE": {
            "id": 8,
        },
        "CPE_AAI": {
            "id": 9,
        },
        "TRU_NETCONF": {
            "id": 5,
        },
        "TRU_CONTROLLER": {
            "id": 6,
        },
        "CPE_NETCONF": {
            "id": 10,
        },
        "CPE_CONTROLLER": {
            "id": 11,
        },
        "FWABandwidthBreach": {
            "id": 12,
        },
        "Upgrade Bandwidth": {
            "id": 16,
        },
        "Downgrade Bandwidth": {
            "id": 21,
        }
    }
    STATES_NAMES = set([x for x in STATES.keys()])
    # States matched using regex. Can overlap with states matched exactly
    STATE_REGEX_MATCHES = {
        13: [re.compile(r'.*ControlLoop-FWA_Upgrade.*')],
        14: [re.compile(r'.*com.Config_BRMS_Param_BRMSParamFWA_Up.*EVENT')],
        15: [re.compile(r'.*com.Config_BRMS_Param_BRMSParamFWA_Up.*SO\.RESPONSE')],
        18: [re.compile(r'.*ControlLoop-FWA_Downgrade.*')],
        19: [re.compile(r'.*com.Config_BRMS_Param_BRMSParamFWA_D.*n.*EVENT')],
        20: [re.compile(r'.*com.Config_BRMS_Param_BRMSParamFWA_D.*n.*SO\.RESPONSE')],
    }
    # States that trigger a soft reset. They should not be added when missing from a precursor sequence
    RESET_STATES = {12}
    # These states should be delayed, i.e. not added immeadiately after their direct precursor
    FORCE_DELAY = {17, 22}

    @staticmethod
    def parse_json(msg):
        """ Load JSON object. """
        jmsg = None
        try:
            jmsg = json.loads(msg)
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass
        return jmsg

    @staticmethod
    def _parse_exact_states(key_set):
        """ Parse the state by matching the given set for an exact match. """
        state = None
        try:
            intersect = ParseUtils.STATES_NAMES.intersection(key_set)
            if intersect:
                name = intersect.pop()
                state = ParseUtils.STATES.get(name, None).get('id', None)
        except (TypeError, AttributeError):
            pass
        return state

    @staticmethod
    def _parse_regex_match(msg):
        """ Parse the state by regex matching the given message. """
        state = None
        for st in ParseUtils.STATE_REGEX_MATCHES:
            regs = ParseUtils.STATE_REGEX_MATCHES[st]
            for reg in regs:
                if reg.match(msg):
                    state = st
        return state

    @staticmethod
    def parse_state(msg):
        """ Parse a string message into a state. """
        state = None
        try:
            jmsg = json.loads(msg)
            keys = set(jmsg.keys())
            state = ParseUtils._parse_exact_states(keys)

            # Ignore the state message if this value is found
            if 'notification' in keys:
                notification = jmsg.get('notification', '')
                if 'FAILURE' in notification:
                    # !!! EARLY RETRUN !!!
                    return None

            if state is None and 'tags' in keys:
                tags = set(jmsg['tags'])
                state = ParseUtils._parse_exact_states(tags)

            if state is None and 'policyName' in keys:
                name = {jmsg['policyName']}
                state = ParseUtils._parse_exact_states(name)
                if state is None:
                    state = ParseUtils._parse_regex_match(jmsg['policyName'])

            if state is None and 'event' in jmsg and 'commonEventHeader' in jmsg['event'] \
                    and 'eventName' in jmsg['event']['commonEventHeader']:
                name = {jmsg['event']['commonEventHeader']['eventName']}
                state = ParseUtils._parse_exact_states(name)

            if state is None and 'closedLoopControlName' in jmsg:
                name = {jmsg['closedLoopControlName']}
                state = ParseUtils._parse_exact_states(name)
                if state is None:
                    state = ParseUtils._parse_regex_match(jmsg['closedLoopControlName'])
        except json.JSONDecodeError:
            if msg in ParseUtils.STATES_NAMES:
                state = ParseUtils.STATES.get(msg, None)['id']
        except (TypeError, AttributeError):
            pass
        return state

    @staticmethod
    def parse_bw(msg):
        """ Parse a string message into a bandwidth number. """
        bw = None
        try:
            bw = int(msg)
        except (ValueError, TypeError):
            pass
        return bw

    @staticmethod
    def infer_additional_states(curr_state, states):
        """ Figure out what states need to be added when the current state is added to states. """
        inferred = set()
        states.add(curr_state)
        if len(states) > 0:
            m = max(states)
            for a in range(1, min(m, 12+1)):
                inferred.add(a)
            isect = {13, 14, 15, 16, 17}.intersection(states)
            if len(isect) > 0:
                m = max(isect)
                for a in range(13, m):
                    inferred.add(a)
            isect = {18, 19, 20, 21, 22}.intersection(states)
            if len(isect) > 0:
                for a in range(18, m):
                    inferred.add(a)
        if 21 in states or 21 in inferred:
            inferred.add(22)
        if 16 in states or 16 in inferred:
            inferred.add(17)
        return inferred

    @staticmethod
    def infer_removable_states(curr_state, states):
        """ Figure out what states need to be removed when the current state is added to states. """
        inferred = set()
        if curr_state == 12:
            inferred = {13, 14, 15, 16, 17, 18, 19, 20, 21, 22}
        if 13 <= curr_state <= 17:
            inferred = {18, 19, 20, 21, 22}
        if 18 <= curr_state <= 22:
            inferred = {13, 14, 15, 16, 17}
        return inferred

    @staticmethod
    def get_initial_states():
        """ Get starting set of states. """
        return set()

    @staticmethod
    def is_reset_state(state):
        """ Check if state is a reset state. """
        if state in ParseUtils.RESET_STATES:
            return True
        return False

    @staticmethod
    def is_force_delay_state(state):
        """ Check if state should be delayed. """
        if state in ParseUtils.FORCE_DELAY:
            return True
        return False


class Mef18Consumers:
    POLL_DELAY = 0  # seconds
    STATE_GET_DELAY = 2 # seconds
    HEALTH_CHECK_DELAY = 15 * 60 # seconds

    def __init__(self):
        Mef18Consumers.log_msg('Initializing MEF18 Consumers')
        self.consumers_lock = threading.RLock()
        self.consumers = {}
        self.states_waiting = deque()
        self.states = ParseUtils.get_initial_states()
        self.states_lock = threading.RLock()
        self.bw = (0, 0)
        self.bw_lock = threading.RLock()

        self.states_thread = threading.Thread(target=self._states_machine_thread)
        self.states_thread.start()
        self.health_thread = threading.Thread(target=self._consumer_health_thread)
        self.health_thread.start()

    def has_state(self, state):
        with self.states_lock:
            return state in self.states

    def get_states(self):
        return self.states.copy()

    def add_state(self, state):
        with self.states_lock:
            if state is not None:
                self.states_waiting.append(state)

    def add_states(self, states):
        with self.states_lock:
            for st in sorted(states):
                if st is not None:
                    self.states_waiting.append(st)

    def delete_state(self, state):
        with self.states_lock:
            try:
                self.states.remove(state)
            except (TypeError, KeyError):
                pass

    def delete_states(self, states):
        with self.states_lock:
            for st in sorted(states):
                self.states_waiting.append(-st)

    def clear_states(self):
        with self.states_lock:
            self.states_waiting.clear()
            self.states = ParseUtils.get_initial_states()

    def get_bw(self):
        bw = 0
        with self.bw_lock:
            try:
                bw = (self.bw[1] - self.bw[0]) * 8
            except (ValueError, TypeError, IndexError):
                pass
        return bw

    def push_bw(self, curr_bytes):
        with self.bw_lock:
            try:
                curr = int(curr_bytes)
                prev = self.bw[1]
                self.bw = (prev, curr)
            except (ValueError, TypeError, IndexError):
                pass
        return self.get_bw()

    def _states_machine_thread(self):
        """
        This thread should only exist once and never die.
        It periodically takes a state that is 'waiting' to be added, and adds it.
        :return:
        """
        Mef18Consumers.log_msg('Starting states machine thread')
        while True:
            try:
                with self.states_lock:
                    state = None
                    while (state is None or self.has_state(state)) and not ParseUtils.is_reset_state(state):
                        state = self.states_waiting.popleft()
                        if state < 0:
                            if self.has_state(abs(state)):
                                self.states.remove(abs(state))
                                state = None
                    to_remove = ParseUtils.infer_removable_states(state, self.get_states())
                    for st in to_remove:
                        if self.has_state(st):
                            self.states.remove(st)
                    to_add = ParseUtils.infer_additional_states(state, self.get_states())
                    to_add.add(state)
                    for st in to_add:
                        # Don't add st if it should be delayed and is immediately going to be processed off the waiting states next
                        if ParseUtils.is_force_delay_state(st) \
                                and len(self.states_waiting) > 0 and self.states_waiting[0] == st:
                            continue
                        self.states.add(st)
                    Mef18Consumers.log_msg('STATES: {}. Added {}: {}. Removed {}. Remaining {}'.format(self.states, state, to_add, to_remove, self.states_waiting))
            except IndexError:
                pass
            except Exception as ex:
                Mef18Consumers.log_msg("Exception in state_machine_thread {}".format(ex))
            time.sleep(Mef18Consumers.STATE_GET_DELAY)

    @staticmethod
    def _verify_settings(settings):
        valid = True
        if 'server' not in settings:
            valid = False
        if 'group_id' not in settings:
            valid = False
        if 'topics' not in settings:
            valid = False
        if not isinstance(settings['topics'], list):
            valid = False
        if len(settings['topics']) <= 0:
            valid = False
        return valid

    @staticmethod
    def log_msg(msg):
        if LOGGING:
            print('MEF18 DEBUG:', msg)

    @staticmethod
    def log_msg_from_consumer(msg, server, group_id, topics):
        if LOGGING:
            Mef18Consumers.log_msg("RECEIVED from {server}.{gid}.{topic}: {msg}".format(
                msg=msg, server=server, gid=group_id, topic=topics
            ))

    @staticmethod
    def _consumer_thread(consumers, settings, event):
        """
        This thread exists to start one Kafka consumer and get messages from it.
        Every message received is parsed.
        :param consumers: Mef18Consumers object
        :param settings: dictionary such as {'server':'localhost', 'group_id':'w1', 'event': threading.Event}
        :param event:
        :return:
        """
        server = settings['server']
        group_id = settings['group_id']
        topics = settings['topics']
        try:
            consumer = kafka_utils.start_consumer(server, group_id, topics)
            while not event.is_set():
                msg = kafka_utils.get_msg_topic(consumer)
                if msg:
                    topic = msg.get('topic', '')
                    msg = str(msg.get('value', b''), 'utf-8')
                    Mef18Consumers.log_msg_from_consumer(msg, server, group_id, topic)
                    # Message is either JSON containing state or current number of bytes
                    # Parse JSON and state
                    state = ParseUtils.parse_state(msg)
                    if state:
                        to_add = set()
                        Mef18Consumers.log_msg("PARSED STATE: {}".format(state))
                        projected_states = consumers.get_states()
                        to_remove = ParseUtils.infer_removable_states(state, projected_states)
                        for st in to_remove:
                            if st in projected_states:
                                projected_states.remove(st)
                        to_add = ParseUtils.infer_additional_states(state, projected_states)
                        # Do not add inferred reset states
                        to_add = to_add - ParseUtils.RESET_STATES
                        to_add.add(state)
                        Mef18Consumers.log_msg("INFERRED STATES: Add {}".format(to_add))
                        consumers.add_states(to_add)
                    bw = ParseUtils.parse_bw(msg)
                    # Parse current number of bytes
                    if bw is not None:
                        consumers.push_bw(bw)
                time.sleep(Mef18Consumers.POLL_DELAY)
        finally:
            Mef18Consumers.log_msg("KAFKA CONSUMER CLOSING: {}, {}, {}".format(server, group_id, topics))
            consumer.close()

    def create_consumer(self, cid, settings):
        with self.consumers_lock:
            if cid in self.consumers:
                Mef18Consumers.log_msg('ERROR: consumer %s already exists' % cid)
                return None
            if not Mef18Consumers._verify_settings(settings):
                Mef18Consumers.log_msg('ERROR: consumer settings invalid', settings)
                return None
            stop_event = threading.Event()
            thread = threading.Thread(target=Mef18Consumers._consumer_thread, args=(self, settings, stop_event))
            thread.start()
            c = {'settings': settings, 'thread': {'ref': thread, 'event': stop_event}}
            self.consumers[cid] = c
            return c

    def delete_consumer(self, cid):
        with self.consumers_lock:
            if cid not in self.consumers:
                return True
            thread = self.consumers[cid]['thread']['ref']
            stop = self.consumers[cid]['thread']['event']
            stop.set()
            thread.join()
            del self.consumers[cid]
            return True

    def get_consumer_settings(self):
        retval = {}
        with self.consumers_lock:
            for k, v in self.consumers.items():
                retval[k] = v['settings']
        return retval

    def _consumer_health_thread(self):
        while True:
            try:
                with self.consumers_lock:
                    to_delete = {}
                    for cid, data in self.consumers.items():
                        ref = data['thread'].get('ref', None)
                        if ref is None or not ref.is_alive():
                            to_delete[cid] = data.get('settings', {})
                    for cid, settings in to_delete.items():
                        Mef18Consumers.log_msg('Resurrecting consumer {} {}'.format(cid, settings))
                        self.delete_consumer(cid)
                        self.create_consumer(cid, settings)
            except Exception:
                pass
            time.sleep(Mef18Consumers.HEALTH_CHECK_DELAY)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Start Kafka Consumer')
    parser.add_argument('--server', '-s', default='100.0.0.200:9092')
    parser.add_argument('--groupid', '-g', default='warrior')
    parser.add_argument('--topics', '-t', nargs='+', default=['test'])
    args = parser.parse_args()
    print("STARTING", args)

    mef = Mef18Consumers()
    settings = {'server': args.server, 'group_id': args.groupid, 'topics': args.topics}
    mef.create_consumer(1, settings)
    consumers = mef.get_consumer_settings()
    print('Consumers:', consumers)

    while True:
        states = mef.get_states()
        bw = mef.get_bw()
        print('States:', states, 'Bandwidth:', bw)
        time.sleep(3)
