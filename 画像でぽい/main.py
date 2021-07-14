
from flask import Flask, render_template, request
import base64, io
import db_plus_dx as dpd
import matplotlib.pyplot as plt
 
app = Flask(__name__)
TARGET_DB_FILE_NAME = dpd.SQL_FILE_NAME_MAIN
TARGET_TABLE = "students_core"

class plot_mine_alpha:
	def __init__(self, dpi_config, alpha=1):
		plt.rcParams["font.family"] = "Yu Gothic" #日本語化
		self.fig = plt.figure(dpi=dpi_config, figsize=(7,4))
		self.alpha = alpha
	def plotScatter(self, xy_tuple_list, col, color_label, s=1):
		x_list = []
		y_list = []
		for v in xy_tuple_list:
			#if v[0] is not None and v[1] is not None:
			vv = [0 if b is None else b for b in v]
			x_list.append(vv[0])
			y_list.append(vv[1])
		plt.scatter(x_list, y_list, s=s, color=col, alpha=self.alpha)
		plt.scatter([], [], label=color_label, s=5, color=col) #ダミープロット
	def plotBase(self, label_x, label_y, title=None):
		plt.xlabel(label_x)
		plt.ylabel(label_y)
		if title is not None:
			plt.title(title)
		plt.grid(which='both', color='black', lw=0.2, ls='--')

def plot_basic(command):
	teg = plot_mine_alpha(300, 0.1) #DPI, 透過率
	data = dpd.protect_execute(command)
	teg.plotScatter(data, color_list[i], color_label_list[i])
	teg.plotBase(label_x, label_y)
	plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left")
	fig = teg.fig
	fig.tight_layout() #拡大縮小対応
	#plt.legend(loc="upper right")

# ルーティング
@app.route("/", methods=["GET"])
def index():
    title_list, flag = dpd.title_list_return(target_file_name=dpd.TITLE_LIST_FILE_CONVERT_DICT[(TARGET_TABLE, TARGET_DB_FILE_NAME)], not_use_non_print=True)
    title_list_ja = [tl["japanese_name"] for tl in title_list if tl["type"] in ["REAL", "INTEGER"]]
    return render_template("./index.html", 
                           x_select_list=[(tl, "") for tl in title_list_ja], 
                           y_select_list=[(tl, "") for tl in title_list_ja]
    )

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
            


            teg = plot_mine_alpha(300, 1) #DPI, 透過率
            teg.plotScatter(data, "#0000FF", "のーまる", s=10)
            teg.plotBase(x_option_ja, y_option_ja)
            plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left")
            fig = teg.fig
            fig.tight_layout() #拡大縮小対応

            my_html = '<img id="plot_data" src="data:image/png;base64, {0}">'.format(fig_to_base64(fig).decode('utf-8'))

            
            return render_template("./index.html", image_data=my_html, title=text,
                                x_select_list=[(tl, "" if tl != x_option_ja else " selected") for tl in title_list_jn],
                                y_select_list=[(tl, "" if tl != y_option_ja else " selected") for tl in title_list_jn]
            )
        else:
            return render_template("./index.html", x_select_list=title_list, y_select_list=title_list, image_data="")
    else:
        return render_template("./index.html", x_select_list=title_list, y_select_list=title_list, image_data="")

def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png',
                bbox_inches='tight')
    img.seek(0)
    return base64.b64encode(img.getvalue())



if __name__ == "__main__":
    app.run(port=8000, debug=True)