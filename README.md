#NetScreen Microburst Detector

This tool allows you to detect microbursts within an ASIC-Based NetScreen platform

#Python Requirements

This code was tested on Python 2.7, however it most likely would work within other releases depending on the support of the required libraries.

The majority of modules used within this tool are contained within the Python standard library.

However there are some additonal libraries that you need to install.

1) ecdsa==0.11 2) paramiko==1.15.1 3) pycrypto==2.6.1 4) wsgiref==0.1.2

Using the PIP tool it is simple to install these packages. In the file "virtualenv_requirements.txt" all of these modules are listed.

Simple do the following and PIP will install the modules for you. Depending on your platform and or Python configuration these modules may need to be compiled.

```
pip install -r virtualenv_requirements.txt
```

#Setting up your Python environment

There are many philosophies in how to configure your Python environment. For the development of this tool [pyenv](https://github.com/yyuu/pyenv) and [virtualenv](https://github.com/yyuu/pyenv-virtualenv) were used

#Usage

To use the tool please install the required libraries as described in the section [Python Requirements](https://github.com/JNPRAutomate/nsmburst-detector#python-requirements).

Once completed simply download the nsautomate.py tool and see the usage patterns below.

```
user@device$ ./nsautomate.py
usage: nsautomate.py [-h] [--output] [--no-output] [--clear-session]
                     [--log LOG] [--log-level LOGLEVEL] [--csv CSVFile]
                     [--host HOST] [--username USERNAME] [--password PASSWORD]
                     [--password-secure]

Gather options from the user

optional arguments:
-h, --help            show this help message and exit
--output              Specify if you want to print output to standard out.
                      Defaults to printing output.
--no-output           Specify if you do not want to print output to standard
                      out.
--clear-session       Clears all other admin sessions. Ensure the successful
                      completion of the script.
--log LOG             Specify the file name where to save the output to.
--log-level LOGLEVEL  Specify the verbosity of logging. Default 0 provides
                      basic logging. Setting log level to 1 provides max
                      output.
--csv CSVFile         Specify the CSV file to read hosts from.
--host HOST           Specify single host to connect to. Can not be used
                      with --csv.
--username USERNAME   Specify the default username to use when not specified
                      within the csv.
--password PASSWORD   Specify the default password to use when not specified
                      within the csv.
--password-secure     Be prompted for the the default password.
```

#Examples

##Specify a single host

```
user@device$ ./nsautomate.py --host 10.0.1.222

======================================================================
Connecting to host 10.0.1.222
Successfully connected to host 10.0.1.222
Host: ssg5-v92-wlan Product: SSG5-v92-WLAN Serial Number: 0168102006001722
======================================================================
```

##Write to a log file ###Works in all Modes

```
user@device$ ./nsautomate.py --host 10.0.1.222 --log output.log

======================================================================
Connecting to host 10.0.1.222
Successfully connected to host 10.0.1.222
Host: ssg5-v92-wlan Product: SSG5-v92-WLAN Serial Number: 0168102006001722
======================================================================

user@device$ ls
nsautomate.py    output.log

```

Specify a single host with a username and password. Excellent for automation scripts.
-------------------------------------------------------------------------------------

```
user@device$ ./nsautomate.py --host 10.0.1.222 --username netscreen --password netscreen

======================================================================
Connecting to host 10.0.1.222
Successfully connected to host 10.0.1.222
Host: ssg5-v92-wlan Product: SSG5-v92-WLAN Serial Number: 0168102006001722
======================================================================
```

Specify a single host with a username and securly collected password
--------------------------------------------------------------------

```
python nsautomate.py --host 10.0.1.222 --password-secure
Password:

======================================================================
Connecting to host 10.0.1.222
Successfully connected to host 10.0.1.222
Host: ssg5-v92-wlan Product: SSG5-v92-WLAN Serial Number: 0168102006001722
======================================================================
```

##Specify a CSV file

You can specify a CSV file that can contain the following lines

1) hostname or ip 2) hostname,username,password 3) Lines can be commented with # or // 4) When a hostname is specified without a username and password specified the default username and password is used

```
user@device$ ./python nsautomate.py --csv test-devices.csv
Found 2 hosts in test-devices.csv CSV file. Starting stats gathering.

======================================================================
Connecting to host 192.168.100.1
Unable to connect to host: 192.168.100.1

======================================================================
Connecting to host testhost.example.com
Successfully connected to host testhost.spglab.juniper.net
Host: testhost Product: NetScreen-5400-II Serial Number: 0047052006000045
No packet loss detected in ASIC 1 witin queue XMT1-d on host testhost
No packet loss detected in ASIC 1 witin queue CPU1-d on host testhost
No packet loss detected in ASIC 1 witin queue  L2Q-d on host testhost
No packet loss detected in ASIC 1 witin queue RSM2-d on host testhost
No packet loss detected in ASIC 1 witin queue  SLU-d on host testhost
No packet loss detected in ASIC 1 witin queue CPU2-d on host testhost
No packet loss detected in ASIC 2 witin queue XMT1-d on host testhost
No packet loss detected in ASIC 2 witin queue CPU1-d on host testhost
No packet loss detected in ASIC 2 witin queue  L2Q-d on host testhost
No packet loss detected in ASIC 2 witin queue RSM2-d on host testhost
No packet loss detected in ASIC 2 witin queue  SLU-d on host testhost
No packet loss detected in ASIC 2 witin queue CPU2-d on host testhost
No packet loss detected in ASIC 3 witin queue XMT1-d on host testhost
No packet loss detected in ASIC 3 witin queue CPU1-d on host testhost
No packet loss detected in ASIC 3 witin queue  L2Q-d on host testhost
No packet loss detected in ASIC 3 witin queue RSM2-d on host testhost
No packet loss detected in ASIC 3 witin queue  SLU-d on host testhost
No packet loss detected in ASIC 3 witin queue CPU2-d on host testhost
No packet loss detected in ASIC 4 witin queue XMT1-d on host testhost
No packet loss detected in ASIC 4 witin queue CPU1-d on host testhost
No packet loss detected in ASIC 4 witin queue  L2Q-d on host testhost
No packet loss detected in ASIC 4 witin queue RSM2-d on host testhost
No packet loss detected in ASIC 4 witin queue  SLU-d on host testhost
No packet loss detected in ASIC 4 witin queue CPU2-d on host testhost
======================================================================
```

##Specify verbose output

You can output all of the values from the ASIC gathering by specifying the log level of 1

```
user@device$ ./python nsautomate.py --log-level 1 --host 172.22.152.24
014-10-06T21:10:50.531939 source-host ======================================================================
2014-10-06T21:10:50.531992 source-host Connecting to host 172.22.152.24
2014-10-06T21:10:53.396725 source-host Successfully connected to host 172.22.152.24
2014-10-06T21:10:53.396759 source-host Host: testhost Product: NetScreen-2000 Serial Number: 0079044005000117
2014-10-06T21:11:02.757802 source-host qgroup select register: qactctl(0x800005d8)=0x00000000, PKTCNT(0x80000598)
2014-10-06T21:11:02.757837 source-host pktcnt[PSR1    ] = 0x00000000          0
2014-10-06T21:11:02.757849 source-host pktcnt[PSR2    ] = 0x00000000          0
2014-10-06T21:11:02.757860 source-host pktcnt[PSR3    ] = 0x00000000          0
2014-10-06T21:11:02.757870 source-host pktcnt[PSR4    ] = 0x00000000          0
2014-10-06T21:11:02.757880 source-host pktcnt[PSR5    ] = 0x00000000          0
2014-10-06T21:11:02.757889 source-host pktcnt[PSR6    ] = 0x00000000          0
2014-10-06T21:11:02.757899 source-host pktcnt[PSR7    ] = 0x00000000          0
2014-10-06T21:11:02.757909 source-host pktcnt[PSR8    ] = 0x00000000          0
2014-10-06T21:11:02.757919 source-host pktcnt[CPU2-d  ] = 0x00000000          0
2014-10-06T21:11:02.757935 source-host qgroup select register: qactctl(0x800005d8)=0x00000004, PKTCNT(0x80000598)
2014-10-06T21:11:02.757944 source-host pktcnt[XMT1    ] = 0x00000000          0
2014-10-06T21:11:02.757955 source-host pktcnt[XMT2    ] = 0x00000000          0
2014-10-06T21:11:02.757964 source-host pktcnt[XMT3    ] = 0x00000000          0
2014-10-06T21:11:02.757974 source-host pktcnt[XMT4    ] = 0x00000004          4
2014-10-06T21:11:02.757984 source-host pktcnt[XMT5    ] = 0x00000000          0
2014-10-06T21:11:02.757993 source-host pktcnt[XMT6    ] = 0x00000000          0
2014-10-06T21:11:02.758003 source-host pktcnt[XMT7    ] = 0x00000000          0
2014-10-06T21:11:02.758013 source-host pktcnt[XMT8    ] = 0x00000002          2
2014-10-06T21:11:02.758023 source-host pktcnt[CPU1-d  ] = 0x00000000          0
2014-10-06T21:11:02.758033 source-host pktcnt[RSM1-d  ] = 0x00000000          0
2014-10-06T21:11:02.758049 source-host qgroup select register: qactctl(0x800005d8)=0x0000000c, PKTCNT(0x80000598)
2014-10-06T21:11:02.758059 source-host pktcnt[XMT5    ] = 0x00000000          0
2014-10-06T21:11:02.758159 source-host pktcnt[XMT6    ] = 0x00000000          0
2014-10-06T21:11:02.758178 source-host pktcnt[XMT7    ] = 0x00000000          0
2014-10-06T21:11:02.758190 source-host pktcnt[XMT8    ] = 0x00000002          2
2014-10-06T21:11:02.758200 source-host pktcnt[PSR5    ] = 0x00000000          0
2014-10-06T21:11:02.758209 source-host pktcnt[PSR6    ] = 0x00000000          0
2014-10-06T21:11:02.758220 source-host pktcnt[PSR7    ] = 0x00000000          0
2014-10-06T21:11:02.758229 source-host pktcnt[PSR8    ] = 0x00000000          0
2014-10-06T21:11:02.758239 source-host pktcnt[PSRB    ] = 0x00000000          0
2014-10-06T21:11:02.758249 source-host pktcnt[L2Q-d   ] = 0x00000000          0
2014-10-06T21:11:02.758265 source-host qgroup select register: qactctl(0x800005d8)=0x00000014, PKTCNT(0x80000598)
2014-10-06T21:11:02.758275 source-host pktcnt[PSR1-d  ] = 0x00000000          0
2014-10-06T21:11:02.758285 source-host pktcnt[PSR2-d  ] = 0x00000000          0
2014-10-06T21:11:02.758295 source-host pktcnt[PSR3-d  ] = 0x00000000          0
2014-10-06T21:11:02.758305 source-host pktcnt[PSR4-d  ] = 0x00000000          0
2014-10-06T21:11:02.758315 source-host pktcnt[PSR5-d  ] = 0x00000000          0
2014-10-06T21:11:02.758325 source-host pktcnt[PSR6-d  ] = 0x00000000          0
2014-10-06T21:11:02.758334 source-host pktcnt[PSR7-d  ] = 0x00000000          0
2014-10-06T21:11:02.758344 source-host pktcnt[PSR8-d  ] = 0x00000000          0
2014-10-06T21:11:02.758354 source-host pktcnt[SLU-d   ] = 0x00000000          0
2014-10-06T21:11:02.758363 source-host pktcnt[SPI-d   ] = 0x00000000          0
2014-10-06T21:11:02.758379 source-host qgroup select register: qactctl(0x800005d8)=0x00000018, PKTCNT(0x80000598)
2014-10-06T21:11:02.758389 source-host pktcnt[XMT1-d  ] = 0x00000000          0
2014-10-06T21:11:02.758399 source-host pktcnt[XMT2-d  ] = 0x00000000          0
2014-10-06T21:11:02.758409 source-host pktcnt[XMT3-d  ] = 0x00000000          0
2014-10-06T21:11:02.758419 source-host pktcnt[XMT4-d  ] = 0x00000000          0
2014-10-06T21:11:02.758428 source-host pktcnt[XMT5-d  ] = 0x00000000          0
2014-10-06T21:11:02.758438 source-host pktcnt[XMT6-d  ] = 0x00000000          0
2014-10-06T21:11:02.758448 source-host pktcnt[XMT7-d  ] = 0x00000000          0
2014-10-06T21:11:02.758458 source-host pktcnt[XMT8-d  ] = 0x00000000          0
2014-10-06T21:11:02.758468 source-host pktcnt[PPA-d   ] = 0x00000000          0
2014-10-06T21:11:02.758478 source-host pktcnt[PPB-d   ] = 0x00000000          0
2014-10-06T21:11:02.758494 source-host qgroup select register: qactctl(0x800005d8)=0x00000020, PKTCNT(0x80000598)
2014-10-06T21:11:02.758503 source-host pktcnt[CPU1    ] = 0x00000000          0
2014-10-06T21:11:02.758513 source-host pktcnt[RSM2-d  ] = 0x00000000          0
2014-10-06T21:11:02.758523 source-host pktcnt[CPU3-d  ] = 0x00000000          0
2014-10-06T21:11:02.758532 source-host pktcnt[CPU4-d  ] = 0x00000000          0
2014-10-06T21:11:02.758543 source-host pktcnt[CPU5-d  ] = 0x00000000          0
2014-10-06T21:11:02.758552 source-host pktcnt[PPC-d   ] = 0x00000000          0
2014-10-06T21:11:02.758562 source-host pktcnt[PPD-d   ] = 0x00000000          0
2014-10-06T21:11:02.758578 source-host qgroup select register: qactctl(0x800005d8)=0x00000000, PKTCNT(0x80000598)
2014-10-06T21:11:02.758587 source-host pktcnt[PSR1    ] = 0x00000000          0
2014-10-06T21:11:02.758597 source-host pktcnt[PSR2    ] = 0x00000000          0
2014-10-06T21:11:02.758607 source-host pktcnt[PSR3    ] = 0x00000000          0
2014-10-06T21:11:02.758617 source-host pktcnt[PSR4    ] = 0x00000000          0
2014-10-06T21:11:02.758627 source-host pktcnt[PSR5    ] = 0x00000000          0
2014-10-06T21:11:02.758636 source-host pktcnt[PSR6    ] = 0x00000000          0
2014-10-06T21:11:02.758646 source-host pktcnt[PSR7    ] = 0x00000000          0
2014-10-06T21:11:02.758656 source-host pktcnt[PSR8    ] = 0x00000000          0
2014-10-06T21:11:02.758666 source-host pktcnt[CPU2-d  ] = 0x00000000          0
2014-10-06T21:11:02.758682 source-host qgroup select register: qactctl(0x800005d8)=0x00000004, PKTCNT(0x80000598)
2014-10-06T21:11:02.758691 source-host pktcnt[XMT1    ] = 0x00000000          0
2014-10-06T21:11:02.758701 source-host pktcnt[XMT2    ] = 0x00000000          0
2014-10-06T21:11:02.758711 source-host pktcnt[XMT3    ] = 0x00000000          0
2014-10-06T21:11:02.758720 source-host pktcnt[XMT4    ] = 0x00000002          2
2014-10-06T21:11:02.758730 source-host pktcnt[XMT5    ] = 0x00000000          0
2014-10-06T21:11:02.758740 source-host pktcnt[XMT6    ] = 0x00000000          0
2014-10-06T21:11:02.758750 source-host pktcnt[XMT7    ] = 0x00000000          0
2014-10-06T21:11:02.758760 source-host pktcnt[XMT8    ] = 0x00000000          0
2014-10-06T21:11:02.758769 source-host pktcnt[CPU1-d  ] = 0x00000000          0
2014-10-06T21:11:02.758779 source-host pktcnt[RSM1-d  ] = 0x00000000          0
2014-10-06T21:11:02.758795 source-host qgroup select register: qactctl(0x800005d8)=0x0000000c, PKTCNT(0x80000598)
2014-10-06T21:11:02.758804 source-host pktcnt[XMT5    ] = 0x00000000          0
2014-10-06T21:11:02.758814 source-host pktcnt[XMT6    ] = 0x00000000          0
2014-10-06T21:11:02.758824 source-host pktcnt[XMT7    ] = 0x00000000          0
2014-10-06T21:11:02.758833 source-host pktcnt[XMT8    ] = 0x00000000          0
2014-10-06T21:11:02.758843 source-host pktcnt[PSR5    ] = 0x00000000          0
2014-10-06T21:11:02.758853 source-host pktcnt[PSR6    ] = 0x00000000          0
2014-10-06T21:11:02.758863 source-host pktcnt[PSR7    ] = 0x00000000          0
2014-10-06T21:11:02.758873 source-host pktcnt[PSR8    ] = 0x00000000          0
2014-10-06T21:11:02.758883 source-host pktcnt[PSRB    ] = 0x00000000          0
2014-10-06T21:11:02.758893 source-host pktcnt[L2Q-d   ] = 0x00000000          0
2014-10-06T21:11:02.758908 source-host qgroup select register: qactctl(0x800005d8)=0x00000014, PKTCNT(0x80000598)
2014-10-06T21:11:02.758918 source-host pktcnt[PSR1-d  ] = 0x00000000          0
2014-10-06T21:11:02.758927 source-host pktcnt[PSR2-d  ] = 0x00000000          0
2014-10-06T21:11:02.758937 source-host pktcnt[PSR3-d  ] = 0x00000000          0
2014-10-06T21:11:02.758947 source-host pktcnt[PSR4-d  ] = 0x00000000          0
2014-10-06T21:11:02.758957 source-host pktcnt[PSR5-d  ] = 0x00000000          0
2014-10-06T21:11:02.758967 source-host pktcnt[PSR6-d  ] = 0x00000000          0
2014-10-06T21:11:02.758977 source-host pktcnt[PSR7-d  ] = 0x00000000          0
2014-10-06T21:11:02.758986 source-host pktcnt[PSR8-d  ] = 0x00000000          0
2014-10-06T21:11:02.758996 source-host pktcnt[SLU-d   ] = 0x00000000          0
2014-10-06T21:11:02.759006 source-host pktcnt[SPI-d   ] = 0x00000000          0
2014-10-06T21:11:02.759022 source-host qgroup select register: qactctl(0x800005d8)=0x00000018, PKTCNT(0x80000598)
2014-10-06T21:11:02.759031 source-host pktcnt[XMT1-d  ] = 0x00000000          0
2014-10-06T21:11:02.759041 source-host pktcnt[XMT2-d  ] = 0x00000000          0
2014-10-06T21:11:02.759051 source-host pktcnt[XMT3-d  ] = 0x00000000          0
2014-10-06T21:11:02.759061 source-host pktcnt[XMT4-d  ] = 0x00000000          0
2014-10-06T21:11:02.759071 source-host pktcnt[XMT5-d  ] = 0x00000000          0
2014-10-06T21:11:02.759081 source-host pktcnt[XMT6-d  ] = 0x00000000          0
2014-10-06T21:11:02.759091 source-host pktcnt[XMT7-d  ] = 0x00000000          0
2014-10-06T21:11:02.759100 source-host pktcnt[XMT8-d  ] = 0x00000000          0
2014-10-06T21:11:02.759111 source-host pktcnt[PPA-d   ] = 0x00000000          0
2014-10-06T21:11:02.759121 source-host pktcnt[PPB-d   ] = 0x00000000          0
2014-10-06T21:11:02.759137 source-host qgroup select register: qactctl(0x800005d8)=0x00000020, PKTCNT(0x80000598)
2014-10-06T21:11:02.759147 source-host pktcnt[CPU1    ] = 0x00000000          0
2014-10-06T21:11:02.759157 source-host pktcnt[RSM2-d  ] = 0x00000000          0
2014-10-06T21:11:02.759166 source-host pktcnt[CPU3-d  ] = 0x00000000          0
2014-10-06T21:11:02.759176 source-host pktcnt[CPU4-d  ] = 0x00000000          0
2014-10-06T21:11:02.759186 source-host pktcnt[CPU5-d  ] = 0x00000000          0
2014-10-06T21:11:02.759196 source-host pktcnt[PPC-d   ] = 0x00000000          0
2014-10-06T21:11:02.759206 source-host pktcnt[PPD-d   ] = 0x00000000          0
2014-10-06T21:11:03.073075 source-host No packet loss detected in ASIC 0 witin queue XMT1-d on host testhost
2014-10-06T21:11:03.073112 source-host No packet loss detected in ASIC 0 witin queue CPU1-d on host testhost
2014-10-06T21:11:03.073124 source-host No packet loss detected in ASIC 0 witin queue  L2Q-d on host testhost
2014-10-06T21:11:03.073134 source-host No packet loss detected in ASIC 0 witin queue RSM2-d on host testhost
2014-10-06T21:11:03.073144 source-host No packet loss detected in ASIC 0 witin queue  SLU-d on host testhost
2014-10-06T21:11:03.073154 source-host No packet loss detected in ASIC 0 witin queue CPU2-d on host testhost
2014-10-06T21:11:03.073165 source-host ======================================================================
```

##Caveats

### Timing

All commands have a 1/5th of a second delay between them. This prevents there from commands being too rapidly executed.

### Multi-user sessions

There are some times when other admin sessions may impact the script. In these cases added a flag --clear-session that forces the logout of all other admin users.

### Configuration Changes

Any time a configuration change is made in ScreenOS, even if the change is reverted, the device will request to save the config. By default the script will always answer N to saving the configuration. There were some conditions in which this can cause an impact.

### Disabling paging

To make the collection of data to work correctly paging to the console is automatically disabled when the script runs. After completion the console paging is set back to the default of 20 lines.

#### Command run to disable paging

```
set console paging 0
```

#### Command run to enable paging

```
set console paging 20
```

###Usage as a library

The nsautomate script is contains two classes or modules in conjunction to the actual execution portion (the code that does the actions against the devices). It is possible to use nsautomate as a module and import it. However to simplify this you do not have to install nsautomate seperately. The module only version of this can be found at the [nsautomate](https://github.com/JNPRAutomate/nsautomate) repo.
