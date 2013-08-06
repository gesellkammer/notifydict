from fnmatch import fnmatch as _fnmatch

class _NOTHING(object): pass

class NotifyDict(dict):
    """a dictionary that notifies you of changes to it or its subdicts
    
    >>> def printfunc(*args): print args
    >>> callback = lambda key, value: printfunc(key, value)
    >>> orig = {'A':10, 'B':{'Ba':100, 'Bb':200}}
    >>> d = NotifyDict(callback, orig)
    >>> d['B']['Ba'] = 101
    B/Ba 101

    You can define qualified callbacks

    >>> d = NotifyDict({'*'  : lambda key, value: printfunc("default", key, value), 
                        'B/*': lambda key, value: printfunc("subdict", key, value)}, orig)
    >>> d['C'] = 9
    default C 9
    >>> d['B']['Bh'] = 8
    subdict B/Bh 8
    """
    __slots__ = ['_callback_registry', '_callback', '_separator', '_bypass']
    def __init__(self, callback, *args, **kws):
        dict.__init__(self, *args, **kws)
        if callable(callback):
            self._callback = callback
            self._callback_registry = {}
        elif isinstance(callback, dict):
            self._callback = self.match
            self._callback_registry = callback
        else:
            raise TypeError("callback must be either a function or a dictionary of callbacks")
        self._separator = "/"
        self._bypass = False

    def _match(self, key, value):
        for pattern, callback in self._callback_registry.iteritems():
            if _fnmatch(key, pattern):
                callback(key, value)

    def notify(self, path, newvalue):
        if self._bypass:
            return 
        self._callback(path, newvalue)

    def __setitem__(self, key, value):
        self.notify(key, value)
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        if isinstance(value, dict) and not isinstance(value, NotifyDict):
            def newcallback(newkey, newvalue, separator=self._separator):
                self._callback(separator.join((key, newkey)), newvalue)
            value = NotifyDict(newcallback, value)
            dict.__setitem__(self, key, value)
        return value
        
    def getpath(self, path, default=None):
        """
        >>> orig = {'A':10, 'B':{'Ba':100, 'Bb':200}}
        >>> d = NotifyDict(printfunc, orig)
        >>> d._separator
        /
        >>> d.getpath('B/Bb')
        200
        """
        if isinstance(path, basestring):
            if self._separator in path:
                keys = path.split(self._separator)
            else:
                keys = [path]
        else:
            return self[path]
        d = self
        for key in keys:
            v = d.get(key, default)
            if isinstance(v, dict):
                d = v
        return v

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.notify(key, None)

    def pop(self, key, default=_NOTHING):
        if default is not _NOTHING:
            value = self.get(key, default)
        else:
            value = self[key]
        self.notify(key, value)
        return value

    def update(self, E, **F):
        try:
            for key in E.keys():
                self[key] = E[key]
        except AttributeError:
            for (k, v) in E:
                self[k] = v
        for k in F:
            self[k] = F[k]

    def set_stealth(self, path, value):
        """
        The same as .set, but does not trigger notification
        """
        self._bypass = True
        self.set(path, value)
        self._bypass = False

    def set(self, path, value):
        """
        the same as d[path] = value, but path can be a multilevel path

        >>> def printfunc(*args): print "got", args
        >>> orig = {'A':10, 'B':{'Ba':100, 'Bb':200}}
        >>> d = NotifyDict(printfunc, orig)
        >>> d._separator
        /
        >>> d.set('B/Bb', 999)
        got ('B/Bb', 999)
        >>> d
        {'A':10, 'B':{'Ba':100, 'Bb':999}}
        """
        if isinstance(path, basestring):
            keys = path.split(self._separator) if isinstance(path, basestring) else path
        elif isinstance(path, (tuple, list)):
            keys = path
        else:
            raise ValueError("the path must be a string of the type key1/key2/... or a seq [key1, key2, ...]")
        d = self
        if len(keys) == 0:
            self[path] = value
        else:
            for key in keys[:-1]:
                v = d.get(key)
                if isinstance(v, dict):
                    d = v
                else:
                    raise KeyError("set -- key not found: %s" % key)
            d[keys[-1]] = value
            self.notify(path, value)

class ChangedDict(NotifyDict):
    __slots__ = ['_changed']
    def __init__(self, *args, **kws):
        """
        >>> d = ChangedDict({'A':10, 'B':20})
        >>> d.changed
        True
        >>> d.check(); d.changed
        False
        >>> d['A'] = 20
        >>> d.changed
        True
        """
        self._changed = False
        def callback(key, value):
            self._changed = True
        NotifyDict.__init__(self, callback, *args, **kws)
    @property
    def changed(self):
        return self._changed
    def check(self):
        self._changed = False

class HistoryDict(NotifyDict):
    __slots__ = ['_history']
    def __init__(self, *args, **kws):
        """
        >>> d = HistoryDict({'A':10, 'B':20})
        >>> d.history
        []
        >>> d['C'] = 30
        >>> d.history
        [('C', 30)]
        >>> d['D' = 40]
        >>> d.history
        [('C', 30), ('D', 40)]
        >>> d.check()
        >>> d.history
        []
        """
        self._history = []
        def callback(key, value):
            self._history.append((key, value))
        NotifyDict.__init__(slef, callback, *args, **kws)
    @property
    def history(self):
        return self._history
    def check(self):
        self._history = []