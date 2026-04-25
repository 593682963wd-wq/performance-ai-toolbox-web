# 机场新旧数据对比 — 网页版 (Streamlit)

参考《机场障碍物分析》同款双端结构。`core/` 与桌面端字节一致：
```
diff -rq /Users/amanda/Documents/airport_data_compare/core \
         /Users/amanda/Desktop/airport-data-compare-web/core
```

启动：
```
cd /Users/amanda/Desktop/airport-data-compare-web
pip install -r requirements.txt
streamlit run app.py
```
