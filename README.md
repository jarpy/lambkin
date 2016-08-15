Lambkin
=======
Lambkin is CLI tool for generating and managing simple functions in AWS Lambda.

Supporting Node.js and Python, Lambkin generates skeleton functions, provides
lightweight help for managing dependencies, and does its best to hide the
complexity of publishing and running functions in Lambda.

Quick Start
===========

Prerequisites
-----------
* A valid `~/.aws/config` file. eg.
```
[default]
region = us-east-1
```
* A valid `~/.aws/credentials` file. eg.
```
[default]
aws_access_key_id = AKIAUAVOHGHOOWEEYIED
aws_secret_access_key = 90kX2Y2bykTH9CpQFHCzN92tukYf26
```

* Fork and clone this repository. Then the functions you create can be committed
into your fork, if you so choose.

* From within your cloned repository:
``` bash
virtualenv --python=python2.7 venv
source venv/bin/activate
pip install --requirement=requirements.txt
```
The virtualenv setup is not strictly necessary, but Python 2.7 is recommended,
since that's the version currently supported on Lambda itself.


Examples
--------

#### Create a new Python function from a basic template

``` bash
./lambkin create cool-func
$EDITOR functions/cool-func/cool-func.py
```

#### ...or a maybe you prefer Node.js

``` bash
./lambkin create cool-func --runtime=nodejs
$EDITOR functions/cool-func/cool-func.js
```

#### Install packages and dependencies for your function

``` bash
$EDITOR functions/cool-func/Makefile
./lambkin make cool-func
```

#### Bundle up your function (with libraries) and send it to Lambda

``` bash
./lambkin publish cool-func --description 'The best function ever.'
```

#### Increase the timeout for a long-running function

``` bash
./lambkin publish cool-func --description 'Slow' --timeout=300
```

#### Invoke the published function, right now!

``` bash
./lambkin run cool-func
```

#### Remove the function from Lambda, but keep it locally.

``` bash
./lambkin unpublish cool-func
```
