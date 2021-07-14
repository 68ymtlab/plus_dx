
from flask import Flask, render_template, request
import db_plus_dx as dpd
 
app = Flask(__name__)
TARGET_DB_FILE_NAME = dpd.SQL_FILE_NAME_MAIN
TARGET_TABLE = "students_core"

# ルーティング
@app.route("/", methods=["GET"])
def index():
    title_list, flag = dpd.title_list_return(target_file_name=dpd.TITLE_LIST_FILE_CONVERT_DICT[(TARGET_TABLE, TARGET_DB_FILE_NAME)], not_use_non_print=True)
    title_list_ja = [tl["japanese_name"] for tl in title_list if tl["type"] in ["REAL", "INTEGER"]]
    return render_template("./index.html", x_select_list=[(tl, "") for tl in title_list_ja], y_select_list=[(tl, "") for tl in title_list_ja])

@app.route("/", methods=["POST"])
def sql_getter():
    title_list, flag = dpd.title_list_return(target_file_name=dpd.TITLE_LIST_FILE_CONVERT_DICT[(TARGET_TABLE, TARGET_DB_FILE_NAME)], not_use_non_print=True)
    title_list_jn = [tl["japanese_name"] for tl in title_list if tl["type"] in ["REAL", "INTEGER"]]
    x_option_ja = request.form.get("x_select_option")
    y_option_ja = request.form.get("y_select_option")
    if x_option_ja is not None and y_option_ja is not None:
        x_option = dpd.search_to_from(x_option_ja, sorce="japanese_name", target="name", pickup_table_and_db_list=[(TARGET_TABLE, TARGET_DB_FILE_NAME)])
        y_option = dpd.search_to_from(y_option_ja, sorce="japanese_name", target="name", pickup_table_and_db_list=[(TARGET_TABLE, TARGET_DB_FILE_NAME)])
        text = "SELECT {0}, {1} FROM {2}".format(x_option, y_option, TARGET_TABLE)
        data = dpd.protect_execute(text, db_file_name=TARGET_DB_FILE_NAME, ignore_mode=False)
        print(True if data is not None else False)
        if data is not None:
            data = [d for d in data if d[0] is not None and d[1] is not None]
            x_limit_min = min([d[0] for d in data])
            x_limit_max = max([d[0] for d in data])
            y_limit_min = min([d[1] for d in data])
            y_limit_max = max([d[1] for d in data])
            return render_template("./plot.html", data=data, title=text,
                                x_limit_min=x_limit_min, x_limit_max=x_limit_max, 
                                y_limit_min=y_limit_min, y_limit_max=y_limit_max, 
                                x_select_list=[(tl, "" if tl != x_option_ja else " selected") for tl in title_list_jn],
                                y_select_list=[(tl, "" if tl != y_option_ja else " selected") for tl in title_list_jn]
            )
        else:
            return render_template("./index.html", x_select_list=title_list, y_select_list=title_list)
    else:
        return render_template("./index.html", x_select_list=title_list, y_select_list=title_list)
 
if __name__ == "__main__":
    app.run(port=8000, debug=True)