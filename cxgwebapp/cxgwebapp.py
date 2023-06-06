import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import FileResponse
import click
from os.path import isfile
from cxgwebapp import AppConfig, CliLaunchServer


@click.command()
@click.option("--datapath", type=click.Path(exists=True), help="Path to .h5ad file.")
def cxgwebapp(datapath):
    """ """
    app = FastAPI()

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
