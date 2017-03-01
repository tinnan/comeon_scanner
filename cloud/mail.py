from jinja2 import Environment, PackageLoader, select_autoescape

ENV = Environment(
    loader=PackageLoader('cloud', 'mail_templates'),
    autoescape=select_autoescape(['html'])
)
