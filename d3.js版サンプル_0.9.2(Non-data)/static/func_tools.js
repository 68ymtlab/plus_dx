function first_select_change(target_num) {
    let inputer_value = document.getElementById("first_select_set_" + target_num).value;
    //console.log("inputer_value [ first_select_change ] = " + inputer_value);
    if (inputer_value == "nonal_select") {
        document.getElementById("nomal_control_" + target_num).style.display ="block";
        document.getElementById("sql_control_" + target_num).style.display ="none";
        document.getElementById("color_control_" + target_num).style.display ="block";
    } else if (inputer_value == "sql_select") {
        document.getElementById("nomal_control_" + target_num).style.display ="none";
        document.getElementById("sql_control_" + target_num).style.display ="block";
        document.getElementById("color_control_" + target_num).style.display ="block";
    } else if (inputer_value == "non_select") {
        document.getElementById("nomal_control_" + target_num).style.display ="none";
        document.getElementById("sql_control_" + target_num).style.display ="none";
        document.getElementById("color_control_" + target_num).style.display ="none";
    }
}

function second_select_change(target_num, sub_target_num) {
    let inputer_value_buf = text_upper(document.getElementById("second_select_set_" + target_num + "_" + sub_target_num).value);
    let inputer_value = inputer_value_buf.split(",", 1)[0];
    //console.log("inputer_value [ second_select_change ] = " + inputer_value);
    if (inputer_value == "INTEGER" || inputer_value == "REAL") {
        document.getElementById("nomal_control_" + target_num + "_" + sub_target_num + "_number_div").style.display ="inline";
        document.getElementById("nomal_control_" + target_num + "_" + sub_target_num + "_text_div").style.display ="none";
    } else if (inputer_value == "TEXT") {
        document.getElementById("nomal_control_" + target_num + "_" + sub_target_num + "_number_div").style.display ="none";
        document.getElementById("nomal_control_" + target_num + "_" + sub_target_num + "_text_div").style.display ="inline";
    } else {
        document.getElementById("nomal_control_" + target_num + "_" + sub_target_num + "_number_div").style.display ="none";
        document.getElementById("nomal_control_" + target_num + "_" + sub_target_num + "_text_div").style.display ="none";
    }
}

function text_upper(s) { //大文字化
    return s.replace(/[a-z]/g, function(ch) {return String.fromCharCode(ch.charCodeAt(0) & ~32);});
}

function priority_select_change(target_num, sub_target_num) {
	let inputer_value = document.getElementById("priority_" + target_num + "_" + sub_target_num + "_select").value;
	let flag = true;
	let set_color = "#ffffff";
	switch (inputer_value) {
		case "max":
			set_color = "#ffbbbb";
			break;
		case "high":
			set_color = "#ddbbbb";
			break;
		case "default":
			set_color = "#bbbbbb";
			break;
		case "low":
			set_color = "#bbbbdd";
			break;
		case "min":
			set_color = "#bbbbff";
			break;
		default:
			flag = false;
	}
	if (flag) {
		document.getElementById("nomal_control_" + target_num + "_" + sub_target_num + "_connecter").style.backgroundColor = set_color;
		document.getElementById("nomal_control_" + target_num + "_" + sub_target_num).style.backgroundColor = set_color;
	}
}

function null_ban_input_number(target_num, sub_target_num, format_text) {
	let inputer_value = document.getElementById("nomal_control_" + target_num + "_" + sub_target_num + "_" + format_text + "_mode").value;
	switch (inputer_value) {
		case "x_is_null":
			document.getElementById("nomal_control_" + target_num + "_" + sub_target_num + "_" + format_text).style.visibility = "hidden";
			break;
		case "x_is_not_null":
			document.getElementById("nomal_control_" + target_num + "_" + sub_target_num + "_" + format_text).style.visibility = "hidden";
			break;
		default:
			document.getElementById("nomal_control_" + target_num + "_" + sub_target_num + "_" + format_text).style.visibility = "visible";
	}
}

function connecter_select_change(target_num, sub_target_num, sub_target_num_max) {
	console.log("nomal_control_" + target_num + "_" + sub_target_num + "_connecter_select");
	let inputer_value = document.getElementById("nomal_control_" + target_num + "_" + sub_target_num + "_connecter_select").value;
	let return_flag = true;
	if (inputer_value == "end") {
		//console.log("ALL : " + target_num + "_(" + sub_target_num+1 + ", " + sub_target_num_max + ")=" + inputer_value);
		for(let di=sub_target_num_max; di>sub_target_num; di--) {
			//console.log(target_num + "_" + di + "=" + inputer_value);
			document.getElementById("nomal_control_" + target_num + "_" + di).style.display ="none";
			if (di < sub_target_num_max) {
				//console.log('document.getElementById("nomal_control_' + target_num + '_' + di + '_connecter").style.display ="none"');
				document.getElementById("nomal_control_" + target_num + "_" + di + "_connecter").style.display ="none";
				document.getElementById("nomal_control_" + target_num + "_" + di + "_connecter_select").selectedIndex = 0; //元に戻す
			}
		}
	} else if (inputer_value == "and" || inputer_value == "or") {
		let di = sub_target_num + 1;
		//console.log(target_num + "_" + di + "=" + inputer_value);
		document.getElementById("nomal_control_" + target_num + "_" + di).style.display ="block";
		if (di < sub_target_num_max) {
			//console.log('document.getElementById("nomal_control_' + target_num + '_' + di + '_connecter").style.display ="block"');
			document.getElementById("nomal_control_" + target_num + "_" + di + "_connecter").style.display ="block";
		}
		return_flag = false;
	}
	return return_flag;
}

//以下、ダウンロード系
const download_button = document.getElementById("download_button");
download_button.addEventListener("click", download_clicked);

function download_clicked(event) {
    event.preventDefault();
    let svg_buf = document.querySelector("svg");
    let svg_text = new XMLSerializer().serializeToString(svg_buf);
    let blob = new Blob(['<?xml version="1.0" encoding="UTF-8"?>' + svg_text], {type: 'text/plain'});
    let url = URL.createObjectURL(blob);
    let a = document.createElement("a");
    document.body.appendChild(a);
    a.download = 'Download.svg';
    a.href = url;
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
}

function format_xy(){
	let buf_x = document.getElementById("x_select_option");
	let buf_y = document.getElementById("y_select_option");
	if (buf_x != null && buf_y != null) {
		target_element_list = document.getElementsByClassName("sql_format_xy_output")
		for(let o=0; o<target_element_list.length; o++){
			target_element_list[o].innerHTML = "SELECT " + ja_na_convert_dict[buf_x.value] + ", " + ja_na_convert_dict[buf_y.value] + ", student_id FROM student_core "; //不格好ではあるあ、維持
		}
	}
}

function tooltip_changer() { //注釈の表示・非表示
	let tooltip_element = document.querySelector("tooltip");
	if(document.getElementById("checkbox_for_tooltip").checked) {
		tooltip.style("display", "inline-block");
	} else {
		tooltip.style("display", "none");
	}
}

//セーブ及びロード系
const config_save_button = document.getElementById("config_save");
config_save_button.addEventListener("click", config_saver);

const config_load_button = document.getElementById("config_load");
config_load_button.addEventListener("click", config_loader);

const dummy_input_file = document.getElementById("dummy_input_file");
dummy_input_file.addEventListener("change", change_input_file);

const reader = new FileReader();
reader.onload = function(event) {
	let read_data = reader.result;
	//console.log(read_data); //調査
	config_data = JSON.parse(read_data);
	config_data["flag_for_download"] = "0"; //除外
	onload_setting();
	const submit_button = document.getElementById("submit_button");
	submit_button.click();
}

var load_flag = document.getElementById("flag_for_download");

function config_saver() {
	load_flag.value = 1;
	const submit_button = document.getElementById("submit_button");
	submit_button.click();
	console.log("LoadFlag: " + load_flag.value ); ////////////////////////////////
}

function config_saver_after_load() {
	console.log("reLoadForDownload")
	const dummy_link = document.getElementById("dummy_link");
	dummy_link.href = URL.createObjectURL(new Blob([JSON.stringify(config_data)], {type: 'text/plain'}));
	dummy_link.download = "plot_config_" + datetime_getter() + ".json";
	dummy_link.click();
}

function config_loader() {
	$("#dummy_input_file").on('click', function(event){
  		event.stopPropagation();
  	});
  	$("#dummy_input_file").click();
}

function change_input_file() { //変わったら実行
	reader.readAsText(dummy_input_file.files[0]);
}

function datetime_getter() {
	let dd = new Date();
	let YYYY = dd.getFullYear();
	let MM = dd.getMonth();
	if (MM < 10) {
		MM = "0" + MM;
	}
	let DD = dd.getDate();
	if (DD < 10) {
		DD = "0" + DD;
	}
	let hh = dd.getHours();
	if (hh < 10) {
		hh = "0" + hh;
	}
	let mm = dd.getMinutes();
	if (mm < 10) {
		mm = "0" + mm;
	}
	let ss = dd.getSeconds();
	if (ss < 10) {
		ss = "0" + ss;
	}
	let pelem021 = document.getElementById("date021");
	return YYYY + "-" + MM + "-" + DD + "_" + hh + "-" + mm + "-" + ss;
}

function return_setter() {
	let object_data;
	for (let dict_key in config_data) {
		object_data = document.getElementsByName(dict_key);
		if (typeof object_data != "undefined") {
			try {
				$('[name=' + dict_key + ']').val(config_data[dict_key]);
			} catch (error) {
				console.warn(error);
				console.dir(object_data);
			}
		}
	}
}

function display_div(my_id, target_id, mode="auto") {
	my_id = document.getElementById(my_id);
	target_id = document.getElementById(target_id);
	if ((mode == "auto" && target_id.style.display == "none") || mode == "open") {
		target_id.style.display = "block";
		my_id.style.backgroundColor = "#e9f9e9";
	} else if (mode == "auto" || mode == "close") {
		target_id.style.display = "none";
		my_id.style.backgroundColor = "#e9e9e9";
	}
}
