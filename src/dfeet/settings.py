#
#    THIS FILE IS PART OF THE D-FEET PROJECT AND LICENSED UNDER THE GPL. SEE
#    THE 'COPYING' FILE FOR DETAILS
#
#   portions taken from the Jokosher project
#
try:
    # python2.x
    import ConfigParser as configparser
except:
    # python3
    import configparser
import os
import re


class ConfigTokenizer():
    COMMA = re.compile(",")
    FALLTHROUGH = re.compile('(?:[^,.])+')
    # FIXME: String re does not ignore escaped quotes (e.g. \") correctly
    STRING = re.compile('"((?:[^\\"]|\\.)*)"' + "|'((?:[^\\']|\\.)*)'")
    NUMBER = re.compile('[+-]?[0-9]*\.?[0-9]+')
    WHITESPACE = re.compile('\s')

    _parse_order = [STRING, NUMBER, WHITESPACE, COMMA, FALLTHROUGH]

    class Match():
        ENDWHITESPACE = re.compile('\s$')
        UNESCAPE = re.compile('\\\(.)')

        def __init__(self, match, regex):
            self.match = match
            self.regex = regex

        def is_whitespace(self):
            if self.regex == ConfigTokenizer.WHITESPACE:
                return True
            return False

        def is_comma(self):
            if self.regex == ConfigTokenizer.COMMA:
                return True
            return False

        def is_value(self):
            if self.regex == ConfigTokenizer.STRING or \
                    self.regex == ConfigTokenizer.NUMBER or \
                    self.regex == ConfigTokenizer.FALLTHROUGH:
                return True
            return False

        def strip(self, s):
            return self.ENDWHITESPACE.sub('', s)

        def unescape(self, s):
            return self.UNESCAPE.sub(r'\1', s)

        def __str__(self):
            result = ''
            groups = self.match.groups()
            if groups:
                for g in groups:
                    if g is not None:
                        result = g
            else:
                result = self.match.group(0)

            result = self.strip(result)
            if self.regex == ConfigTokenizer.STRING:
                result = self.unescape(result)

            return result

    def __init__(self, s):
        self._consumable = s

    def __iter__(self):
        return self

    def next(self):
        """for python2"""
        return self.__next__()

    def __next__(self):
        for r in self._parse_order:
            m = r.match(self._consumable)
            if m:
                self._consumable = self._consumable[len(m.group(0)):]
                return self.Match(m, r)

        raise StopIteration


class Settings:
    """
    Handles loading/saving settings from/to a file on disk.
    """

    instance = None

    # the different settings in each config block
    general = {
        "windowheight": 550,
        "windowwidth": 900,
        "windowstate": None,
        "bustabs_list": [],
        "addbus_list": [],
        }

    def __init__(self, filename=None):
        """
        Creates a new instance of Settings.

        Parameters:
            filename -- path to the settings file.
                        If None, the default $XDG_CONFIG_HOME/d-feet/config will be used.
        """
        if not filename:
            if 'XDG_CONFIG_HOME' in list(os.environ.keys()):
                self.filename = os.path.join(os.environ['XDG_CONFIG_HOME'], 'd-feet', 'config')
            else:
                self.filename = os.path.join(os.environ['HOME'], '.config', 'd-feet', 'config')
        else:
            self.filename = filename
        self.config = configparser.ConfigParser()

        self.read()

    @classmethod
    def get_instance(cls):
        """This class is a singlton so use this method to get it"""
        if cls.instance:
            return cls.instance

        cls.instance = Settings()
        return cls.instance

    def decode_list(self, s):
        result = []
        lex = ConfigTokenizer(s)
        for item in lex:
            if item.is_value():
                result.append(str(item))

        return result

    def read(self):
        """
        Reads configuration settings from the config file and loads
        then into the Settings dictionaries.
        """
        self.config.read(self.filename)

        if not self.config.has_section("General"):
            self.config.add_section("General")

        for key, value in self.config.items("General"):
            if key.endswith('list'):
                value = self.decode_list(value)

            self.general[key] = value

    def quote(self, value):
        result = ''
        result = re.sub(r'([\\\"\'])', r'\\\1', value)
        return '"%s"' % result

    def write(self):
        """
        Writes configuration settings to the Settings config file.
        """
        for key in self.general:
            if key.endswith('list'):
                for i in range(0, len(self.general[key])):
                    self.general[key][i] = self.quote(self.general[key][i])
                self.general[key] = ','.join(self.general[key])

            if self.general[key] is None:
                self.general[key] = ''

            self.config.set("General", str(key), str(self.general[key]))

        # make sure that the directory that the config file is in exists
        new_file_dir = os.path.split(self.filename)[0]
        if not os.path.isdir(new_file_dir):
            os.makedirs(new_file_dir)
        f = open(self.filename, 'w')
        self.config.write(f)
        f.close()
