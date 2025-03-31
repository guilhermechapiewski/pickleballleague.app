import os
import logging
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class TemplateEngine:
    template_dir = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/templates/"
    env = Environment(loader=FileSystemLoader(template_dir))

    @classmethod
    def render(cls, template_name, context={}):
        template = cls.env.get_template(f"{template_name}.html")
        return template.render(context)
