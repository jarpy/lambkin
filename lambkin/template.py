import pystache
from os.path import join
from textwrap import dedent


def render_template(template_name, function_name, output_filename=None):
    if not output_filename:
        output_filename = template_name
    output = join(function_name, output_filename)
    expansions = {
        'function_name': function_name
    }
    with open(output, 'w') as dst:
        dst.write(pystache.render(templates[template_name], expansions))

templates = {
    'python': dedent(
        """
        # {{function_name}}.py: An AWS Lambda function.
        #
        # To run this function in Lambda, you need to bundle all the libraries you use.
        # Even something as mundane as:
        #   import requests
        # won't work by default.
        #
        # To install a library (like "requests") into your Lambda function, edit
        # the requirements.txt in your function's directory, then run:
        #
        #  lambkin build
        #
        # The files installed by pip are all "gitignored" by default, so they don't
        # get commited. In fact, almost everything is ignored, so if you want to add
        # and commit more than just your script, you'll need to explicitly list things
        # in "functions/{{function_name}}/.gitignore".
        #
        #
        #
        # Here is the entry point for Lambda. Execution starts here when an
        # event triggers us to run.
        #
        # Lambda passes us two objects, the event that triggered us, and a 'context'
        # object for this execution.

        def handler(event, context):
            # To log to Cloudwatch, just:
            print "anything you like."

            optional_return_value = {
                "hello": "World",
                "from": "Python"
            }

            return optional_return_value  # which often becomes a JSON response.
        """[1:]),

    'makefile': dedent("""
        {{function_name}}:
        	@echo "make" called for {{function_name}}
        	# npm install --prefix=. aws-sdk
        """[1:]),

    'nodejs': dedent(
        """
        // {{function_name}}.js: An AWS Lambda function.

        exports.handler = function(event, context, callback) {
          console.log("Running in Lambda...");

          // An abitrary object.
          result = {
            "hello": "World",
            "from": "Node.js"
          };

          // This example uses an NPM package. Look in the "Makefile" to see how to
          // install packages for your Lambda function.
          //
          // var yaml = require('js-yaml');
          // console.log(yaml.safeDump(result));

          // Lambda will emit the "result" object as the output of our function.
          callback(null, result);
        }
        """[1:]),

    'gitignore': dedent(
        """
        # If this Lambda function uses any libraries, they will be here in the
        # source directory.
        #
        # We don't want to commit copies of 3rd party libraries to our repository,
        # so by default we will ignore _everything_ in the source dir:
        *
        # ...except for some things we want to commit:
        !{{function_name}}.*
        !metadata.json
        !Makefile
        !.gitignore
        """[1:]),

    'gitignore-python': dedent(
        """
        /venv
        """[1:]),

    'requirements': dedent(
        """
        # Declare requirements for your Python Lambda function here.
        #
        # eg.
        # requests>=2
        """[1:])
}
