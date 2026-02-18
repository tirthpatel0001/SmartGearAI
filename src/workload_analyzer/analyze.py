from datetime import datetime
from .db import get_connection

SHIFT_MINUTES = 8 * 60  # 8-hour shift

def analyze_workload(gear_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT total_steps, completed_steps, start_time, last_update, machine_status
        FROM production_logs
        WHERE gear_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (gear_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return {"error": "Gear ID not found"}

    total_steps, completed_steps, start_time, last_update, machine_status = row

    start_time = datetime.fromisoformat(start_time)
    last_update = datetime.fromisoformat(last_update)

    if completed_steps == 0:
        elapsed_minutes = 0
        remaining_minutes = 0
        progress = 0
        shifts_required = 0
    else:
        elapsed_minutes = (last_update - start_time).total_seconds() / 60
        progress = (completed_steps / total_steps) * 100
        estimated_total = (elapsed_minutes / completed_steps) * total_steps

        # Machine status penalty
        if machine_status == "STOPPED":
            estimated_total /= 0.6
        remaining_minutes = max(0, estimated_total - elapsed_minutes)
        shifts_required = estimated_total / SHIFT_MINUTES

    return {
        "gear_id": gear_id,
        "progress_percent": round(progress, 2),
        "elapsed_minutes": round(elapsed_minutes, 2),
        "remaining_minutes": round(remaining_minutes, 2),
        "machine_status": machine_status,
        "shifts_required": round(shifts_required, 2)
    }
