#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
import base64, io, time
import db_plus_dx as dpd
import matplotlib.pyplot as plt
 
app = Flask(__name__)
TARGET_DB_FILE_NAME = dpd.SQL_FILE_NAME_MAIN
TARGET_TABLE = "students_core"
ONE_STUDENT_TARGET_TABLE = "students_plus"
FIRST_CODE_LIMIT = 10
SECOND_CODE_LIMIT = 10
DEFAULT_COLOR_CODE = "#0000FFFF"
MAX_TITIE_LEN = 35

def number_converter(title, symbol, value):
	#print("number_converter({0}, {1}, {2})".format(title, symbol, value))
	number_convert_dict = {"x_equal":"==", 
						   "x_non_equal":"!=", 
						   "x_upper_y":">", 
						   "x_upper_equal_y":">=", 
						   "x_lower_y":"<", 
						   "x_lower_equal_y":"<=", 
						   "x_is_null":"IS NULL", 
						   "x_is_not_null":"IS NOT NULL"
	}
	if symbol in ["x_is_null", "x_is_not_null"]:
		return "{0} {1}".format(title, number_convert_dict[symbol])
	else:
		return "{0} {1} {2}".format(title, number_convert_dict[symbol], value)

def text_converter(title, symbol, value):
	#print("text_converter({0}, {1}, {2})".format(title, symbol, value))
	if "x_equal" == symbol:
		return "{0} == {1}".format(title, dpd.value_char_filter(value))
	elif "x_non_equal" == symbol:
		return "{0} != {1}".format(title, dpd.value_char_filter(value))
	elif "x_like_yo" == symbol:
		return "{0} LIKE {1}||'%'".format(title, dpd.value_char_filter(value))
	elif "x_like_oy" == symbol:
		return "{0} LIKE '%'||{1}".format(title, dpd.value_char_filter(value))
	elif "x_like_oyo" == symbol:
		return "{0} LIKE '%'||{1}||'%'".format(title, dpd.value_char_filter(value))
	elif "x_is_null" == symbol:
		return "{0} IS NULL".format(title)
	elif "x_is_not_null" == symbol:
		return "{0} IS NOT NULL".format(title)
	else:
		return None

def sql_text_maker(priority_code_list, connect_symbol_list, inner_sql_list):
	#print("priority_code_list : {0}".format(priority_code_list))
	#print("connect_symbol_list : {0}".format(connect_symbol_list))
	#print("inner_sql_list : {0}".format(inner_sql_list))
	#inner_sql_list : 接続するSQL文の破片
	#connect_symbol_list : AND や OR (接続しない場合のNone)
	#priority_code_list : 優先度 最高0 , 1 , 2 , 3,  4最低から構成
	#
	#入力 例
	#inner_sql_list = ["a==2", "b!='nami'", "c>=0", "c<10", "d!=0"]
	#connect_symbol_list = ["AND", "OR", "OR", "AND"]
	#priority_code_list = [2, 1, 0, 0, 1]
	#
	#出力 例
	# a==2 AND (b!='nami' OR (c>=0 OR c<10) AND d!=0)
	#
	if len(priority_code_list) != len(inner_sql_list):
		raise ValueError("len(connect_symbol_list)={0}, len(priority_code_list)={1}, len(inner_sql_list)={2}".format(len(connect_symbol_list), len(priority_code_list), len(inner_sql_list)))
	if len(inner_sql_list) - 1 != len(connect_symbol_list):
		raise ValueError("len(connect_symbol_list)={0}, len(priority_code_list)={1}, len(inner_sql_list)={2}".format(len(connect_symbol_list), len(priority_code_list), len(inner_sql_list)))
	max_priority = max(priority_code_list)
	min_priority = min(priority_code_list)
	buf_right = [0 for _ in range(len(connect_symbol_list) + 2)] #(
	buf_left = [0 for _ in range(len(connect_symbol_list) + 2)] #)
	for p in range(min_priority, max_priority + 1):
		buf = [False for _ in range(len(connect_symbol_list))]
		for code in range(len(priority_code_list) - 1):
			if priority_code_list[code] == priority_code_list[code + 1] and priority_code_list[code] == p:
				buf[code] = True
		priority_code_list = [(pp + 1 if pp == p else pp) for pp in priority_code_list]
		#1次元オートマトンもどき
		padding_plus_buf = [False, False] + buf + [False, False] #両側にpadding追加
		for code in range(0, len(buf) + 2):
			if padding_plus_buf[code + 2] and not(padding_plus_buf[code + 1]):
				buf_right[code] += 1
			if padding_plus_buf[code] and not(padding_plus_buf[code + 1]):
				buf_left[code] += 1
	sql_buf = "{0}{1} ".format("(" * buf_right[0], inner_sql_list[0])
	#print("[C]: {0}{1} ".format("(" * buf_right[0], inner_sql_list[0])) #確認
	for code in range(1, len(buf) + 1):
		sql_buf += "{0} {1} {2}{3}".format(")" * buf_left[code],  connect_symbol_list[code - 1], "(" * buf_right[code], inner_sql_list[code])
		#print("[C]: {0} {1} {2}{3}".format(")" * buf_left[code],  connect_symbol_list[code - 1], "(" * buf_right[code], inner_sql_list[code])) #確認
	sql_buf += "{0}".format(")" * buf_left[-1])
	#print("[C]: {0}".format(")" * buf_left[-1])) #確認
	#print("sql_buf : {0}".format(sql_buf)) #確認
	return sql_buf

def data_getter():
	color_title_list, color_list, main_list, priority_convert_dict = [], [], [], {"max":0, "high":1, "default":2, "low":3, "min":4}
	for first_code_one in reversed(range(FIRST_CODE_LIMIT)):
		first_select = request.form.get("first_select_set_{0}".format(first_code_one))
		if first_select is not None and first_select != "non_select":
			if first_select == "nonal_select":
				inner_sql_list, connect_symbol_list, priority_code_list = [], [], []
				for second_code_one in range(SECOND_CODE_LIMIT):
					second_select = request.form.get("second_select_set_{0}_{1}".format(first_code_one, second_code_one))
					if second_select is None or "," not in second_select:
						#print("[break]: {0}".format("second_select: | {0} = {1}".format("second_select_set_{0}_{1}".format(first_code_one, second_code_one), second_select)))
						continue
					return_text = None
					title = dpd.search_to_from(",".join(second_select.split(",", 1)[1:]), sorce="japanese_name", target="name", pickup_table_and_db_list=[(TARGET_TABLE, TARGET_DB_FILE_NAME)])
					if second_select.split(",", 1)[0].upper() in ["REAL", "INTEGER"]:
						symbol = request.form.get("nomal_control_{0}_{1}_number_mode".format(first_code_one, second_code_one))
						value = request.form.get("nomal_control_{0}_{1}_number".format(first_code_one, second_code_one))
						return_text = number_converter(title, symbol, value)
					elif second_select.split(",", 1)[0].upper() in ["TEXT"]:
						symbol = request.form.get("nomal_control_{0}_{1}_text_mode".format(first_code_one, second_code_one))
						value = request.form.get("nomal_control_{0}_{1}_text".format(first_code_one, second_code_one))
						return_text = text_converter(title, symbol, value)
					priority_code = request.form.get("priority_{0}_{1}_select".format(first_code_one, second_code_one))
					if priority_code is None or priority_code not in [k for k in priority_convert_dict.keys()]:
						#print("[break]: {0}".format("if priority_code is None or priority_code not in [k for k in priority_convert_dict.keys()]:"))
						continue
					inner_sql_list.append(return_text) #ワード
					priority_code_list.append(priority_convert_dict[priority_code]) #優先度
					if second_code_one < SECOND_CODE_LIMIT - 1:
						connect_symbol = request.form.get("nomal_control_{0}_{1}_connecter_select".format(first_code_one, second_code_one))
						if connect_symbol is not None and connect_symbol.upper() in ["AND", "OR"]:
							connect_symbol_list.append(connect_symbol.upper()) #接続
						else:
							#print("[break]: {0}".format("else:"))
							break
				main_list.append(" WHERE {0}".format(sql_text_maker(priority_code_list, connect_symbol_list, inner_sql_list))) #生成
			elif first_select == "sql_select":
				sql_buf = request.form.get("sql_input_area_{0}".format(first_code_one))
				if sql_buf is not None:
					main_list.append(" {0}".format(sql_buf))
			if first_select in ["sql_select", "nonal_select"] and len(color_list) == len(main_list) - 1:
				color_buf = request.form.get("color_input_{0}".format(first_code_one))
				alpha_buf = request.form.get("alpha_input_{0}".format(first_code_one))
				color_title_buf = request.form.get("color_title_{0}".format(first_code_one))
				if color_title_buf is None:
					color_title_buf = "不明なタイトル"
				color_title_list.append(color_title_buf)
				if color_buf is not None and alpha_buf is not None and int(alpha_buf) >= 0 and int(alpha_buf) <= 255:
					color_list.append("{0}{1:0>2}".format(color_buf, format(int(alpha_buf), "x")))
				else:
					color_list.append(DEFAULT_COLOR_CODE)
	if len(main_list) < 1:
		return ([""], [DEFAULT_COLOR_CODE], ["タイトルなし"])
	else:
		return (main_list, color_list, color_title_list)

def text_split2b(text, start, end): #2byte文字切り取り用
	counter, return_buf = 0, ""
	for t in text:
		buf_counter = dpd.len2b("{0}".format(t))
		if counter >= start and counter < end:
			return_buf += t
		elif counter >= end:
			break
		counter += buf_counter
	return return_buf

@app.template_filter("num_right_p1") #フィルター
def num_right(target):
	try:
		count = len(str(FIRST_CODE_LIMIT)) - len(str(target + 1))
		return "{0}{1}".format(count*"&ensp;", target + 1)
	except ValueError:
		return target

# ルーティング
@app.route("/", methods=["GET"])
def index():
	return sql_getter("none")

@app.route("/", methods=["POST"])
def sql_getter(block_config="block"):
	#print("[ 確認 ]")
	#for k, v in request.form.items():
	#	print("{0:<60} = {1}".format(k, v))
	#print("-"*60)
	return_input_dict = {k:v for k, v in request.form.items() if k != "flag_for_download"} #除外
	title_list, flag = dpd.title_list_return(target_file_name=dpd.TITLE_LIST_FILE_CONVERT_DICT[(TARGET_TABLE, TARGET_DB_FILE_NAME)], not_use_non_print=True)
	title_list_jn = [tl["japanese_name"] for tl in title_list if tl["type"] in ["REAL", "INTEGER"]]
	ja_na_convert_dict = {tl["japanese_name"]:tl["name"] for tl in title_list if tl["type"] in ["REAL", "INTEGER"]}
	title_list_ty = [(tl["japanese_name"], tl["type"]) for tl in title_list if tl["type"] in ["REAL", "INTEGER", "TEXT"]]
	x_option_jn = request.form.get("x_select_option")
	y_option_jn = request.form.get("y_select_option")
	plot_size = request.form.get("plot_size_select")
	try:
		if plot_size is None:
			print("plot_size IS NONE")
			raise ValueError
		plot_size = abs(float(plot_size))
	except ValueError:
		plot_size = 1.0
		print("plot_size ERROR")
	if x_option_jn is not None and y_option_jn is not None:
		load_flag = request.form.get("flag_for_download")
		if load_flag is not None and load_flag in ["0", "1"]:
			load_flag = load_flag
		else:
			load_flag = 0
		x_option = dpd.search_to_from(x_option_jn, sorce="japanese_name", target="name", pickup_table_and_db_list=[(TARGET_TABLE, TARGET_DB_FILE_NAME)])
		y_option = dpd.search_to_from(y_option_jn, sorce="japanese_name", target="name", pickup_table_and_db_list=[(TARGET_TABLE, TARGET_DB_FILE_NAME)])
		try:
			#SQL 実行部
			color_code_list, log_data, data = [], [], []
			sql_buf_list, color_buf_list, color_title_list = data_getter()
			for sql_buf, color_buf, color_title in zip(sql_buf_list, color_buf_list, color_title_list):
				sql_text = "SELECT {0}, {1}, student_id FROM {2}{3}".format(x_option, y_option, TARGET_TABLE, sql_buf)
				data_buf = dpd.protect_execute(sql_text, db_file_name=TARGET_DB_FILE_NAME)
				if data_buf is not None:
					log_data.append((sql_text, "#dddddd", len(data_buf), color_buf, color_title if dpd.len2b(color_title) < MAX_TITIE_LEN else text_split2b(color_title, 0, MAX_TITIE_LEN)))
					data.extend(data_buf)
					color_code_list.extend([color_buf for _ in range(sum([1 for d in data_buf if d[0] is not None and d[1] is not None]))])
				else:
					log_data.append((sql_text, "#ffaaaa", "取得失敗", None, color_title if dpd.len2b(color_title) < MAX_TITIE_LEN else text_split2b(color_title, 0, MAX_TITIE_LEN)))
			print("block_config= {0}".format(block_config)) #確認
			if data is not None:
				data = [(d[0], d[1], d[2], ccl) for d, ccl in zip(data, color_code_list) if d[0] is not None and d[1] is not None]
				data_set = []
				for d in data:
					data_set.append({"x":d[0], 
									 "y":d[1], 
									 "link_address":"/one_student/{0}".format(d[2]), 
									 "link_text":d[2],
									 "plot_color":d[3]
					})
				del data
				return render_template("./index.html", data_set=data_set, x_title=x_option_jn, y_title=y_option_jn,
									x_select_list=[(tl, "" if tl != x_option_jn else " selected") for tl in title_list_jn], load_flag=load_flag, 
									y_select_list=[(tl, "" if tl != y_option_jn else " selected") for tl in title_list_jn], ja_na_convert_dict=ja_na_convert_dict,
									r_select_list=[tlt for tlt in title_list_ty], return_input_dict=return_input_dict, 
									plot_size=plot_size, block_config=block_config, log_data=log_data, 
									first_code_list=list(range(FIRST_CODE_LIMIT)), second_code_list=list(range(SECOND_CODE_LIMIT))
				)
			else:
				print("data is None")
				return render_template("./index.html", data_set={}, x_title="", y_title="",
									x_select_list=[(tl, "") for tl in title_list_jn], load_flag=0, 
									y_select_list=[(tl, "") for tl in title_list_jn], ja_na_convert_dict=ja_na_convert_dict,
									r_select_list=[tlt for tlt in title_list_ty], return_input_dict=return_input_dict, 
									plot_size=1.0, block_config="none", log_data=[], 
									first_code_list=list(range(FIRST_CODE_LIMIT)), second_code_list=list(range(SECOND_CODE_LIMIT))
				)
		except ValueError as e: #エラー無視
			print("except ValueError as e")
			import traceback
			traceback.print_exc()
			return render_template("./index.html", data_set={}, x_title="", y_title="",
									x_select_list=[(tl, "") for tl in title_list_jn], load_flag=0, 
									y_select_list=[(tl, "") for tl in title_list_jn], ja_na_convert_dict=ja_na_convert_dict,
									r_select_list=[tlt for tlt in title_list_ty], return_input_dict=return_input_dict, 
									plot_size=1.0, block_config="none", log_data=[], 
									first_code_list=list(range(FIRST_CODE_LIMIT)), second_code_list=list(range(SECOND_CODE_LIMIT))
			)
	else:
		print("x_option_jn is None or y_option_jn is None")
		return render_template("./index.html", data_set={}, x_title="", y_title="",
									x_select_list=[(tl, "") for tl in title_list_jn], load_flag=0, 
									y_select_list=[(tl, "") for tl in title_list_jn], ja_na_convert_dict=ja_na_convert_dict,
									r_select_list=[tlt for tlt in title_list_ty], return_input_dict=return_input_dict, 
									plot_size=1.0, block_config="none", log_data=[], 
									first_code_list=list(range(FIRST_CODE_LIMIT)), second_code_list=list(range(SECOND_CODE_LIMIT))
		)

@app.route("/one_student/<id>", methods=["GET"])
def one_student(id):
	data = dpd.protect_execute("SELECT * FROM {0} WHERE student_id == {1}".format(ONE_STUDENT_TARGET_TABLE, id), dict_flag=True)
	return_list, ban_list = [], []
	data_dict = data[0]
	for k, v in data_dict.items():
		if v is not None:
			return_list.append([dpd.search_to_from(k, sorce="name", target="japanese_name", 
				pickup_table_and_db_list=[(ONE_STUDENT_TARGET_TABLE, TARGET_DB_FILE_NAME)]), v]
			)
		else:
			ban_list.append(dpd.search_to_from(k, sorce="name", target="japanese_name", pickup_table_and_db_list=[(ONE_STUDENT_TARGET_TABLE, TARGET_DB_FILE_NAME)]))
	return render_template("./one.html", student_id=id, data=return_list, ban_list=ban_list)

@app.route("/parameter", methods=["GET"])
def parameter():
	limit_number = 60
	data = dpd.parameter_check_core(limit_number, 1, 1, TARGET_TABLE, 1, title_list_target_key="japanese_name", db_file_name=dpd.SQL_FILE_NAME_MAIN,
								cacha_flag=True, non_print_flag=True
	)
	data = {dpd.search_to_from(k, sorce="name", target="japanese_name", tolerate_ambiguity_flag=True, pickup_table_and_db_list=[(TARGET_TABLE, dpd.SQL_FILE_NAME_MAIN)]):[vv if vv != "None" else "NULL" for vv in v] for k, v in data.items()}
	return render_template("./parameter.html", data=data, limit=limit_number, table_name=TARGET_TABLE)

def main():
	error_time = 0
	error_counter = 10
	error_counter_default = int(error_counter)
	while True:
		try:
			app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
		except:
			if time.time() - error_time < 10:
				if error_counter > 0:
					error_counter -= 1
					error_time = time.time()
				else:
					print("I think the exit.")
					return None
			else:
				error_counter = int(error_counter_default)
				error_time = time.time()

if __name__ == "__main__":
	main()