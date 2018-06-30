import dash_html_components as html

footer = html.Div(
    id='footer',
    className='footer',
    children=html.Div(
        className='container-width',
        style={'height': '100%', 'text-align': 'center'},
        children=[
            html.Div(className="links", children=[
                html.A(u'Link to twitter feed', className="link", href="https://twitter.com/jaaaaam"),
            ])
        ]
    )
)

header = html.Div(
    className='header',
    children=html.Div(
        className='container-width',
        style={'height': '100%'},
        children=[
            html.A(
            html.Img(
                src="https://user-images.githubusercontent.com/29542097/42127641-d0caa1ce-7c9c-11e8-94ac-d181af932fd2.png",
                className="logo"),
            href='http://spacescience.ie/', className="logo-link"),

            html.Div(className="links", children=[
                html.A('GMoDem  Balloon Flight 2018', className="link active", href="#"),
                html.A('Space Science @ UCD', className="link", href="http://spacescience.ie/"),
            ])
        ]
    )
)
