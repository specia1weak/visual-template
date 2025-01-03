## 环境
```commandline
pip install -r requirements.txt
```
## 快速开始
直接运行即可

1. 在main_cfg中配置脚本文件，文件自动保存在data/templates_mathing下。 路径例如"data/templates_matching/960x600/Test/configs/960x600-play.json"
2. 在cfg.yaml 中的modes列表中加入该json路径
```yaml
modes: ["data/templates_matching/960x600/Test/configs/960x600-play.json"] # 如果列表多个元素，那么他们会合并运行
```
3. 在main_run中运行脚本文件

后续会出教程

## main_cfg.py
### 可以调整的参数
```python
template_config_generator = TemplateConfigGenerator(game_name="Test", hwnd=search_mumu("MuMu模拟器12"), mode="test1")
```
game_name 与 mode会影响配置文件的存放位置，但是不会对文件的运行有影响

hwnd为句柄，可以传入模拟窗口的句柄，如果是mumu模拟器也可以调用search_mumu("你的模拟器标题")让程序找
### 更多的操作
在main_cfg.py 下，你可以自主选择不同的detector 和 operations，可以通过DetectorType，OperationType来获得更多的操作
```python
if __name__ == "__main__":
    detector = DetectorType.FIXED_REGION
    operations = []
    operations.append(OperationType.TAP)
    # operations.append(OperationType.
    configurate(detector, operations)
```
detector和operations列表是分离的，因此组合可以有很多强大的操作
#### Detector 类别
1. DetectorType.FIXED_REGION: 检测一个固定区域是否等于模板
2. DetectorType.REGION_EXISTS: 检测一个大区域是否存在模板
3. 更多省略

#### Operation 类别
1. OperationType.TAP: 在一个固定坐标点击一次
2. OperationType.DRAG: 在一个预设的固定直线路径拖拽一次
3. OperationType.ADB_EVENT: 使用adb shell input keyevent 命令
4. OperationType.KEY_TEXT: 使用adb shell input "text" 命令 text可以在代码中指定
5. 还有更多不一一列举

## main_run.py
run通过读取cfg.yaml中的modes字段寻找脚本配置文件，所以运行前保证脚本路径存在于这个字段中。
```python
if __name__ == "__main__":
    run("./cfg.yaml")
```

```yaml
modes: ["data/templates_matching/960x600/Test/configs/960x600-play.json"] # 如果列表多个元素，那么他们会合并运行
```