import boto3


def get_region():
    """Return the configured AWS region, or "us-east-1" if undefined."""
    return boto3.session.Session().region_name or 'us-east-1'


def get_account_id():
    """Get the AWS account id for our current credentials."""
    return boto3.resource('iam').CurrentUser().arn.split(':')[4]


def get_iam_arn_prefix():
    return "arn:aws:iam::%s" % get_account_id()


def get_event_arn_prefix():
    return "arn:aws:events:%s:%s" % (get_region(), get_account_id())


def get_role_arn(role):
    """Given a short role name, return the ARN of the role.

    eg.

    get_role_arn('lambda_basic_execution')
    "arn:aws:iam::329487123:role/lambda-basic-execution"
    """
    role = boto3.resource('iam').Role(role)
    return role.arn


def get_event_rule_arn(rule):
    """Given a short event rule name, return the ARN of the rule.

    eg.

    get_event_rule_arn('allow-from-s3')
    "arn:aws:events:us-west-2:329487123:rule/allow-from-s3"
    """
    return "%s:rule/%s" % (get_event_arn_prefix(), rule)


def get_function_arn(function):
    """Given a short function name, return the ARN of function."""
    return 'arn:aws:lambda:%s:%s:function:%s' % (
        get_region(), get_account_id(), function
    )
