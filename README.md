# 小刘的博客站

个人技术博客，线上地址：https://stay-leave.github.io/

站点用 [Hugo](https://gohugo.io/) + [hugo-theme-reimu](https://github.com/D-Sketon/hugo-theme-reimu) 生成，源码在 [`hugo-src/`](hugo-src/)，GitHub Pages 继续托管仓库根目录的静态文件。

## 本地预览

需要 Hugo Extended ≥ 0.158（当前构建用 0.166.0）：

```bash
git submodule update --init --recursive
hugo server -s hugo-src
```

## 写新文章

1. 在 `hugo-src/content/post/` 新建 Markdown，文件名会成为 URL：`/post/<文件名>/`
2. Front matter 至少包含 `title`、`date`、`categories`、`tags`；封面用 `cover: "/images/..."` 或 `/b_images/...`
3. 配图放到 `hugo-src/static/b_images/` 或 `hugo-src/static/images/`
4. 本地 `hugo server -s hugo-src` 预览
5. 发布：

```bash
bash hugo-src/scripts/publish.sh
git add -A && git commit && git push
```

也可以只改 `hugo-src/` 并推到 `main`，GitHub Actions 会自动构建并写回根目录。不要提交 `hugo server` 的开发产物（带 `localhost:1313` / `livereload` 的页面）。

## 站点身份

作者、头像、关于页、友链在：

- `hugo-src/config/_default/params.yml`
- `hugo-src/content/about.md`
- `hugo-src/content/friend.md`
- `hugo-src/data/friends.yml`
- `hugo-src/static/avatar/avatar.webp`
