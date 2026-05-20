from flask import Flask,request,session,redirect,url_for
import sqlite3
import os
from datetime import datetime
import shutil
from werkzeug.utils import secure_filename
import re
from markupsafe import escape
#TABLE user(name TEXT PRIMARY KEY, pw TEXT,pic TEXT);
#login data will be setted in session, and the session will be used to check if user is logged in or not, and to get the user's name and pic

app = Flask(__name__)
app.secret_key = 'key'  # 改成安全的密鑰
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'user_avatar')
HISTORY_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'history')
ALLOWED_EXTENSIONS = {'png'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 最大檔案大小

# 確保上傳目錄存在
for folder in (UPLOAD_FOLDER, HISTORY_FOLDER):
    if not os.path.exists(folder):
        os.makedirs(folder)



# ------------------------------------------------------------------ #
#  XSS 偵測                                                           #
# ------------------------------------------------------------------ #
XSS_PATTERNS = re.compile(
    r'<script|onerror|onload|onclick|onmouseover|onfocus|'
    r'javascript:|<img|<svg|<iframe|<body|alert\(|prompt\(|confirm\(',
    re.IGNORECASE
)
 
def contains_xss(text: str) -> bool:
    print(f"Checking for XSS in: {text}")
    return bool(XSS_PATTERNS.search(text))

#if user is not logged in, redirect to login page
@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        #avatar pic is stored under ./static/user_avatar/username.png
        pic = f"/static/user_avatar/{username}.png"
        ret=f"""
        <html>
            <head>
                <title>Forum</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        margin: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                        text-align: center;
                        max-width: 500px;
                    }}
                    h1 {{
                        color: #333;
                        margin-bottom: 20px;
                    }}
                    img {{
                        border-radius: 50%;
                        width: 150px;
                        height: 150px;
                        object-fit: cover;
                        margin: 20px 0;
                        border: 5px solid #667eea;
                    }}
                    .button-group {{
                        margin-top: 30px;
                        display: flex;
                        gap: 10px;
                        justify-content: center;
                    }}
                    button, a.btn {{
                        padding: 10px 20px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 14px;
                        text-decoration: none;
                        display: inline-block;
                        transition: all 0.3s;
                    }}
                    .logout-btn {{
                        background-color: #e74c3c;
                        color: white;
                    }}
                    .logout-btn:hover {{
                        background-color: #c0392b;
                    }}
                    .upload-btn {{
                        background-color: #2ecc71;
                        color: white;
                    }}
                    .upload-btn:hover {{
                        background-color: #27ae60;
                    }}
                    .upload-form {{
                        margin-top: 30px;
                        padding-top: 30px;
                        border-top: 2px solid #ecf0f1;
                    }}
                    .file-input-wrapper {{
                        position: relative;
                        display: inline-block;
                    }}
                    input[type="file"] {{
                        display: none;
                    }}
                    .file-label {{
                        background-color: #3498db;
                        color: white;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        transition: all 0.3s;
                    }}
                    .file-label:hover {{
                        background-color: #2980b9;
                    }}
                    .upload-submit {{
                        background-color: #2ecc71;
                        color: white;
                        margin-top: 10px;
                    }}
                    .upload-submit:hover {{
                        background-color: #27ae60;
                    }}
                    .file-name {{
                        margin-top: 10px;
                        color: #666;
                        font-size: 12px;
                    }}
                </style>
                <script>
                    function updateFileName(input) {{
                        var fileName = document.getElementById('file-name-display');
                        if (input.files && input.files[0]) {{
                            fileName.textContent = '選中: ' + input.files[0].name;
                        }}
                    }}
                </script>
            </head>
            <body>
                <div class="container">
                    <h1>歡迎, {username}!</h1>
                    <img src='{pic}' alt='{username} avatar' onerror="this.src='/static/user_avatar/default.png'">
                    <p>你已成功登入論壇</p>
                    
                    <div class="upload-form">
                        <h3>更新你的頭像</h3>
                        <form method="post" action="/upload" enctype="multipart/form-data">
                            <div class="file-input-wrapper">
                                <label for="avatar" class="file-label">選擇圖片</label>
                                <input type="file" id="avatar" name="avatar" accept=".png" required onchange="updateFileName(this)">
                                <div class="file-name" id="file-name-display"></div>
                            </div>
                            <button type="submit" class="upload-submit">上傳頭像</button>
                        </form>
                    </div>

                    <div class="button-group" style="margin-top: 30px; padding-top: 30px; border-top: 2px solid #ecf0f1;">
                        <form method="POST" action="/search_user" style="display: inline;">
                            <input type="text" name="name" placeholder="使用者名稱" required>
                            <button class="search-btn" type="submit">🔍 搜尋使用者</button>
                        </form>
                        <form method="GET" action="/logout" style="display: inline;">
                            <button class="logout-btn" type="submit">登出</button>
                        </form>
                    </div>
                </div>
            </body>
        </html>
        """
        if contains_xss(username):
            ret += "<script>alert('CCCTF{人類有三大慾望：食慾、性慾、睡眠欲，而在這三大慾望之中，因為食慾是滿足人類生存需求的慾望，所以，滿足食慾的行為，在這三者之中，優先是第一位的，如果能在進食的過程中，吃下了美味的食物，也能使人類無比愉快，而在現實生活中，存在著這種對快感執著追求的人，我們通常把這種人稱之為美食家，而本餐廳則專門為那些厭倦世間常見美食的人，量體裁衣，提供符合他們身份的美食。}')</script>"
        if username=="𰻞𰻞龘齉𱁬𪚥𠔻䨻䲜朤":
            ret+="<script>alert('CCCTF{嚴厲斥責你發瘋啦這什麼東西啦不可以啊不要再亂搞了啦不要再蝦幾把搞了啦你幹嘛這樣啊怎麼這麼激烈啊不可以這樣子啊發瘋了是不是啊啥小啦不要不可以不可以講什麼話啊操擊敗勒啦冷靜一點啦幹這到底又是什麼東西不可以啦這是能講的話嗎絕對不可以的啊}')</script>"
        return ret
        

    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        pw = request.form['pw']
        pw2 = request.form['pw2']
        
        # 檢查密碼是否相符
        if pw != pw2:
            return '''<html><body style="font-family: Arial; text-align: center; padding-top: 50px;">
                <h2>密碼不相符</h2>
                <a href="/login">返回登入</a>
            </body></html>'''
        
        # 檢查帳號是否已存在
        conn = sqlite3.connect("forum.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE name=?", (name,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return '''<html><body style="font-family: Arial; text-align: center; padding-top: 50px;">
                <h2>該用戶名已被使用</h2>
                <a href="/login">返回登入</a>
            </body></html>'''
        
        # 新增帳號
        cursor.execute("INSERT INTO user (name, pw, pic) VALUES (?, ?, ?)", (name, pw, ''))
        conn.commit()
        conn.close()
        
        return '''<html><body style="font-family: Arial; text-align: center; padding-top: 50px;">
            <h2>帳號建立成功！</h2>
            <p>請返回登入</p>
            <a href="/login">返回登入</a>
        </body></html>'''
    
    # GET 請求，返回登入頁面
    return redirect(url_for('login'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        pw = request.form['pw']
        conn = sqlite3.connect("forum.db")  # 在函數內創建連接
        cursor = conn.cursor()
        script=f"SELECT * FROM user WHERE name='{name}' AND pw='{pw}'"
        print("script: " + script)
        cursor.execute(script)
        user = cursor.fetchone()
        conn.close()  # 用完後關閉
        if user:
            session['username'] = name  # 將用戶名稱存在session
            session['flag'] = "CCCTF{太大聲太小聲去跟舍監反應🗣️🗣️會改進 不想聽可以包一包滾回🫦…滾出宿舍🔥🔥🔥👺👺👺 不是像沒爸沒媽🤏🤏🤏對老子的歌指指點點🖕🖕 老子播什麼你聽什麼🗣️🗣️🤡🤡👊👊👊👊 另外！靠杯一中版的 🗣️🗣️🗣️（哦哦哦哦哦哦哦） 🗣️🗣️🗣️🗣️🗣️靠杯一中版🗣️🗣️🗣️ （哦哦哦哦哦） 🗣️🗣️🗣️🗣️🗣️的🗣️🗣️🗣️（哦哦哦哦哦哦） 🗣️🗣️🗣️🗣️🗣️近期對於公開平台🗣️🗣️🗣️（哦哦哦哦哦哦）🗣️🗣️🗣️🗣️🗣️（沃草）🗣️🗣️🗣️🗣️🗣️（哦哦哦哦哦哦）（119）🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️}"  # 這裡放置flag
            #redirect to index page
            return redirect(url_for('index'))
        else:
            return "Login failed"
    else:
        return '''
        <!DOCTYPE html>
        <html>
            <head>
                <title>登入 / 註冊 - Forum</title>
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                    .container {
                        background: white;
                        border-radius: 10px;
                        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
                        width: 100%;
                        max-width: 450px;
                        overflow: hidden;
                    }
                    .tabs {
                        display: flex;
                        background: #f8f8f8;
                        border-bottom: 2px solid #e0e0e0;
                    }
                    .tab {
                        flex: 1;
                        padding: 15px;
                        text-align: center;
                        cursor: pointer;
                        background: #f8f8f8;
                        border: none;
                        font-size: 16px;
                        font-weight: 600;
                        color: #999;
                        transition: all 0.3s;
                    }
                    .tab.active {
                        background: white;
                        color: #667eea;
                        border-bottom: 3px solid #667eea;
                        margin-bottom: -2px;
                    }
                    .tab:hover {
                        color: #667eea;
                    }
                    .form-content {
                        padding: 50px;
                        display: none;
                    }
                    .form-content.active {
                        display: block;
                    }
                    h2 {
                        text-align: center;
                        color: #333;
                        margin-bottom: 30px;
                        font-size: 24px;
                    }
                    .form-group {
                        margin-bottom: 20px;
                    }
                    label {
                        display: block;
                        margin-bottom: 8px;
                        color: #555;
                        font-weight: 500;
                    }
                    input[type="text"],
                    input[type="password"],
                    input[type="email"] {
                        width: 100%;
                        padding: 12px;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        font-size: 14px;
                        transition: border-color 0.3s;
                    }
                    input[type="text"]:focus,
                    input[type="password"]:focus,
                    input[type="email"]:focus {
                        outline: none;
                        border-color: #667eea;
                        box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
                    }
                    .submit-btn {
                        width: 100%;
                        padding: 12px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: transform 0.2s, box-shadow 0.2s;
                    }
                    .submit-btn:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
                    }
                    .submit-btn:active {
                        transform: translateY(0);
                    }
                    .info-text {
                        text-align: center;
                        color: #999;
                        font-size: 14px;
                        margin-top: 15px;
                    }
                </style>
                <script>
                    function switchTab(tabName) {
                        var tabs = document.querySelectorAll('.tab');
                        var contents = document.querySelectorAll('.form-content');
                        tabs.forEach(function(tab) {
                            tab.classList.remove('active');
                        });
                        contents.forEach(function(content) {
                            content.classList.remove('active');
                        });
                        event.target.classList.add('active');
                        document.getElementById(tabName).classList.add('active');
                    }
                </script>
            </head>
            <body>
                <div class="container">
                    <div class="tabs">
                        <button class="tab active" onclick="switchTab('login-form')">登入</button>
                        <button class="tab" onclick="switchTab('register-form')">註冊</button>
                    </div>
                    
                    <div id="login-form" class="form-content active">
                        <h2>論壇登入</h2>
                        <form method="post" action="/login">
                            <div class="form-group">
                                <label for="login-name">用戶名稱</label>
                                <input type="text" id="login-name" name="name" required>
                            </div>
                            <div class="form-group">
                                <label for="login-pw">密碼</label>
                                <input type="password" id="login-pw" name="pw" required>
                            </div>
                            <button class="submit-btn" type="submit">登入</button>
                        </form>
                    </div>
                    
                    <div id="register-form" class="form-content">
                        <h2>建立新帳號</h2>
                        <form method="post" action="/register">
                            <div class="form-group">
                                <label for="reg-name">用戶名稱</label>
                                <input type="text" id="reg-name" name="name" required>
                            </div>
                            <div class="form-group">
                                <label for="reg-pw">密碼</label>
                                <input type="password" id="reg-pw" name="pw" required>
                            </div>
                            <div class="form-group">
                                <label for="reg-pw2">確認密碼</label>
                                <input type="password" id="reg-pw2" name="pw2" required>
                            </div>
                            <button class="submit-btn" type="submit">建立帳號</button>
                        </form>
                    </div>
                </div>
            </body>
        </html>
        '''
    

@app.route('/user/<username>')#find out other's user info, but only if you are logged in
def user_info(username):
    if 'username' in session:
        conn = sqlite3.connect("forum.db")  # 在函數內創建連接
        cursor = conn.cursor()
        # ⚠️ 故意的 SQL Injection 漏洞：使用字符串拼接而不是參數化查詢
        query = f"SELECT * FROM user WHERE name='{username}'"
        try:
            cursor.execute(query)
            user = cursor.fetchone() # 改為只取一個結果
            conn.close()
            
            if user:
                # 美化輸出：只顯示該使用者的資訊
                html = f"""
                <html>
                    <head>
                        <title>用戶信息 - {escape(user[0])}</title>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                min-height: 100vh;
                                margin: 0;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                padding: 20px;
                            }}
                            .container {{
                                background: white;
                                padding: 40px;
                                border-radius: 10px;
                                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                                max-width: 400px;
                                width: 100%;
                                text-align: center;
                            }}
                            h1 {{
                                color: #333;
                                margin-bottom: 20px;
                            }}
                            .user-avatar {{
                                border-radius: 50%;
                                width: 150px;
                                height: 150px;
                                object-fit: cover;
                                margin: 20px 0;
                                border: 5px solid #667eea;
                            }}
                            .info-box {{
                                background: #f8f9fa;
                                padding: 20px;
                                border-radius: 8px;
                                text-align: left;
                                margin-bottom: 20px;
                            }}
                            .label {{
                                font-weight: 600;
                                color: #667eea;
                            }}
                            .back-btn {{
                                display: inline-block;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white;
                                padding: 10px 20px;
                                border-radius: 5px;
                                text-decoration: none;
                                transition: all 0.3s;
                                width: 100%;
                                box-sizing: border-box;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>👤 用戶資料</h1>
                            <img src='/static/user_avatar/{escape(user[0])}.png' class="user-avatar" onerror="this.src='/static/user_avatar/default.png'">
                            <div class="info-box">
                                <p><span class="label">用戶名稱：</span> {escape(user[0])}</p>
                                <p><span class="label">自定義圖片路徑：</span> {escape(user[2])}</p>
                            </div>
                            <a href="/" class="back-btn">返回首頁</a>
                        </div>
                    </body>
                </html>
                """
                return html
            else:
                return """
                <html>
                    <head>
                        <title>用戶未找到</title>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                min-height: 100vh;
                                margin: 0;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                            }
                            .container {
                                background: white;
                                padding: 40px;
                                border-radius: 10px;
                                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                                text-align: center;
                                max-width: 400px;
                            }
                            h1 { color: #e74c3c; }
                            .back-btn {
                                display: inline-block;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white;
                                padding: 10px 20px;
                                border-radius: 5px;
                                text-decoration: none;
                                margin-top: 20px;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>❌ 用戶未找到</h1>
                            <p>資料庫中沒有此用戶。</p>
                            <a href="/" class="back-btn">返回首頁</a>
                        </div>
                    </body>
                </html>
                """
        except sqlite3.Error as e:
            conn.close()
            # 顯示 SQL 錯誤（便於調試）
            return f"""
            <html>
                <head>
                    <title>資料庫錯誤</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            min-height: 100vh;
                            margin: 0;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                        }}
                        .container {{
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                            max-width: 600px;
                        }}
                        h1 {{ color: #e74c3c; }}
                        .error-box {{
                            background: #ffebee;
                            border-left: 4px solid #e74c3c;
                            padding: 15px;
                            border-radius: 4px;
                            margin: 20px 0;
                        }}
                        .error-box p {{
                            margin: 8px 0;
                            color: #d32f2f;
                            font-family: monospace;
                            word-break: break-all;
                        }}
                        .back-btn {{
                            display: inline-block;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 10px 20px;
                            border-radius: 5px;
                            text-decoration: none;
                            margin-top: 20px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>⚠️ 資料庫錯誤</h1>
                        <div class="error-box">
                            <p><strong>錯誤：</strong>{escape(str(e))}</p>
                            <p><strong>查詢：</strong>{escape(query)}</p>
                        </div>
                        <a href="/" class="back-btn">返回首頁</a>
                    </div>
                </body>
            </html>
            """
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)  # 移除用戶名稱
    session.pop('flag', None)  # 移除flag
    return redirect(url_for('login'))


@app.route('/upload', methods=['POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    # 檢查是否有檔案上傳
    if 'avatar' not in request.files:
        return '''<html><body style="font-family: Arial; text-align: center; padding-top: 50px;">
            <h2>沒有選擇檔案</h2>
            <a href="/">返回首頁</a>
        </body></html>'''
    
    file = request.files['avatar']
    
    if file.filename == '':
        return '''<html><body style="font-family: Arial; text-align: center; padding-top: 50px;">
            <h2>沒有選擇檔案</h2>
            <a href="/">返回首頁</a>
        </body></html>'''
    
    # 檢查檔案類型
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
        return '''<html><body style="font-family: Arial; text-align: center; padding-top: 50px;">
            <h2>檔案類型不支持，只能上傳 PNG</h2>
            <a href="/">返回首頁</a>
        </body></html>'''
    
    try:
        # 1) 主頭像路徑：/static/user_avatar/username.png
        avatar_filename = secure_filename(f"{username}.png")
        avatar_path = os.path.join(UPLOAD_FOLDER, avatar_filename)
        file.save(avatar_path)

        # 2) 歷史路徑：/static/history/username_date_time.png
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_filename = secure_filename(f"{username}_{timestamp}.png")
        history_path = os.path.join(HISTORY_FOLDER, history_filename)
        shutil.copy2(avatar_path, history_path)
        
        return '''<html><body style="font-family: Arial; text-align: center; padding-top: 50px;">
            <h2>頭像上傳成功！</h2>
            <a href="/">返回首頁</a>
        </body></html>'''
    except Exception as e:
        return f'''<html><body style="font-family: Arial; text-align: center; padding-top: 50px;">
            <h2>上傳失敗</h2>
            <p>{str(e)}</p>
            <a href="/">返回首頁</a>
        </body></html>'''


@app.route('/search_user', methods=['POST'])
def search_user():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        conn = sqlite3.connect("forum.db")  # 在函數內創建連接
        cursor = conn.cursor()
        if request.form.get('name'):
            query = f"SELECT * FROM user WHERE name LIKE '%{request.form.get('name')}%'"
            print("script: " + query)
            try:
                cursor.execute(query)
                users = cursor.fetchall()
                conn.close()
                
                if users:
                    html = '''
                    <html>
                        <head>
                            <title>搜尋結果</title>
                            <style>
                                body {
                                    font-family: Arial, sans-serif;
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    min-height: 100vh;
                                    margin: 0;
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                }
                                .container {
                                    background: white;
                                    padding: 40px;
                                    border-radius: 10px;
                                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                                    max-width: 600px;
                                }
                                h1 { color: #333; }
                                .user-list { list-style-type: none; padding: 0; }
                                .user-list li { margin-bottom: 10px; }
                                .back-btn {
                                    display: inline-block;
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    color: white;
                                    padding: 10px 20px;
                                    border-radius: 5px;
                                    text-decoration: none;
                                    margin-top: 20px;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h1>搜尋結果</h1>
                                <ul class="user-list">

                    '''
                    for user in users:
                        html += f"<li><a href='/user/{escape(user[0])}'>{escape(user[0])}</a></li>"
                    html += '''
                                </ul>
                                <a href="/" class="back-btn">返回首頁</a>
                            </div>
                        </body>
                    </html>
                    '''
                    return html
                else:
                    return '''<html><body style="font-family: Arial; text-align: center; padding-top: 50px;">
                        <h2>沒有找到符合條件的用戶</h2>
                        <a href="/">返回首頁</a>'''
            except sqlite3.Error as e:
                conn.close()
                return f'''<html><body style="font-family: Arial; text-align: center; padding-top: 50px;">
                    <h2>資料庫錯誤</h2>
                    <p>{escape(str(e))}</p>'''
        else:
            return '''<html><body style="font-family: Arial; text-align: center; padding-top: 50px;">
                <h2>請輸入搜尋條件</h2>
                <a href="/">返回首頁</a>'''


