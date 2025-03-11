from jinja2 import Environment, FileSystemLoader

class TemplateEngine:    
    def render(self, template_name, context=None):
        # Setup Jinja environment
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template(f"./templates/{template_name}.html")
        return template.render(context)
