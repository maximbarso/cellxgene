import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import FileResponse, HTMLResponse
import click
from os.path import isfile
from cxgwebapp import AppConfig, CliLaunchServer


@click.command()
@click.option("--datapath", type=click.Path(exists=True), help="Path to .h5ad file.")
def cxgwebapp(datapath):
    """ """
    app = FastAPI()

    # root
    def gen_html_response():
        html_content = """
        <html>
            <title>POINTCLOUDS</title>
              <style type="text/css">
                p.p1 {margin: 0.0px 0.0px 0.0px 0.0px; font: 17.0px Courier}
                p.p2 {margin: 0.0px 0.0px 0.0px 0.0px; font: 17.0px Courier; min-height: 14.0px}
                a:link {color:#000000; text-decoration:none;}
                a:visited {color:#000000; text-decoration:none;}
                a:hover {font-weight:bold;}
                span.white {
                  color:white;
                }
                pre {
                  font: 17.0px Courier;
                  width: 600px;
                  position: relative;
                }
              </style>
            </head>   
            <body>
            <pre>
            <ul>
                <li><a href="cxg/">CELLxGENE VIEWER.</a></li>
                <li><a href="annos">ANNOTATIONS.</a></li>
            </ul>
            </pre>
            </body>
        </html>
        """
        return html_content

    @app.get("/", response_class=HTMLResponse)
    async def root():
        return gen_html_response()

    # cxg
    app_config = AppConfig()
    app_config.update_server_config(single_dataset__datapath=datapath)
    app_config.update_dataset_config(user_annotations__local_file_csv__file="./annos.csv")
    if not app_config.server_config.app__flask_secret_key:
        app_config.update_server_config(app__flask_secret_key="SparkleAndShine")
    app_config.complete_config()
    server = CliLaunchServer(app_config)
    app.mount("/cxg", WSGIMiddleware(server.app))

    # annos
    @app.get("/annos")
    async def annos():
        annos_file = "./annos.csv"
        if not isfile(annos_file):
            raise HTTPException(status_code=404, detail="File does not exist.")
        return FileResponse("./annos.csv")

    # uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    app = cxgwebapp()
