import sqlite3

DB_NAME = "course.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plan(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            days_left INTEGER NOT NULL,
            hours_per_day REAL NOT NULL,
            plan_text TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def save_plan(subject: str,days_left: int,hours_per_day: float,plan_text: str) -> str:
    con = sqlite3.connect(DB_NAME)
    cursor = con.cursor()
    cursor.execute(
        """
        INSERT INTO plan (subject,days_left,hours_per_day,plan_text)
        VALUES(?,?,?,?)
        """,
        (subject,days_left,hours_per_day,plan_text)
    )
    con.commit()
    new_id = cursor.lastrowid
    con.close()
    return f"已保存计划,编号{new_id},科目: {subject}"

def get_plan(plan_id: int=0)-> str:
    """

    查询复习计划
    如果传了plan_id就传这条;
    如果不传或传0,就查全部.
    
    """
    con = sqlite3.connect(DB_NAME)
    cursor = con.cursor()
    if plan_id > 0:
        cursor.execute(
            "SELECT id,subject,days_left,hours_per_day,plan_text,created_at FROM plan WHERE id = ?",
            (plan_id,)
        )
    else :
        cursor.execute(
            "SELECT id,subject,days_left,hours_per_day,plan_text,created_at FROM plan ORDER BY id DESC"
        )
    rows = cursor.fetchall()
    con.close()
    if not rows:
        return "没有找到计划."
    result_lines = []
    for row in rows:
        plan_id_val,subject,days_left,hours_per_day,plan_text,created_time=row
        result_lines.append(
            f"编号 {plan_id_val}｜{subject}｜剩 {days_left} 天｜每天 {hours_per_day} 小时｜{plan_text}｜创建于 {created_time}"
        )
    return "\n".join(result_lines)

def update_plan(plan_id:int,days_left:int =0,hours_per_day:float=0)->str:
    con = sqlite3.connect(DB_NAME)
    cursor = con.cursor()
    cursor.execute("SELECT  id,subject,days_left,hours_per_day,plan_text,created_at FROM plan WHERE id = ?",(plan_id,))
    row = cursor.fetchone()
    ans = ""
    if row is None:
        ans = f"未查找到{plan_id}计划,更新失败"
    else:
        plan_id_val,subject,days_left_val,hours_per_day_val,plan_text,created_time = row
        if days_left == 0 and hours_per_day == 0:
            ans = "未输入有效天数和每日学习时长"
        elif days_left == 0 and  hours_per_day>0:
            cursor.execute("UPDATE plan SET hours_per_day = ? WHERE id = ?",(hours_per_day,plan_id))
            con.commit()
            ans = f"已更新编号 {plan_id} 的计划：{subject}，剩 {days_left_val} 天，每天 {hours_per_day} 小时。"
        elif days_left > 0 and  hours_per_day==0:
            cursor.execute("UPDATE plan SET days_left = ? WHERE id = ?",(days_left,plan_id))
            con.commit()
            ans = f"已更新编号 {plan_id} 的计划：{subject}，剩 {days_left} 天，每天 {hours_per_day_val} 小时。"
        else : 
            cursor.execute("UPDATE plan SET days_left = ?,hours_per_day = ? WHERE id = ?",(days_left,hours_per_day,plan_id))
            ans = f"已更新编号 {plan_id} 的计划：{subject}，剩 {days_left} 天，每天 {hours_per_day} 小时。"
            con.commit()
    con.close()
    return ans


if __name__ == "__main__":
    init_db()
    print("=== 改动前 ===")
    print(get_plan(1))

    print("=== 只改天数 ===")
    print(update_plan(1, 3))
    print(get_plan(1))

    print("=== 只改小时数 ===")
    print(update_plan(1, 0, 4))
    print(get_plan(1))

    print("=== 两个都改 ===")
    print(update_plan(1, 20, 5))
    print(get_plan(1))

    print("=== 编号不存在 ===")
    print(update_plan(999, 5))

    print("=== 两个都不传 ===")
    print(update_plan(1, 0, 0))
    print(get_plan(1))
