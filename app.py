import streamlit as st
import pandas as pd
import numpy as np
import time
import hashlib
import random
from datetime import datetime

# 初始化Session State
def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    if 'transactions' not in st.session_state:
        st.session_state.transactions = []
    if 'marketplace' not in st.session_state:
        st.session_state.marketplace = []
    if 'users' not in st.session_state:
        st.session_state.users = []
    
    # 初始化一些示例数据
    if not st.session_state.documents:
        st.session_state.documents = [
            {
                "id": 1,
                "title": "电动叉车电池维护指南",
                "author": "张工",
                "content": "电动叉车电池维护是确保设备长期稳定运行的关键...",
                "required_score": 150,
                "status": "approved",
                "reward_score": 50,
                "read_count": 245,
                "created_at": "2023-08-01"
            },
            {
                "id": 2,
                "title": "液压系统故障排查手册",
                "author": "李工",
                "content": "叉车液压系统常见问题包括油压不足、漏油和噪音过大...",
                "required_score": 200,
                "status": "approved",
                "reward_score": 80,
                "read_count": 178,
                "created_at": "2023-08-10"
            },
            {
                "id": 3,
                "title": "内燃叉车发动机保养技巧",
                "author": "王工",
                "content": "内燃叉车的发动机需要定期保养以确保其最佳性能...",
                "required_score": 120,
                "status": "pending",
                "reward_score": None,
                "read_count": 0,
                "created_at": "2023-09-05"
            }
        ]
    
    if not st.session_state.marketplace:
        st.session_state.marketplace = [
            {
                "id": 1,
                "title": "叉车轮胎（全新）",
                "type": "配件",
                "description": "适用于林德叉车，规格：28×9-15",
                "required_score": 300,
                "user": "张工",
                "status": "active"
            },
            {
                "id": 2,
                "title": "叉车液压油更换服务",
                "type": "服务",
                "description": "提供专业叉车液压油更换服务，上门服务",
                "required_score": 250,
                "user": "李工",
                "status": "active"
            },
            {
                "id": 3,
                "title": "叉车电池充电器",
                "type": "配件",
                "description": "48V 智能充电器，适用于电动叉车",
                "required_score": 400,
                "user": "王工",
                "status": "active"
            }
        ]
    
    if not st.session_state.users:
        st.session_state.users = [
            {
                "phone": "13800138000",
                "password": "123456",
                "name": "张工",
                "score": 350,
                "hash": hashlib.sha256("13800138000".encode()).hexdigest(),
                "reg_date": "2023-07-15"
            },
            {
                "phone": "13900139000",
                "password": "123456",
                "name": "李工",
                "score": 280,
                "hash": hashlib.sha256("13900139000".encode()).hexdigest(),
                "reg_date": "2023-07-20"
            },
            {
                "phone": "13700137000",
                "password": "123456",
                "name": "王工",
                "score": 150,
                "hash": hashlib.sha256("13700137000".encode()).hexdigest(),
                "reg_date": "2023-08-01"
            }
        ]

# 生成哈希值
def generate_hash(phone):
    return hashlib.sha256(phone.encode()).hexdigest()

# 用户注册
def register_user(phone, password, name):
    # 检查手机号是否已注册
    for user in st.session_state.users:
        if user["phone"] == phone:
            return False, "该手机号已注册"
    
    # 创建新用户
    new_user = {
        "phone": phone,
        "password": password,
        "name": name,
        "score": 100,  # 注册赠送100分
        "hash": generate_hash(phone),
        "reg_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    st.session_state.users.append(new_user)
    
    # 记录积分交易
    st.session_state.transactions.append({
        "user": phone,
        "amount": 100,
        "type": "注册奖励",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    
    return True, "注册成功！获得100积分"

# 用户登录
def login_user(phone, password):
    for user in st.session_state.users:
        if user["phone"] == phone and user["password"] == password:
            st.session_state.user = user
            return True, "登录成功"
    return False, "手机号或密码错误"

# 提交技术文档
def submit_document(title, content, required_score):
    if st.session_state.user is None:
        return False, "请先登录"
    
    new_doc = {
        "id": len(st.session_state.documents) + 1,
        "title": title,
        "author": st.session_state.user["name"],
        "content": content,
        "required_score": required_score,
        "status": "pending",
        "reward_score": None,
        "read_count": 0,
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    
    st.session_state.documents.append(new_doc)
    return True, "文档提交成功，等待审核"

# 阅读文档
def read_document(doc_id):
    if st.session_state.user is None:
        return False, "请先登录"
    
    # 查找文档
    doc = next((d for d in st.session_state.documents if d["id"] == doc_id), None)
    if not doc:
        return False, "文档不存在"
    
    # 检查文档状态
    if doc["status"] != "approved":
        return False, "文档尚未审核通过"
    
    # 检查用户积分
    if st.session_state.user["score"] < doc["required_score"]:
        return False, "积分不足"
    
    # 扣除用户积分
    for user in st.session_state.users:
        if user["phone"] == st.session_state.user["phone"]:
            user["score"] -= doc["required_score"]
            break
    
    # 增加作者积分
    for user in st.session_state.users:
        if user["name"] == doc["author"]:
            user["score"] += doc["required_score"]
            break
    
    # 增加阅读计数
    for doc_item in st.session_state.documents:
        if doc_item["id"] == doc_id:
            doc_item["read_count"] += 1
            
            # 每100次阅读奖励作者
            if doc_item["read_count"] % 100 == 0:
                reward = min(100, max(10, doc_item["read_count"] // 10))
                for u in st.session_state.users:
                    if u["name"] == doc_item["author"]:
                        u["score"] += reward
                        st.session_state.transactions.append({
                            "user": u["phone"],
                            "amount": reward,
                            "type": "阅读奖励",
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        break
    
    # 记录交易
    st.session_state.transactions.append({
        "user": st.session_state.user["phone"],
        "amount": -doc["required_score"],
        "type": "阅读文档",
        "description": doc["title"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    
    st.session_state.transactions.append({
        "user": next(u["phone"] for u in st.session_state.users if u["name"] == doc["author"]),
        "amount": doc["required_score"],
        "type": "文档收益",
        "description": doc["title"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    
    return True, doc

# 添加市场项目
def add_market_item(title, item_type, description, required_score, platform_fee):
    if st.session_state.user is None:
        return False, "请先登录"
    
    new_item = {
        "id": len(st.session_state.marketplace) + 1,
        "title": title,
        "type": item_type,
        "description": description,
        "required_score": required_score,
        "user": st.session_state.user["name"],
        "status": "active",
        "platform_fee": platform_fee
    }
    
    st.session_state.marketplace.append(new_item)
    return True, "需求发布成功"

# 兑换市场项目
def redeem_market_item(item_id):
    if st.session_state.user is None:
        return False, "请先登录"
    
    # 查找项目
    item = next((i for i in st.session_state.marketplace if i["id"] == item_id), None)
    if not item:
        return False, "项目不存在"
    
    # 检查用户积分
    if st.session_state.user["score"] < item["required_score"]:
        return False, "积分不足"
    
    # 扣除用户积分
    for user in st.session_state.users:
        if user["phone"] == st.session_state.user["phone"]:
            user["score"] -= item["required_score"]
            break
    
    # 增加提供者积分
    final_score = item["required_score"]
    if item["platform_fee"]:
        fee = int(item["required_score"] * 0.1)
        final_score = item["required_score"] - fee
        
        # 记录平台服务费
        st.session_state.transactions.append({
            "user": "platform",
            "amount": fee,
            "type": "平台服务费",
            "description": f"{item['title']}服务费",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
    
    for user in st.session_state.users:
        if user["name"] == item["user"]:
            user["score"] += final_score
            break
    
    # 更新项目状态
    for item_entry in st.session_state.marketplace:
        if item_entry["id"] == item_id:
            item_entry["status"] = "completed"
            break
    
    # 记录交易
    st.session_state.transactions.append({
        "user": st.session_state.user["phone"],
        "amount": -item["required_score"],
        "type": "兑换" + item["type"],
        "description": item["title"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    
    st.session_state.transactions.append({
        "user": next(u["phone"] for u in st.session_state.users if u["name"] == item["user"]),
        "amount": final_score,
        "type": item["type"] + "收益",
        "description": item["title"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    
    return True, f"成功兑换{item['type']}: {item['title']}"

# 审核文档
def review_document(doc_id, reward_score):
    doc = next((d for d in st.session_state.documents if d["id"] == doc_id), None)
    if not doc:
        return False, "文档不存在"
    
    if doc["status"] == "approved":
        return False, "文档已审核"
    
    # 更新文档状态
    for doc_item in st.session_state.documents:
        if doc_item["id"] == doc_id:
            doc_item["status"] = "approved"
            doc_item["reward_score"] = reward_score
            break
    
    # 奖励作者
    for user in st.session_state.users:
        if user["name"] == doc["author"]:
            user["score"] += reward_score
            break
    
    # 记录交易
    st.session_state.transactions.append({
        "user": next(u["phone"] for u in st.session_state.users if u["name"] == doc["author"]),
        "amount": reward_score,
        "type": "文档奖励",
        "description": doc["title"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    
    return True, "文档审核通过"

# 页面样式
def set_custom_style():
    st.markdown("""
    <style>
    /* 主色调 */
    :root {
        --primary-blue: #1e3a8a;
        --secondary-blue: #3b82f6;
        --gold: #d97706;
        --red: #dc2626;
        --green: #059669;
    }
    
    /* 整体样式 */
    body {
        background-color: #f0f7ff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 标题样式 */
    .title {
        color: var(--primary-blue);
        padding-bottom: 0.3rem;
        border-bottom: 3px solid var(--gold);
    }
    
    /* 卡片样式 */
    .card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--secondary-blue);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* 按钮样式 */
    .stButton>button {
        background-color: var(--secondary-blue) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background-color: var(--primary-blue) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* 积分徽章 */
    .score-badge {
        background-color: var(--gold);
        color: white;
        border-radius: 9999px;
        padding: 0.25rem 0.75rem;
        font-weight: bold;
        display: inline-block;
    }
    
    /* 市场项目卡片 */
    .market-item {
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .market-item:hover {
        border-color: var(--secondary-blue);
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .service-tag {
        background-color: var(--green);
        color: white;
        border-radius: 6px;
        padding: 0.25rem 0.5rem;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .part-tag {
        background-color: var(--secondary-blue);
        color: white;
        border-radius: 6px;
        padding: 0.25rem 0.5rem;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    /* 页脚样式 */
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: var(--primary-blue);
        color: white;
        text-align: center;
        padding: 0.5rem 0;
    }
    
    /* 响应式布局 */
    @media (max-width: 768px) {
        .card {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 主页
def home_page():
    st.title("叉车技术共享平台")
    st.subheader("专业维修经验共享，让叉车维护更简单")
    
    # 欢迎信息
    if st.session_state.user:
        user = st.session_state.user
        st.markdown(f"<div class='card'><h3>👋 欢迎回来，{user['name']}！</h3><p>您的当前积分：<span class='score-badge'>{user['score']}分</span></p></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card">
            <h3>欢迎来到叉车技术共享平台！</h3>
            <p>在这里，您可以：</p>
            <ul>
                <li>分享您的叉车维修经验，赚取积分</li>
                <li>学习他人的维修技巧，提升技能</li>
                <li>使用积分兑换配件或服务</li>
            </ul>
            <p>注册即送<span class='score-badge'>100积分</span>，立即加入！</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 热门文档
    st.header("🔥 热门技术文档")
    approved_docs = [doc for doc in st.session_state.documents if doc["status"] == "approved"]
    sorted_docs = sorted(approved_docs, key=lambda x: x["read_count"], reverse=True)[:3]
    
    if sorted_docs:
        for doc in sorted_docs:
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>{doc["title"]}</h3>
                        <span class='score-badge'>{doc["required_score"]}分</span>
                    </div>
                    <p><b>作者：</b>{doc["author"]} | <b>阅读次数：</b>{doc["read_count"]} | <b>奖励积分：</b>{doc["reward_score"]}</p>
                    <p>{doc["content"][:100]}...</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("暂无已审核文档")
    
    # 市场推荐
    st.header("🛒 热门配件与服务")
    active_items = [item for item in st.session_state.marketplace if item["status"] == "active"]
    
    if active_items:
        for item in active_items[:3]:
            tag_class = "service-tag" if item["type"] == "服务" else "part-tag"
            st.markdown(f"""
            <div class="market-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>{item["title"]}</h3>
                    <span class='score-badge'>{item["required_score"]}分</span>
                </div>
                <p><span class='{tag_class}'>{item["type"]}</span> | <b>提供者：</b>{item["user"]}</p>
                <p>{item["description"]}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("暂无可用配件或服务")

# 注册页面
def register_page():
    st.title("新用户注册")
    
    with st.form("注册表单"):
        phone = st.text_input("手机号", placeholder="请输入您的手机号")
        name = st.text_input("姓名", placeholder="请输入您的姓名")
        password = st.text_input("密码", type="password", placeholder="请设置登录密码")
        password_confirm = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
        
        submitted = st.form_submit_button("注册")
        
        if submitted:
            if not phone or not name or not password:
                st.error("请填写所有必填项")
            elif password != password_confirm:
                st.error("两次输入的密码不一致")
            else:
                success, message = register_user(phone, password, name)
                if success:
                    st.success(message)
                    st.balloons()
                    time.sleep(1)
                    st.session_state.page = "登录"
                    st.experimental_rerun()
                else:
                    st.error(message)

# 登录页面
def login_page():
    st.title("用户登录")
    
    with st.form("登录表单"):
        phone = st.text_input("手机号", placeholder="请输入您的手机号")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        
        submitted = st.form_submit_button("登录")
        
        if submitted:
            success, message = login_user(phone, password)
            if success:
                st.success(message)
                time.sleep(0.5)
                st.session_state.page = "主页"
                st.experimental_rerun()
            else:
                st.error(message)
    
    st.markdown("---")
    st.write("还没有账号？")
    if st.button("立即注册"):
        st.session_state.page = "注册"
        st.experimental_rerun()

# 文档列表页面
def documents_page():
    st.title("技术文档库")
    
    # 搜索和筛选
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("搜索文档", placeholder="输入关键词搜索")
    with col2:
        filter_status = st.selectbox("筛选状态", ["全部", "已审核", "待审核"])
    
    # 文档列表
    docs = st.session_state.documents
    if search_query:
        docs = [doc for doc in docs if search_query.lower() in doc["title"].lower() or 
               search_query.lower() in doc["content"].lower()]
    
    if filter_status == "已审核":
        docs = [doc for doc in docs if doc["status"] == "approved"]
    elif filter_status == "待审核":
        docs = [doc for doc in docs if doc["status"] == "pending"]
    
    if docs:
        for doc in docs:
            status_color = "green" if doc["status"] == "approved" else "orange"
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>{doc["title"]}</h3>
                        <div>
                            <span class='score-badge'>{doc["required_score"]}分</span>
                            <span style="color: {status_color}; font-weight: bold;">{doc["status"]}</span>
                        </div>
                    </div>
                    <p><b>作者：</b>{doc["author"]} | <b>发布日期：</b>{doc["created_at"]} | <b>阅读次数：</b>{doc["read_count"]}</p>
                    <p>{doc["content"][:150]}...</p>
                    <div style="margin-top: 1rem;">
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"阅读全文", key=f"read_{doc['id']}"):
                        success, result = read_document(doc["id"])
                        if success:
                            st.session_state.current_doc = result
                            st.session_state.page = "文档详情"
                            st.experimental_rerun()
                        else:
                            st.error(result)
                with col2:
                    if st.session_state.user and st.session_state.user["name"] == "管理员":
                        if st.button(f"审核文档", key=f"review_{doc['id']}"):
                            st.session_state.review_doc_id = doc["id"]
                            st.session_state.page = "文档审核"
                            st.experimental_rerun()
                
                st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.info("没有找到符合条件的文档")

# 文档详情页面
def document_detail_page():
    doc = st.session_state.current_doc
    st.title(doc["title"])
    
    st.markdown(f"""
    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3>{doc["title"]}</h3>
            <span class='score-badge'>{doc["required_score"]}分</span>
        </div>
        <p><b>作者：</b>{doc["author"]} | <b>发布日期：</b>{doc["created_at"]} | <b>阅读次数：</b>{doc["read_count"]}</p>
        <div style="margin-top: 1rem; padding: 1rem; background-color: #f9fafb; border-radius: 8px;">
            <p>{doc["content"]}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("返回文档列表"):
        st.session_state.page = "文档列表"
        st.experimental_rerun()

# 提交文档页面
def submit_document_page():
    st.title("提交技术文档")
    
    with st.form("文档提交表单"):
        title = st.text_input("文档标题", placeholder="请输入文档标题")
        required_score = st.number_input("所需积分", min_value=100, value=100, step=50)
        content = st.text_area("文档内容", height=300, placeholder="请输入详细的维修经验和技术说明...")
        
        submitted = st.form_submit_button("提交文档")
        
        if submitted:
            if not title or not content:
                st.error("请填写文档标题和内容")
            else:
                success, message = submit_document(title, content, required_score)
                if success:
                    st.success(message)
                    st.session_state.page = "文档列表"
                    st.experimental_rerun()
                else:
                    st.error(message)

# 文档审核页面
def review_document_page():
    doc_id = st.session_state.review_doc_id
    doc = next((d for d in st.session_state.documents if d["id"] == doc_id), None)
    
    if not doc:
        st.error("文档不存在")
        st.session_state.page = "文档列表"
        st.experimental_rerun()
    
    st.title("文档审核")
    st.subheader(doc["title"])
    
    st.markdown(f"""
    <div class="card">
        <p><b>作者：</b>{doc["author"]}</p>
        <p><b>所需积分：</b>{doc["required_score"]}分</p>
        <p><b>提交日期：</b>{doc["created_at"]}</p>
        <div style="margin-top: 1rem; padding: 1rem; background-color: #f9fafb; border-radius: 8px;">
            <p>{doc["content"]}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    reward_score = st.slider("奖励积分", min_value=10, max_value=100, value=50)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("通过审核", type="primary"):
            success, message = review_document(doc_id, reward_score)
            if success:
                st.success(message)
                time.sleep(1)
                st.session_state.page = "文档列表"
                st.experimental_rerun()
    with col2:
        if st.button("返回列表"):
            st.session_state.page = "文档列表"
            st.experimental_rerun()

# 市场页面
def marketplace_page():
    st.title("配件与服务市场")
    
    # 搜索和筛选
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("搜索配件或服务", placeholder="输入关键词搜索")
    with col2:
        filter_type = st.selectbox("筛选类型", ["全部", "配件", "服务"])
    
    # 添加新项目按钮
    if st.session_state.user:
        if st.button("发布新需求", type="primary"):
            st.session_state.page = "添加市场项目"
            st.experimental_rerun()
    
    # 市场项目列表
    items = st.session_state.marketplace
    if search_query:
        items = [item for item in items if search_query.lower() in item["title"].lower() or 
               search_query.lower() in item["description"].lower()]
    
    if filter_type != "全部":
        items = [item for item in items if item["type"] == filter_type]
    
    if items:
        for item in items:
            status_color = "green" if item["status"] == "active" else "gray"
            tag_class = "service-tag" if item["type"] == "服务" else "part-tag"
            st.markdown(f"""
            <div class="market-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>{item["title"]}</h3>
                    <div>
                        <span class='score-badge'>{item["required_score"]}分</span>
                        <span style="color: {status_color}; font-weight: bold;">{item["status"]}</span>
                    </div>
                </div>
                <p><span class='{tag_class}'>{item["type"]}</span> | <b>提供者：</b>{item["user"]}</p>
                <p>{item["description"]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if item["status"] == "active" and st.session_state.user:
                if st.button(f"兑换{item['type']}", key=f"redeem_{item['id']}"):
                    success, message = redeem_market_item(item["id"])
                    if success:
                        st.success(message)
                        st.experimental_rerun()
                    else:
                        st.error(message)
    else:
        st.info("没有找到符合条件的配件或服务")

# 添加市场项目页面
def add_market_item_page():
    st.title("发布新需求")
    
    with st.form("市场项目表单"):
        title = st.text_input("项目标题", placeholder="例如：叉车电池充电器")
        item_type = st.selectbox("项目类型", ["配件", "服务"])
        description = st.text_area("详细描述", height=150, placeholder="请提供详细描述...")
        required_score = st.number_input("所需积分", min_value=100, value=200, step=50)
        platform_fee = st.checkbox("需要平台担保（收取10%服务费）")
        
        submitted = st.form_submit_button("发布需求")
        
        if submitted:
            if not title or not description:
                st.error("请填写项目标题和详细描述")
            else:
                success, message = add_market_item(title, item_type, description, required_score, platform_fee)
                if success:
                    st.success(message)
                    st.session_state.page = "市场"
                    st.experimental_rerun()
                else:
                    st.error(message)

# 用户中心页面
def profile_page():
    user = st.session_state.user
    st.title(f"用户中心 - {user['name']}")
    
    # 用户信息
    st.markdown(f"""
    <div class="card">
        <h3>个人信息</h3>
        <p><b>手机号：</b>{user["phone"]}</p>
        <p><b>用户哈希值：</b>{user["hash"]}</p>
        <p><b>注册日期：</b>{user["reg_date"]}</p>
        <p><b>当前积分：</b><span class='score-badge'>{user["score"]}分</span></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 交易记录
    st.subheader("交易记录")
    user_transactions = [t for t in st.session_state.transactions if t["user"] == user["phone"]]
    
    if user_transactions:
        for trans in reversed(user_transactions[-5:]):
            amount_color = "green" if trans["amount"] > 0 else "red"
            amount_sign = "+" if trans["amount"] > 0 else ""
            st.markdown(f"""
            <div style="padding: 0.75rem; border-left: 4px solid {'#10b981' if trans['amount'] > 0 else '#ef4444'}; 
                        background-color: white; border-radius: 8px; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <b>{trans["type"]}</b>
                        <p style="font-size: 0.9rem; color: #6b7280;">{trans.get("description", "")}</p>
                    </div>
                    <div style="color: {amount_color}; font-weight: bold;">
                        {amount_sign}{trans["amount"]}分
                    </div>
                </div>
                <p style="font-size: 0.8rem; color: #9ca3af; margin-top: 0.5rem;">{trans["date"]}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("暂无交易记录")
    
    # 用户文档
    st.subheader("我的文档")
    user_docs = [doc for doc in st.session_state.documents if doc["author"] == user["name"]]
    
    if user_docs:
        for doc in user_docs:
            status_color = "green" if doc["status"] == "approved" else "orange"
            st.markdown(f"""
            <div class="card">
                <h3>{doc["title"]}</h3>
                <p><b>状态：</b><span style="color: {status_color};">{doc["status"]}</span> | 
                   <b>阅读次数：</b>{doc["read_count"]} | 
                   <b>奖励积分：</b>{doc.get("reward_score", 0)}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("您尚未提交文档")
    
    if st.button("退出登录"):
        st.session_state.user = None
        st.session_state.page = "主页"
        st.experimental_rerun()

# 主应用
def main():
    init_session_state()
    set_custom_style()
    
    # 设置页面状态
    if "page" not in st.session_state:
        st.session_state.page = "主页"
    
    # 侧边栏导航
    with st.sidebar:
        st.header("叉车变现")
        st.image("https://cdn-icons-png.flaticon.com/512/1701/1701550.png", width=80)
        
        if st.session_state.user:
            st.markdown(f"<p style='font-size: 1.1rem;'>欢迎, <b>{st.session_state.user['name']}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p>积分: <span class='score-badge'>{st.session_state.user['score']}分</span></p>", unsafe_allow_html=True)
        
        menu_options = ["主页", "文档列表", "市场"]
        if st.session_state.user:
            menu_options += ["提交文档", "用户中心"]
            if st.session_state.user["name"] == "管理员":
                menu_options += ["文档审核"]
        else:
            menu_options += ["登录", "注册"]
        
        st.session_state.page = st.selectbox("导航", menu_options, index=menu_options.index(st.session_state.page))
    
    # 页面路由
    if st.session_state.page == "主页":
        home_page()
    elif st.session_state.page == "注册":
        register_page()
    elif st.session_state.page == "登录":
        login_page()
    elif st.session_state.page == "文档列表":
        documents_page()
    elif st.session_state.page == "文档详情":
        document_detail_page()
    elif st.session_state.page == "提交文档":
        submit_document_page()
    elif st.session_state.page == "文档审核":
        review_document_page()
    elif st.session_state.page == "市场":
        marketplace_page()
    elif st.session_state.page == "添加市场项目":
        add_market_item_page()
    elif st.session_state.page == "用户中心":
        profile_page()
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>叉车变现平台 © 2023 | 专业叉车维修技术共享平台</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
