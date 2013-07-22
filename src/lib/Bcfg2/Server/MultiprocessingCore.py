""" The multiprocessing server core is a reimplementation of the
:mod:`Bcfg2.Server.BuiltinCore` that uses the Python
:mod:`multiprocessing` library to offload work to multiple child
processes.  As such, it requires Python 2.6+.

The parent communicates with the children over a
:class:`multiprocessing.Pipe` that implements a very simple RPC
protocol.  Each command passed to a child over the Pipe must be a
tuple with the format::

    (<method>, <args>, <kwargs>)

The method must be exposed by the child by decorating it with
:func:`Bcfg2.Server.Core.exposed`.

The RPC call always returns a value via the pipe, so the caller *must*
read the return value in order to keep the pipe consistent.
"""

import threading
import lxml.etree
import multiprocessing
from Bcfg2.Cache import Cache
from Bcfg2.Compat import Queue
from Bcfg2.Server.Core import BaseCore, exposed
from Bcfg2.Server.Plugin import Debuggable
from Bcfg2.Server.BuiltinCore import Core as BuiltinCore


class DispatchingCache(Cache, Debuggable):
    """ Implementation of :class:`Bcfg2.Cache.Cache` that propagates
    cache expiration events to child nodes. """

    #: The method to send over the pipe to expire the cache
    method = "expire_cache"

    def __init__(self, *args, **kwargs):
        #: A dict of <child name>: :class:`multiprocessing.Pipe`
        #: objects that should be given a cache expiration command any
        #: time an item is expired.
        self.pipes = kwargs.pop("pipes", dict())

        Debuggable.__init__(self)
        Cache.__init__(self, *args, **kwargs)

    def expire(self, key=None):
        if (key and key in self) or (not key and len(self)):
            # dispatching cache expiration to children can be
            # expensive, so only do it if there's something to expire
            for child, pipe in self.pipes.items():
                if key:
                    self.logger.debug("Expiring metadata cache for %s on %s" %
                                      (key, child))
                else:
                    self.logger.debug("Expiring metadata cache on %s" % child)
                pipe.send((self.method, [key], dict()))
                pipe.recv()
        Cache.expire(self, key=key)


class NoSuchMethod(Exception):
    """ Exception raised by a child process if it's asked to execute a
    method that doesn't exist or that isn't exposed via the
    :class:`multiprocessing.Pipe` RPC interface. """
    pass


class DualEvent(object):
    """ DualEvent is a clone of :class:`threading.Event` that
    internally implements both :class:`threading.Event` and
    :class:`multiprocessing.Event`. """

    def __init__(self, threading_event=None, multiprocessing_event=None):
        self._threading_event = threading_event or threading.Event()
        self._multiproc_event = multiprocessing_event or \
            multiprocessing.Event()
        if threading_event or multiprocessing_event:
            # initialize internal flag to false, regardless of the
            # state of either object passed in
            self.clear()

    def is_set(self):
        """ Return true if and only if the internal flag is true. """
        return self._threading_event.is_set()

    isSet = is_set

    def set(self):
        """ Set the internal flag to true. """
        self._threading_event.set()
        self._multiproc_event.set()

    def clear(self):
        """ Reset the internal flag to false. """
        self._threading_event.clear()
        self._multiproc_event.clear()

    def wait(self, timeout=None):
        """ Block until the internal flag is true, or until the
        optional timeout occurs. """
        return self._threading_event.wait(timeout=timeout)


class ChildCore(BaseCore):
    """ A child process for :class:`Bcfg2.MultiprocessingCore.Core`.
    This core builds configurations from a given
    :class:`multiprocessing.Pipe`.  Note that this is a full-fledged
    server core; the only input it gets from the parent process is the
    hostnames of clients to render.  All other state comes from the
    FAM. However, this core only is used to render configs; it doesn't
    handle anything else (authentication, probes, etc.) because those
    are all much faster.  There's no reason that it couldn't handle
    those, though, if the pipe communication "protocol" were made more
    robust. """

    #: How long to wait while polling for new clients to build.  This
    #: doesn't affect the speed with which a client is built, but
    #: setting it too high will result in longer shutdown times, since
    #: we only check for the termination event from the main process
    #: every ``poll_wait`` seconds.
    poll_wait = 5.0

    def __init__(self, setup, pipe, terminate):
        """
        :param setup: A Bcfg2 options dict
        :type setup: Bcfg2.Options.OptionParser
        :param pipe: The pipe to which client hostnames are added for
                     ChildCore objects to build configurations, and to
                     which client configurations are added after
                     having been built by ChildCore objects.
        :type pipe: multiprocessing.Pipe
        :param terminate: An event that flags ChildCore objects to shut
                          themselves down.
        :type terminate: multiprocessing.Event
        """
        BaseCore.__init__(self, setup)

        #: The pipe to which client hostnames are added for ChildCore
        #: objects to build configurations, and to which client
        #: configurations are added after having been built by
        #: ChildCore objects.
        self.pipe = pipe

        #: The :class:`multiprocessing.Event` that will be monitored
        #: to determine when this child should shut down.
        self.terminate = terminate

    def _daemonize(self):
        return True

    def _run(self):
        return True

    def rpc_dispatch(self):
        """ Dispatch a method received via the
        :class:`multiprocessing.Pipe` RPC interface.

        :param data: The tuple of ``(<method name>, <args>, <kwargs>)``
        :type data: tuple
        """
        method, args, kwargs = self.pipe.recv()
        if hasattr(self, method):
            func = getattr(self, method)
            if func.exposed:
                self.pipe.send(func(*args, **kwargs))
            else:
                raise NoSuchMethod(method)
        else:
            raise NoSuchMethod(method)

    @exposed
    def GetConfig(self, client):
        self.logger.debug("Building configuration for %s" % client)
        return lxml.etree.tostring(self.BuildConfiguration(client))

    @exposed
    def expire_cache(self, client=None):
        """ Expire the metadata cache for a client """
        self.metadata_cache.expire(client)

    def _block(self):
        while not self.terminate.isSet():
            try:
                if self.pipe.poll(self.poll_wait):
                    if not self.metadata.use_database:
                        # handle FAM events, in case (for instance) the
                        # client has just been added to clients.xml, or a
                        # profile has just been asserted.  but really, you
                        # should be using the metadata database if you're
                        # using this core.
                        self.fam.handle_events_in_interval(0.1)
                    self.rpc_dispatch()
            except KeyboardInterrupt:
                break
        self.shutdown()


class Core(BuiltinCore):
    """ A multiprocessing core that delegates building the actual
    client configurations to
    :class:`Bcfg2.Server.MultiprocessingCore.ChildCore` objects.  The
    parent process doesn't build any children itself; all calls to
    :func:`GetConfig` are delegated to children. All other calls are
    handled by the parent process. """

    #: How long to wait for a child process to shut down cleanly
    #: before it is terminated.
    shutdown_timeout = 10.0

    def __init__(self, setup):
        BuiltinCore.__init__(self, setup)
        if setup['children'] is None:
            setup['children'] = multiprocessing.cpu_count()

        #: A dict of child name -> one end of the
        #: :class:`multiprocessing.Pipe` object used to communicate
        #: with that child.  (The child is given the other end of the
        #: Pipe.)
        self.pipes = dict()

        #: A queue that keeps track of which children are available to
        #: render a configuration.  A child is popped from the queue
        #: when it starts to render a config, then it's pushed back on
        #: when it's done.  This lets us use a blocking call to
        #: :func:`Queue.Queue.get` when waiting for an available
        #: child.
        self.available_children = Queue(maxsize=self.setup['children'])

        # sigh.  multiprocessing was added in py2.6, which is when the
        # camelCase methods for threading objects were deprecated in
        # favor of the Pythonic under_score methods.  So
        # multiprocessing.Event *only* has is_set(), while
        # threading.Event has *both* isSet() and is_set().  In order
        # to make the core work with Python 2.4+, and with both
        # multiprocessing and threading Event objects, we just
        # monkeypatch self.terminate to have isSet().
        self.terminate = DualEvent(threading_event=self.terminate)

        self.metadata_cache = DispatchingCache()

    def _run(self):
        for cnum in range(self.setup['children']):
            name = "Child-%s" % cnum
            (mainpipe, childpipe) = multiprocessing.Pipe()
            self.pipes[name] = mainpipe
            self.metadata_cache.pipes[name] = mainpipe
            self.logger.debug("Starting child %s" % name)
            childcore = ChildCore(self.setup, childpipe, self.terminate)
            child = multiprocessing.Process(target=childcore.run, name=name)
            child.start()
            self.logger.debug("Child %s started with PID %s" % (name,
                                                                child.pid))
            self.available_children.put(name)
        return BuiltinCore._run(self)

    def shutdown(self):
        BuiltinCore.shutdown(self)
        for child in multiprocessing.active_children():
            self.logger.debug("Shutting down child %s" % child.name)
            child.join(self.shutdown_timeout)
            if child.is_alive():
                self.logger.error("Waited %s seconds to shut down %s, "
                                  "terminating" % (self.shutdown_timeout,
                                                   child.name))
                child.terminate()
            else:
                self.logger.debug("Child %s shut down" % child.name)
        self.logger.debug("All children shut down")

    @exposed
    def set_debug(self, address, debug):
        self.metadata_cache.set_debug(debug)
        return BuiltinCore.set_debug(self, address, debug)

    @exposed
    def GetConfig(self, address):
        client = self.resolve_client(address)[0]
        childname = self.available_children.get()
        self.logger.debug("Building configuration on child %s" % childname)
        pipe = self.pipes[childname]
        pipe.send(("GetConfig", [client], dict()))
        config = pipe.recv()
        self.available_children.put_nowait(childname)
        return config
