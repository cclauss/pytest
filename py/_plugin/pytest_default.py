""" default hooks and general py.test options. """

import sys
import py

def pytest_cmdline_main(config):
    from py._test.session import Session, Collection
    collection = Collection(config)
    # instantiate session already because it
    # records failures and implements maxfail handling
    session = Session(config, collection)
    exitstatus = collection.do_collection()
    if not exitstatus:
        exitstatus = session.main()
    return exitstatus

def pytest_ignore_collect(path, config):
    ignore_paths = config.getconftest_pathlist("collect_ignore", path=path)
    ignore_paths = ignore_paths or []
    excludeopt = config.getvalue("ignore")
    if excludeopt:
        ignore_paths.extend([py.path.local(x) for x in excludeopt])
    return path in ignore_paths
    # XXX more refined would be:
    if ignore_paths:
        for p in ignore_paths:
            if path == p or path.relto(p):
                return True

def pytest_collect_directory(path, parent):
    # XXX reconsider the following comment
    # not use parent.Directory here as we generally
    # want dir/conftest.py to be able to
    # define Directory(dir) already
    if not parent.recfilter(path): # by default special ".cvs", ...
        # check if cmdline specified this dir or a subdir directly
        for arg in parent.collection._argfspaths:
            if path == arg or arg.relto(path):
                break
        else:
            return
    Directory = parent.config._getcollectclass('Directory', path)
    return Directory(path, parent=parent)

def pytest_report_iteminfo(item):
    return item.reportinfo()

def pytest_addoption(parser):
    group = parser.getgroup("general", "running and selection options")
    group._addoption('-x', '--exitfirst', action="store_true", default=False,
               dest="exitfirst",
               help="exit instantly on first error or failed test."),
    group._addoption('--maxfail', metavar="num",
               action="store", type="int", dest="maxfail", default=0,
               help="exit after first num failures or errors.")

    group = parser.getgroup("collect", "collection")
    group.addoption('--collectonly',
        action="store_true", dest="collectonly",
        help="only collect tests, don't execute them."),
    group.addoption("--ignore", action="append", metavar="path",
        help="ignore path during collection (multi-allowed).")
    group.addoption('--confcutdir', dest="confcutdir", default=None,
        metavar="dir",
        help="only load conftest.py's relative to specified dir.")

    group = parser.getgroup("debugconfig",
        "test process debugging and configuration")
    group.addoption('--basetemp', dest="basetemp", default=None, metavar="dir",
               help="base temporary directory for this test run.")

def pytest_configure(config):
    # compat
    if config.getvalue("exitfirst"):
        config.option.maxfail = 1

