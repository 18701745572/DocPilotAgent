# OOM 排错指南

> Java 服务进程被 OOM Killer 终止的排查与修复。

## 现象

- 服务进程被系统 OOM Killer 终止，`dmesg` 含 `Out of memory: Killed process`
- 或应用抛出 `OutOfMemoryError: Java heap space`
- 严重时伴随 `NullPointerException`（堆损坏副作用）

## 排查步骤

1. 确认被杀进程：`dmesg | grep -i oom`
2. 查应用日志中的 `OutOfMemoryError` 行：`grep -i "OutOfMemory\|oom" logs/app.log`
3. 检查 JVM 启动参数 `-Xmx` 是否过小
4. 复查近期大查询：是否一次性加载全表
5. 检查缓存上限：是否无淘汰策略

## 常见根因

- 未分页大查询（一次拉取数十万行）
- 缓存无上限（如 `HashMap` 累积）
- 连接泄漏（连接未释放，资源堆积）
- `-Xmx` 配置过小

## 调试建议

- 调大 `-Xmx`（如从 2g 改为 4g）
- 启用 `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/log/app/heapdump.hprof`
- 用 `jmap -histo:live <pid>` 定位占用大户
- 大查询加分页与流式处理

## 参考

- [用户服务接口文档](../api/user-service.md)：错误码定义
