# FSMTSG

基于有限状态机的漏洞基准测试集生成，目前主要PHP语言的sqli、xss漏洞进行生成，可通过在`xml`文件中添加代码片段来生成更多漏洞类型、应用场景的的测试集。

## 运行环境
- python3.12
- php 7.4

## 运行方式

```
# 生成sqli基准测试集
python3 main_sqli.py

# 生成xss基准测试集
python3 main_xss.py
```

## 参数调整

在`main_*.py`中：
- 调整`repeat_num`参数可以调整生成的测试集数量；
- 调整`decorator_*`参数可以调整生成的测试集的装饰器的数量、层数等；

