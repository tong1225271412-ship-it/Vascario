# Vascário P1.5：工程增强版与一万词扩容器

## 开箱即用

`index.html`：P1 现有精选词条 + 966条工程术语原始表（与现有词条去重后部分覆盖）。不需要付费 API、云数据库或在线语音。

独立体验版：使用单 HTML 文件直接离线运行，不依赖 GitHub Actions。

词典首页→检索 `ensaio de carga`、`barragem`、`bloco de coroamento`、`prorrogação de prazo`、`não conformidade`、`betão`、`concreto` 等工程词汇。分类栏新增“工程、桥梁、岩土、水工、电气、合同、质量”。

## 为什么初次打开并非一万词？

当前本地制作环境不能直接下载完整中文 Wiktionary 原始词库。我们提供可运行的**公开词库自动扩容器**，而不捏造一万条无含义的词条。`data/open_lexicon.json` 初始是 `{}`；网上执行扩容后才会成为有实际释义的开放词库。生成后词条会通过浏览器加载并缓存。

## 完全免费的扩容方式（推荐 GitHub Pages）

1. 将 `Vascario_P1_5_网站` 目录内的**所有文件和隐藏目录 `.github`** 上传至 GitHub 公开仓库根目录（不要将外层文件夹作为网站根目录）。
2. 在 GitHub 仓库：**Settings → Pages → Deploy from a branch → main / root**。网站部署与一般 PWA 相同。
3. 在 GitHub：**Actions → Expand Portuguese-Chinese Dictionary → Run workflow**。脚本会下载 Kaikki 的葡萄牙語/葡萄牙语中文词库，清洗中文定义和词形，并自动将生成的数据提交到仓库。
4. 运行结束后，在 `data/build_report.json` 查验 **selected_entries**、**total_distinct_app_headwords**、**target_met**。若有效词条没有达到 10,000 条，结果会如实显示缺口，绝不自动补出虚假单词。
5. 再次打开网站，词条数量会按生成文件实际数量增加。首次下载开放词库需要联网；资源加载后可在已缓存的设备上离线使用（浏览器可能清除缓存）。

**免费条件**：在 GitHub 免费额度允许范围内，使用公开仓库的 GitHub Pages 和 Actions。无需购买 API 或另租服务器。仓库如果属于组织或有限制，应按实际账户额度为准。

## 本地扩容（适合后续开发）

先从 [Kaikki 葡萄牙語](https://kaikki.org/zhwiktionary/%E8%91%A1%E8%90%84%E7%89%99%E8%AA%9E/index.html) 和 [Kaikki 葡萄牙语](https://kaikki.org/zhwiktionary/%E8%91%A1%E8%90%84%E7%89%99%E8%AF%AD/index.html) 下载 JSONL，或者执行：

```bash
python scripts/import_kaikki.py --download --out data/open_lexicon.json --report data/build_report.json --target 10000 --limit 15000
```

默认脚本不需要收费服务。为了显示为简体中文，推荐在运行环境安装免费的 `opencc-python-reimplemented`；GitHub Actions 已自动安装。

## 重要规则

- 绝不使用人名、英文译文或动词变位来冒充有效基础葡汉词条。
- 不自动编造工程词条例句；没有经过审核的例句会明确显示待补充。
- 现有精选词条和工程精选词条优先于开放词库；同名不覆盖。
- 出现词义冲突时，根据真实合同、技术规范及地区语言变体人工审核。
- 开放词库归属与许可：见 `LICENSE_DATA.md`，包括 CC BY-SA 的署名及衍生内容要求。

**本次工程专业内容**：966条独立工程词目，覆盖土建、桥梁、岩土、水电、道路、施工机械、电气、焊接、合同、计量支付、质量和安全。部分与旧版词条重叠，因此实际应用合并词数小于简单相加。
