# skd-fireworks-masters
适用于森空岛的“狂欢烟火大师赛”的刷分脚本

## 使用方法
### 从源码运行
1. 克隆本仓库
2. 修改`config.py`中的`DEVICE_ADDRESS`，更改为模拟器的实际地址（mumu模拟器可以在多开器的ADB按钮选项中看）
3. 将模拟器分辨率修改为1600*900
3. 确保adb在环境变量中，亦可以将adb放到`bin/adb`下
4. `pip install -r requirements.txt`（当然创建虚拟环境也是可以的，在此不多赘述）
5. 将森空岛切换到游戏主界面（有开始的那个界面），`python main.py`

## 注
- 脚本写的很粗糙，因为急，几乎全部是AI写的，逻辑也很粗糙。
- config中硬编码了1600*900分辨率的参数，如果你需要其它分辨率可以自己调一下~