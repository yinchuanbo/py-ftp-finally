import os
import sys
import json
import flask
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import importlib.util
from pathlib import Path
import datetime  # 添加导入 datetime 模块

# 导入 ftp_manager 中的函数
from ftp_manager import get_files, upload_files, LANGUAGES

app = Flask(__name__)
app.secret_key = 'ftpwebinterfacesecretkey'  # 用于 flash 消息和 session

# 首页路由
@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES, now=datetime.datetime.now())

# 获取文件列表路由
@app.route('/get_files', methods=['POST'])
def get_files_route():
    env = request.form.get('environment')
    language_selection = request.form.getlist('languages[]')
    
    # 设置环境变量
    os.environ['NODE_ENV'] = env
    
    # 更新环境文件
    env_file = f'.env.{env}'
    with open(env_file, 'w') as f:
        f.write(f"onlyLan={','.join(language_selection)}\n")
        f.write("isFilter=true\n")
        
        # 处理提交ID
        for lang in language_selection:
            commit_ids = request.form.get(f'{lang}_commit', '')
            if commit_ids:
                f.write(f"{lang}commit={commit_ids}\n")
    
    # 获取文件列表
    result = get_files()
    
    # 如果输出文件存在，读取输出
    output_data = None
    if os.path.exists('output.py'):
        try:
            from output import OUTPUT
            output_data = OUTPUT
        except ImportError:
            output_data = None
    
    return render_template('files.html', 
                          result=result, 
                          output=output_data, 
                          environment=env,
                          languages=language_selection,
                          now=datetime.datetime.now())

# 上传文件路由
@app.route('/upload_files', methods=['POST'])
def upload_files_route():
    env = request.form.get('environment')
    
    # 设置环境变量
    os.environ['NODE_ENV'] = env
    
    try:
        # 导入输出文件
        from output import OUTPUT
        
        # 执行上传
        upload_files(OUTPUT)
        
        flash('文件上传完成！', 'success')
    except ImportError:
        flash('未找到文件列表，请先获取文件列表', 'error')
    except Exception as e:
        flash(f'上传过程中发生错误: {str(e)}', 'error')
    
    return redirect(url_for('index'))

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', now=datetime.datetime.now()), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', now=datetime.datetime.now()), 500

if __name__ == '__main__':
    # 确保模板目录存在
    Path('templates').mkdir(exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000) 