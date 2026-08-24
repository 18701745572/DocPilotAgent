# OOM 排错指南

## 现象

服务进程被 OOM Killer 终止，系统日志出现 `Out of memory: Kill process`。

## 排查步骤

1. `dmesg | grep -i oom` 确认被杀进程；
2. 查看应用日志是否存在内存泄漏（堆使用持续增长）；
3. 检查 JVM 堆配置 `-Xmx` 是否过小；
4. 复查是否有大查询未分页导致结果集过大。

## 常见根因

- 查询未分页，单次结果集过大；
- 缓存无上限策略；
- 连接泄漏导致堆外内存增长。

## 调试建议

- 临时调大 `-Xmx` 观察是否复现；
- 启用堆 dump（`-XX:+HeapDumpOnOutOfMemoryError`）定位对象；
- 检查日志中 `OutOfMemoryError` 附近的业务路径。
