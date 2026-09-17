# 小刘的博客站

基于 [Hugo](https://gohugo.io/) + [hugo-theme-reimu](https://github.com/D-Sketon/hugo-theme-reimu)，源码在 `main`，由 GitHub Actions 构建并发布到 GitHub Pages。

在线地址：https://stay-leave.github.io/

## 首次部署注意

推送源码后，请在仓库网页设置一次：

`Settings → Pages → Build and deployment → Source` 选 **GitHub Actions**

否则会继续按「根目录静态文件」发布，站点会异常。

## 用 GitHub 桌面版新建文章

1. 用 GitHub Desktop 打开本仓库，确认当前分支是 `main`。
2. 在 `content/post/` 新建一个 Markdown 文件，例如 `我的新文章.md`（文件名会成为 URL 的一部分，建议用中文或英文均可）。
3. 文件开头写上 front matter，再写正文：

```yaml
---
title: "文章标题"
date: 2026-09-17T12:00:00+08:00
draft: false
categories: ["RAG"]
tags: ["LLM"]
---

这里写正文，支持 Markdown。

图片放到 `static/b_images/日期/`，正文里这样引用：

![说明](/b_images/日期/1.png)
```

4. `draft: false` 才会出现在首页；改成 `true` 表示草稿。
5. 在 GitHub Desktop 里填写提交说明 → Commit → Push origin。
6. 打开仓库的 Actions 页，等 **Deploy Hugo site to Pages** 跑完即可上线。

也可以复制现有文章（如 `content/post/rag给回复加上引用.md`）再改标题、日期和正文。

## 本地预览（可选）

需要本机安装 **Hugo Extended ≥ 0.158**，并初始化主题子模块：

```bash
git submodule update --init --recursive
hugo server
```

浏览器打开提示的本地地址即可预览。

## 常用目录

| 路径 | 作用 |
|------|------|
| `content/post/` | 文章 Markdown |
| `static/avatar/avatar.webp` | 侧栏头像（直接替换文件即可） |
| `static/b_images/` | 文章配图 |
| `config/_default/params.yml` | 站点名、作者、菜单、不蒜子等主题配置 |
| `hugo.toml` | 站点 URL、语言 |

## 主题升级

主题以 git submodule 放在 `themes/hugo-theme-reimu`。升级示例：

```bash
cd themes/hugo-theme-reimu
git fetch
git checkout v0.16.1   # 或更新的 tag
cd ../..
git add themes/hugo-theme-reimu
```

然后提交推送即可。
