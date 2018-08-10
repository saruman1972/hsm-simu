HSMSim使用说明：
HSMSim.exe - 加密机模拟程序(本地侦听端口6666)
KeyTranslateDialog.exe - 密钥转换程序
MakeCardDialog.exe - 生成卡片信息(PIN、二磁道)

Retrieve.sh - 压力测试随机抽取卡片
Usage: Retrieve.sh [输入del文件] [需要抽取的卡片数目]
输入文件：从数据库中导出的卡片列表。
格式：卡号,有效期,PIN OFFSET
"4026740000000001","200902","000000FFFFFF"
输出文件：输入文件名.Rand

GenCrdData.exe - 压力测试时候批量生成卡片信息
Usage: GenCrdData.exe [输入卡片列表] > cards.txt
输入卡片列表：由Retrieve.sh产生
输出文件：cards.txt - 生成的卡片信息，包含密码、磁道信息
