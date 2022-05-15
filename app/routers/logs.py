import time
from fastapi import APIRouter
from app.library.logger import read_logs
router = APIRouter()

@router.get('/api/logs')
async def check_logs():
    logs = read_logs()
    update_at = time.time()
    return {"logs": logs, "update_at": update_at}
