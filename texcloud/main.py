import os
import shutil

from uvicorn.logging import logging
from uuid import UUID
from starlette.applications import Starlette
from starlette.datastructures import UploadFile
from starlette.responses import JSONResponse, PlainTextResponse, FileResponse, Response
from starlette.requests import Request
from starlette.routing import Route
from starlette.endpoints import HTTPEndpoint
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("uvicorn:error")


class TexProject(HTTPEndpoint):
    def get(self, request: Request):
        id = request.path_params["project_id"]
        return PlainTextResponse(f"{id}")


class FileStorage(HTTPEndpoint):
    root = os.environ["FILE_ROOR"]

    def get(self, request):
        """
        获取文件或目录
        """
        id: UUID = request.path_params["project_id"]
        fp = self._get_file_path(id, request.path_params["file_path"])
        if os.path.isdir(fp):
            return JSONResponse(self._listdir(fp))
        elif os.path.isfile(fp):
            return FileResponse(path=fp)
        else:
            return Response(status_code=404)

    async def post(self, request: Request):
        """
        上传文件
        """
        id: UUID = request.path_params["project_id"]
        form = await request.form()
        fp = self._get_file_path(id, request.path_params["file_path"])
        upload_file: UploadFile = form.get("file")
        try:
            await self._save_file(fp, upload_file)
            return Response(status_code=201)
        except Exception as err:
            logger.warn(str(err))
            return Response(status_code=403)

    def delete(self, request):
        """
        删除文件
        """
        id: UUID = request.path_params["project_id"]
        fp = self._get_file_path(id, request.path_params["file_path"])
        if os.path.isdir(fp):
            shutil.rmtree(fp)
        elif os.path.isfile(fp):
            os.unlink(fp)
        return Response(status_code=204)

    def _get_file_path(self, project_id: UUID, fp):
        return os.path.join(self.root, str(project_id), fp)

    async def _save_file(self, fp, upload_file: UploadFile):
        if (not os.path.isfile(fp)) and (not os.path.isdir(fp)):
            os.makedirs(fp, exist_ok=True)
        else:
            raise Exception("不合法的存储路径")
        filename = upload_file.filename
        with open(os.path.join(fp, filename), "wb") as f:
            while chunck := await upload_file.read(1024 * 1024):
                f.write(chunck)

    def _listdir(self, fp):
        """
        列出fp下所有的文件以及目录
        """
        files = os.listdir(fp)
        ret = []
        for filename in files:
            ret.append(
                {
                    "filename": filename,
                    "is_dir": os.path.isdir(os.path.join(fp, filename)),
                }
            )
        return ret


def index(request):
    return PlainTextResponse("你好世界")


routes = [
    Route("/", index),
    Route("/projects/{project_id:uuid}", TexProject),
    Route("/files/{project_id:uuid}/{file_path:path}", FileStorage),
]

app = Starlette(routes=routes)
