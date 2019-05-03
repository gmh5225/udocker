#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
udocker unit tests: UdockerCLI
"""

import sys
from unittest import TestCase, main
try:
    from unittest.mock import Mock, patch, MagicMock, mock_open
except ImportError:
    from mock import Mock, patch, MagicMock, mock_open

sys.path.append('.')

from udocker.config import Config
from udocker.container.localrepo import LocalRepository
from udocker.cli import UdockerCLI

if sys.version_info[0] >= 3:
    BUILTIN = "builtins"
else:
    BUILTIN = "__builtin__"

BOPEN = BUILTIN + '.open'


class UdockerCLITestCase(TestCase):
    """Test UdockerTestCase() command line interface."""

    def setUp(self):
        self.conf = Config().getconf()
        self.conf['hostauth_list'] = ("/etc/passwd", "/etc/group")
        self.conf['cmd'] = "/bin/bash"
        self.conf['cpu_affinity_exec_tools'] = (["numactl", "-C", "%s", "--", ],
                                                ["taskset", "-c", "%s", ])
        self.conf['valid_host_env'] = "HOME"
        self.conf['username'] = "user"
        self.conf['userhome'] = "/"
        self.conf['oskernel'] = "4.8.13"
        self.conf['location'] = ""
        self.conf['keystore'] = "KEYSTORE"
        self.local = LocalRepository(self.conf)

    @patch('udocker.cli.KeyStore')
    @patch('udocker.cli.DockerLocalFileAPI')
    @patch('udocker.cli.DockerIoAPI')
    def test_01_init(self, mock_dioapi, mock_dlocapi, mock_ks):
        """Test UdockerCLI() constructor."""

        # Test self.conf['keystore'] starts with /
        self.conf['keystore'] = "/xxx"
        udoc = UdockerCLI(self.local, self.conf)
        self.assertTrue(mock_dioapi.called)
        self.assertTrue(mock_dlocapi.called)
        self.assertTrue(mock_ks.called_with(self.conf['keystore']))
        mock_ks.reset_mock()

        # Test self.conf['keystore'] does not starts with /
        self.conf['keystore'] = "xx"
        udoc = UdockerCLI(self.local, self.conf)
        self.assertTrue(mock_ks.called_with(self.conf['keystore']))

    @patch('udocker.cli.KeyStore')
    @patch('udocker.cli.DockerLocalFileAPI')
    @patch('udocker.cli.DockerIoAPI')
    @patch('udocker.cli.Msg')
    def test_02__check_imagespec(self, mock_msg, mock_dioapi,
                                 mock_dlocapi, mock_ks):
        """Test UdockerCLI()._check_imagespec()."""

        mock_msg.level = 0
        mock_dioapi.is_repo_name = False
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc._check_imagespec("")
        self.assertEqual(status, (None, None))

        mock_dioapi.is_repo_name = False
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc._check_imagespec("AAA")
        self.assertEqual(status, ("AAA", "latest"))

        mock_dioapi.is_repo_name = False
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc._check_imagespec("AAA:45")
        self.assertEqual(status, ("AAA", "45"))

    @patch('udocker.cmdparser.CmdParser.get')
    @patch('udocker.cmdparser.CmdParser')
    @patch('udocker.cli.os.path.exists')
    @patch('udocker.cli.KeyStore')
    @patch('udocker.cli.DockerLocalFileAPI')
    @patch('udocker.cli.DockerIoAPI')
    @patch('udocker.cli.Msg')
    def test_03_do_mkrepo(self, mock_msg, mock_dioapi, mock_dlocapi, mock_ks,
                          mock_exists, mock_cmdp, mock_cmdget):
        """Test UdockerCLI().do_mkrepo()."""

        mock_msg.level = 0
        mock_cmdget.return_value = "/"
        mock_exists.return_value = True
        mock_dlocapi.create_repo.return_value = True
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_mkrepo(mock_cmdp)
        self.assertEqual(status, 1)

        mock_cmdget.return_value = ""
        mock_exists.return_value = True
        mock_dlocapi.create_repo.return_value = True
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_mkrepo(mock_cmdp)
        self.assertEqual(status, 0)

        mock_cmdget.return_value = "/"
        mock_exists.return_value = True
        mock_dlocapi.create_repo.return_value = False
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_mkrepo(mock_cmdp)
        self.assertEqual(status, 1)

    def test_04__search_print_v1(self):
        """Test UdockerCLI()._search_print_v1()."""
        pass

    def test_05__search_print_v2(self):
        """Test UdockerCLI()._search_print_v2()."""
        pass

    @patch('udocker.cli.input')
    @patch('udocker.cli.UdockerCLI._search_print_v2')
    @patch('udocker.cli.UdockerCLI._search_print_v1')
    @patch('udocker.cmdparser.CmdParser')
    @patch('udocker.cli.KeyStore')
    @patch('udocker.cli.DockerLocalFileAPI')
    @patch('udocker.cli.DockerIoAPI')
    @patch('udocker.cli.Msg')
    def test_06_do_search(self, mock_msg, mock_dioapi, mock_dlocapi, mock_ks,
                          mock_cmdp, mock_print1, mock_print2, mock_input):
        """Test UdockerCLI().do_search()."""

        mock_msg.level = 0
        mock_cmdp.get.side_effect = ["", "", "" "", "", ]
        mock_cmdp.missing_options.return_value = True
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_search(mock_cmdp)
        self.assertEqual(status, 1)

        mock_cmdp.get.side_effect = ["", "", "" "", "", ]
        mock_cmdp.missing_options.return_value = False
        mock_dioapi.return_value.search_get_page.return_value = None
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_search(mock_cmdp)
        self.assertEqual(status, 0)

        mock_cmdp.get.side_effect = ["", "", "" "", "", ]
        mock_cmdp.missing_options.return_value = False
        mock_dioapi.return_value.search_get_page.side_effect = (
            [["results", ], ["repositories", ], [], ])
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_search(mock_cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_print1.called)
        self.assertTrue(mock_print2.called)

        mock_print1.reset_mock()
        mock_print2.reset_mock()
        mock_cmdp.get.side_effect = ["", "", "" "", "", ]
        mock_cmdp.missing_options.return_value = False
        mock_dioapi.return_value.search_get_page.side_effect = (
            [["zzz", ], ["repositories", ], [], ])
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_search(mock_cmdp)
        self.assertEqual(status, 0)
        self.assertFalse(mock_print1.called)
        self.assertTrue(mock_print2.called)

        mock_print1.reset_mock()
        mock_print2.reset_mock()
        mock_cmdp.get.side_effect = ["", "", "" "", "", ]
        mock_cmdp.missing_options.return_value = False
        mock_input.return_value = "q"
        mock_dioapi.return_value.search_ended = False
        mock_dioapi.return_value.search_get_page.side_effect = (
            [["zzz", ], ["repositories", ], [], ])
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_search(mock_cmdp)
        self.assertEqual(status, 0)
        self.assertFalse(mock_print1.called)
        self.assertFalse(mock_print2.called)

    @patch('udocker.cmdparser.CmdParser')
    @patch('udocker.cli.KeyStore')
    @patch('udocker.cli.DockerLocalFileAPI')
    @patch('udocker.cli.DockerIoAPI')
    @patch('udocker.cli.Msg')
    def test_07_do_load(self, mock_msg, mock_dioapi,
                        mock_dlocapi, mock_ks, mock_cmdp):
        """Test UdockerCLI().do_load()."""

        mock_msg.level = 0
        mock_cmdp.get.side_effect = ["", "", "" "", "", ]
        mock_cmdp.missing_options.return_value = True
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_load(mock_cmdp)
        self.assertEqual(status, 1)

        mock_cmdp.get.side_effect = ["", "", "" "", "", ]
        mock_cmdp.missing_options.return_value = False
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_load(mock_cmdp)
        self.assertEqual(status, 1)

        mock_cmdp.get.side_effect = ["INFILE", "", "" "", "", ]
        mock_cmdp.missing_options.return_value = False
        mock_dlocapi.return_value.load.return_value = []
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_load(mock_cmdp)
        self.assertEqual(status, 1)

        mock_cmdp.get.side_effect = ["INFILE", "", "" "", "", ]
        mock_cmdp.missing_options.return_value = False
        mock_dlocapi.return_value.load.return_value = ["REPO", ]
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_load(mock_cmdp)
        self.assertEqual(status, 0)

    @patch('udocker.cli.UdockerCLI._check_imagespec')
    @patch('udocker.cmdparser.CmdParser')
    @patch('udocker.cli.KeyStore')
    @patch('udocker.cli.DockerLocalFileAPI')
    @patch('udocker.cli.DockerIoAPI')
    @patch('udocker.cli.Msg')
    def test_08_do_import(self, mock_msg, mock_dioapi,
                          mock_dlocapi, mock_ks, mock_cmdp, mock_chkimg):
        """Test UdockerCLI().do_import()."""

        mock_msg.level = 0
        cmd_options = [False, False, "", False,
                       "INFILE", "IMAGE", "" "", "", ]
        mock_cmdp.get.side_effect = ["", "", "", "", "", "", "", "", "", ]
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_import(mock_cmdp)
        self.assertEqual(status, 1)
        mock_cmdp.reset_mock()

        mock_cmdp.get.side_effect = cmd_options
        mock_chkimg.return_value = ("", "")
        mock_cmdp.missing_options.return_value = False
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_import(mock_cmdp)
        self.assertEqual(status, 1)
        mock_cmdp.reset_mock()

        mock_cmdp.get.side_effect = cmd_options
        mock_chkimg.return_value = ("IMAGE", "")
        mock_cmdp.missing_options.return_value = True
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_import(mock_cmdp)
        self.assertEqual(status, 1)
        mock_cmdp.reset_mock()

        mock_cmdp.get.side_effect = cmd_options
        mock_chkimg.return_value = ("IMAGE", "TAG")
        mock_cmdp.missing_options.return_value = False
        mock_dlocapi.return_value.import_toimage.return_value = False
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_import(mock_cmdp)
        self.assertEqual(status, 1)
        mock_cmdp.reset_mock()

        mock_cmdp.get.side_effect = cmd_options
        mock_chkimg.return_value = ("IMAGE", "TAG")
        mock_cmdp.missing_options.return_value = False
        mock_dlocapi.return_value.import_toimage.return_value = True
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_import(mock_cmdp)
        self.assertEqual(status, 0)

    def test_09_do_export(self):
        """Test UdockerCLI().do_export()."""
        pass

    def test_10_do_clone(self):
        """Test UdockerCLI().do_clone()."""
        pass

    @patch('udocker.cli.getpass')
    @patch('udocker.cli.input')
    @patch('udocker.cmdparser.CmdParser')
    @patch('udocker.cli.KeyStore')
    @patch('udocker.cli.DockerLocalFileAPI')
    @patch('udocker.cli.DockerIoAPI')
    @patch('udocker.cli.Msg')
    def test_08_do_login(self, mock_msg, mock_dioapi,
                         mock_dlocapi, mock_ks, mock_cmdp,
                         mock_rinput, mock_gpass):
        """Test UdockerCLI().do_login()."""

        mock_msg.level = 0
        mock_cmdp.get.side_effect = ["user", "pass", "" "", "", ]
        mock_rinput.return_value = "user"
        mock_gpass.return_value = "pass"
        mock_ks.return_value.put.return_value = False
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_login(mock_cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(mock_rinput.called)
        self.assertFalse(mock_gpass.called)

        mock_rinput.reset_mock()
        mock_gpass.reset_mock()
        mock_cmdp.get.side_effect = ["", "", "" "", "", ]
        mock_rinput.return_value = "user"
        mock_gpass.return_value = "pass"
        mock_ks.return_value.put.return_value = False
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_login(mock_cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_rinput.called)
        self.assertTrue(mock_gpass.called)

        mock_cmdp.get.side_effect = ["", "", "" "", "", ]
        mock_rinput.return_value = "user"
        mock_gpass.return_value = "pass"
        mock_ks.return_value.put.return_value = True
        udoc = UdockerCLI(self.local, self.conf)
        status = udoc.do_login(mock_cmdp)
        self.assertEqual(status, 0)


if __name__ == '__main__':
    main()
