# notifydict #

A subclass of dictionary that notifies you of changes to it or its subdicts

    >>> from notifydict import NotifyDict
    >>> from __future__ import print_function
    >>> callback = lambda key, value: print(key, value)
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

Other classes:

* ChangedDict
* HistoryDict