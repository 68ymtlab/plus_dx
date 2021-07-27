import sys, os
ADD_MODULES_ADDRESS = "..\\" #相対ディレクトリ指定
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ADD_MODULES_ADDRESS))) #相対パスを絶対パスに変換
try:
	del sys.modules[str(__name__)] #importされたこのファイルを消す 
except Exception:
	pass
from db_plus_dx import * #再import
