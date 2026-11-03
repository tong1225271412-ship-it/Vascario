# Vascário P1.5 — 词库来源与许可

## 1. 内置工程词库

工程专业条目、中文基础释义及配套示例由本项目独立整理编写；术语作为施工与翻译学习参考，不代替合同文本、设计规范或合格专业人员的审查。

## 2. 可选的开放词库

可通过本项目 `scripts/import_kaikki.py` 提取以下公开数据：

- [中文 Wiktionary](https://zh.wiktionary.org/)（葡萄牙語/葡萄牙语，词条由维基贡献者共同编写）
- [Kaikki / Wiktextract](https://kaikki.org/zhwiktionary/)（用于生成机器可读取结构化数据的工具与公开镜像；Tatu Ylonen 等贡献者）
- 具体原始数据地址及运行时间见 `data/build_report.json`；开放词条页面包含每条词的 Wiktionary 来源 URL。

维基词典文本按适用的 **Creative Commons Attribution–ShareAlike (CC BY-SA)** 等许可分发。请参阅 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.zh-hans) 和 [Wiktionary 版权说明](https://en.wiktionary.org/wiki/Wiktionary:Copyrights)。如再发布由开放词典衍生的数据，应满足相应署名、许可通知及相同方式共享条件；不得把这些开放释义当作本应用原创独占内容。

> 本应用对来源内容做了必要的结构化筛选、简体转换、数据截断及检索格式处理；这一处理不等于完成了人工语言校审。

## 3. 自编工程术语与第三方词条的区别

- **工程精选**：本项目组织整理的工程双语对应和部分自编例句。
- **开放词库**：取自中文 Wiktionary / Kaikki 的词义，必须显示署名与相应许可。
- **个人导入**：用户自己编写的词条，仅保存在当前浏览器中。

## 4. 音频

软件不捆绑或复制第三方发音素材。语音朗读调用浏览器/设备内置的语音合成，声音取决于系统。
