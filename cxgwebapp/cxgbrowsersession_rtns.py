def cxgctrl_html_response(
    urlcxg,
    cxgbrowserstatus,
):
    html_content = """
    <html>
        <title>POINTCLOUDS</title>
          <style type="text/css">
            p.p1 {{margin: 0.0px 0.0px 0.0px 0.0px; font: 17.0px Courier}}
            p.p2 {{margin: 0.0px 0.0px 0.0px 0.0px; font: 17.0px Courier; min-height: 14.0px}}
            a:link {{color:#000000; text-decoration:none;}}
            a:visited {{color:#000000; text-decoration:none;}}
            a:hover {{font-weight:bold;}}
            span.white {{
              color:white;
            }}
            pre {{
              font: 17.0px Courier;
              width: 600px;
              position: relative;
            }}
          </style>
        </head>   
        <body>
        <pre>
        <ul>
            <li><a href="cxg/">CELLxGENE VIEWER.</a></li>
            <li><a href="annos">ANNOTATIONS.</a></li>
            <li><a href="{urlcxg}">{cxgbrowserstatus} START CELLxGENE VIEWER.</a></li>
        </ul>
        </pre>
        </body>
    </html>
    """.format(
        cxgbrowserstatus=cxgbrowserstatus,
        urlcxg=urlcxg,
    )
    return html_content
