import click
import uvicorn
from fastapi import (
    FastAPI,
    BackgroundTasks,
    HTTPException,
)
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
)
from os.path import isfile
from cxgwebapp import (
    AppConfig,
    CliLaunchServer,
)
import multiprocessing as mp
import time
import typing
import os
from cxgbrowsersession_rtns import cxgctrl_html_response


def start_cxgctrl(urlcxg):
    app = FastAPI()

    # root
    @app.get("/", response_class=HTMLResponse)
    async def root():
        cxgbrowserstatus = "!!status!!"
        return cxgctrl_html_response(
            cxgbrowserstatus=cxgbrowserstatus,
            urlcxg=urlcxg,
        )

    uvicorn.run(app, host="0.0.0.0", port=8000)


def _launchcxgbrowser(
    datapath: str | os.PathLike,
):
    app = FastAPI()
    app_config = AppConfig()
    app_config.update_server_config(single_dataset__datapath=datapath)
    app_config.update_dataset_config(user_annotations__local_file_csv__file="./annos.csv")
    if not app_config.server_config.app__flask_secret_key:
        app_config.update_server_config(app__flask_secret_key="SparkleAndShine")
    app_config.complete_config()
    server = CliLaunchServer(app_config)
    print("_launchcxgbrowser: started server")
    app.mount("/cxg", WSGIMiddleware(server.app))
    uvicorn.run(app, host="0.0.0.0", port=8001)


def _start_cxg_in_process(
    datapath: str | os.PathLike,
    stop_event: mp.Event,
    cxg_up_time: float,
):
    process = mp.Process(
        target=_launchcxgbrowser,
        args=[datapath],
        daemon=True,
    )
    process.start()
    print(f"{time.ctime()} _start_cxg_in_process: started process")
    stop_event.wait(timeout=cxg_up_time)
    stop_event.set()
    print(f"{time.ctime()} _start_cxg_in_process: done waiting")
    process.terminate()
    process.join()
    print(process.exitcode)


def start_cxg(
    datapath: str | os.PathLike,
    stop_event: mp.Event,
    cxg_up_time: float = 10,
):
    if stop_event.is_set():
        stop_event.clear()
        process = mp.Process(
            target=_start_cxg_in_process,
            args=[
                datapath,
                stop_event,
                cxg_up_time,
            ],
        )
        process.start()
    else:
        print(f"{time.ctime()} start_cxg: Not starting stop_event.is_set()={stop_event.is_set()}")


@click.command()
@click.option("--datapath", type=click.Path(exists=True), help="Path to .h5ad file.")
@click.option("--urlcxg", type=click.STRING, help="URL for cxg browser.")
@click.option("--cxg_up_time", type=click.FLOAT, help="Up-time for cxg browser session.")
def cli(
    datapath,
    urlcxg,
    cxg_up_time,
):
    # starting cxgctrl
    mp.set_start_method("fork")
    process = mp.Process(
        target=start_cxgctrl,
        args=[
            urlcxg,
        ],
    )
    process.start()
    # starting cxg
    stop_event = mp.Event()
    stop_event.set()
    start_cxg(
        datapath=datapath,
        stop_event=stop_event,
        cxg_up_time=cxg_up_time,
    )


if __name__ == "__main__":
    cli()
