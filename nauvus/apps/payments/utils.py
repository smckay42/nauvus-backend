

def create_invoice_pdf(context):

    template = 'payments/invoice.html'

    filename = 'Invoice_{}.pdf'.format(load.id)

    template = get_template(template)
    html_string = template.render(context)

    # create a pdf
    font_config = FontConfiguration()
    html = HTML(string=html_string)

    css_config = open('core/static/css/laudo.css', 'r').read()

    css = CSS(string=css_config, font_config=font_config)
    html.write_pdf(target='media/{}'.format(filename), presentational_hints=True, font_config=font_config,
                   stylesheets=[css])
