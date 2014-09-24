#NetScreen Microburst Detector

This tool allows you to detect microbursts within an ASIC-Based NetScreen platform

#Python Requirements

This code was tested on Python 2.7, however it most likely would work within other releases depending on the support of the required libraries.

The majority of modules used within this tool are contained within the Python standard library.

However there are some additonal libraries that you need to install.

1) ecdsa==0.11 2) paramiko==1.14.1 3) pycrypto==2.6.1 4) wsgiref==0.1.2

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
usage: nsautomate.py [-h] [---output] [---no-output] [--csv CSVFile]
                     [--host HOST] [--username USERNAME] [--password PASSWORD]
                     [--password-secure]

Gather options from the user

optional arguments:
  -h, --help           show this help message and exit
  ---output            Specify if you want to print output to standard out.
                       Defaults to printing output.
  ---no-output         Specify if you do not want to print output to standard
                       out.
  --csv CSVFile        Specify the CSV file to read hosts from.
  --host HOST          Specify single host to connect to. Can not be used with
                       --csv.
  --username USERNAME  Specify the default username to use when not specified
                       within the csv.
  --password PASSWORD  Specify the default password to use when not specified
                       within the csv.
  --password-secure    Be prompted for the the default password.

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
Connecting to host 172.22.152.24
Unable to connect to host: 172.22.152.24

======================================================================
Connecting to host lattern.spglab.juniper.net
Unable to connect to host: lattern.spglab.juniper.net
```
