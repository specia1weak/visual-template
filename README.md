## 环境
```commandline
pip install -r requirements.txt
```
## 使用
直接运行即可

1. 在main_cfg中配置脚本文件，文件自动保存在data/templates_mathing下。 路径例如"data/templates_matching/960x600/Test/configs/960x600-play.json"
2. 在cfg.yaml 中的modes列表中加入该json路径
```yaml
modes: ["data/templates_matching/960x600/Test/configs/960x600-play.json"] # 如果列表多个元素，那么他们会合并运行
```
3. 在main_run中运行脚本文件

后续会出教程