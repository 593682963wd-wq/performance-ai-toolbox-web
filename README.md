# 性能 AI 工具台 (Performance AI Toolbox)

把 3 个独立工具汇总到同一个 Streamlit Web 站点：

| 页面 | 工具 | 说明 |
|---|---|---|
| 🗼 机场障碍物分析 | `tools_obstacle/` | 来源: airport-obstacle-web |
| 📊 机场新旧数据对比 | `tools_compare/` | 来源: airport-data-compare-web |
| 📦 航线载量分析 | `tools_routeload/` | 来源: 航线载量分析工具 |

## 本地启动
```
cd /Users/amanda/Desktop/performance-ai-toolbox-web
pip install -r requirements.txt
streamlit run app.py
```

## 部署到 Streamlit Cloud
1. 在 GitHub 上创建仓库 `performance-ai-toolbox-web`
2. `git push` 到该仓库
3. 登录 https://share.streamlit.io/ → New app → 选择仓库 → Main file = `app.py` → Deploy

## 同步原工具的更新
本仓库的 3 个 `tools_*/` 是**镜像副本**。原工具有改动时同步：
```
rsync -a --exclude='.git*' --exclude='.streamlit' --exclude='__pycache__' \
  /Users/amanda/Desktop/airport-obstacle-web/        tools_obstacle/
rsync -a --exclude='.git*' --exclude='.streamlit' --exclude='__pycache__' \
  /Users/amanda/Desktop/airport-data-compare-web/    tools_compare/
rsync -a --exclude='.git*' --exclude='.streamlit' --exclude='__pycache__' \
  --exclude='输入' --exclude='输出' \
  /Users/amanda/Desktop/航线载量分析工具/             tools_routeload/
git add -A && git commit -m "sync tools" && git push
```
