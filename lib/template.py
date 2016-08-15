import pystache
from os.path import join

def render_template(template_name, function_name, output_filename=None):
    if not output_filename:
        output_filename = template_name
    template = join('templates', '%s.mustache' % template_name)
    output = join('functions/', function_name, output_filename)
    expansions = {
        'function_name': function_name
    }
    with open(template) as src, open(output, 'w') as dst:
        dst.write(pystache.render(src.read(), expansions))
