import os
import fastapi
from fastapi import Query
from typing import Optional
from services import FileRepository
from depends import *
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
from services.graph import (
    get_file_graph,
    get_tag_graph
)


api_graph_router = fastapi.routing.APIRouter()
templates = Jinja2Templates(
    directory=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    )
)

@api_graph_router.get(
        "/{node_type}/{id}",
        description="Граф связей для файла"

)
async def api_graph(
    id: str,
    node_type: str,
    request: Request,
    repository: FileRepository = fastapi.Depends(FileRepositoryRequired),
    
):
    
    graph_data = await get_file_graph(repository, id)
    #graph_data = fake_data_for_graf
    print('graph_data: ', graph_data)
    modal_html = templates.TemplateResponse(
        "graph/graph.html", 
        {"request": request, "graph": graph_data}
    ).body.decode("utf-8")
    
    # 3. Возвращаем эту HTML-строку (фронтенд вставит её в модалку)
    return HTMLResponse(content=modal_html)

@api_graph_router.get(
        "/{node_type}/{id}/json",
        description="Возвращаем новый JSON для перерисовки графа"

)
async def api_graph_json(
    id: str,
    node_type: str,
    request: Request,
    repository: FileRepository = fastapi.Depends(FileRepositoryRequired),
    
):
    graph_data = {} 
    if node_type == "tag":
        graph_data = await get_tag_graph(repository, id)
    elif node_type == "file":
        graph_data = await get_file_graph(repository, id)
    print('graph_data: ', graph_data)
    return graph_data