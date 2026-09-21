# 把项目上传到 GitHub

上传对象是 **movie-ratings-analysis 这个新文件夹**。父文件夹里的旧环境和重复文件不属于新仓库。GitHub 首页将自动展示英文 README，里面有中文入口与结果图。

## 最后填写的个人信息

当前文档按证据保留了 “CPSC 368 Group 1” 身份。可以补上真实成员署名，以及你自己实际负责的工作。项目没有替小组成员决定开放源代码许可；数据来源与使用说明已经放在 `NOTICE.md`。

建议仓库名：`movie-ratings-analysis`。

可直接使用的描述：

> Movie evaluation analysis across IMDb, Rotten Tomatoes, and the Oscars using Oracle SQL, MongoDB, and Python.

可选主题：`python`、`sql`、`oracle`、`mongodb`、`data-analysis`、`data-integration`、`data-visualization`。

## 上传步骤

在 GitHub 创建一个同名空仓库；为避免与本地文件冲突，创建页面先不要自动添加 README、.gitignore 或 License。然后在新项目文件夹内执行：

```powershell
cd 'D:\STY\CPSC 368\Project\movie-ratings-analysis'
git init -b main
git add .
git status
git commit -m "Organize movie ratings analysis portfolio"
git remote add origin https://github.com/Sabrina310/movie-ratings-analysis.git
git push -u origin main
```

仓库地址已设置为 `Sabrina310/movie-ratings-analysis`。如果本地 Git 要求姓名和邮箱，填写你希望显示在提交记录中的真实配置后重试提交。

`.gitignore` 已排除本地虚拟环境、密码文件、缓存和可再生成的逐行结果；输入数据、结果图、统计摘要、报告和源码会纳入仓库。`git status` 应只显示这个新目录里的项目内容。

上传后查看 README 图片与中文链接是否正常，并查看 Actions 中的 `Verify analysis` 检查。该检查将安装依赖、运行本地分析与匹配流程、执行回归测试；Oracle/MongoDB 服务不在此检查范围内。

## 仓库与后续更新

本地整理、复现与检查已完成。在线项目见 [GitHub 仓库](https://github.com/Sabrina310/movie-ratings-analysis)，自动检查见 [Actions](https://github.com/Sabrina310/movie-ratings-analysis/actions)。

首次上传完成后，之后修改文件只需要在项目目录执行：

```powershell
git add .
git commit -m "Update project documentation and analysis"
git push
```
