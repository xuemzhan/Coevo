# K8s CRD 纸面清单生成器（CTAF §14.2 / §16.4 / M9）

> 里程碑：M9（2026-08-08 交付）。实现：`src/coevo/framework/k8s_listing.py`。
> 工作项：`US-16-AC-9-k8s-crd-listing-v0.1`。

## 定位

把框架声明（能力注册表 / Tool 注册表 / Policy / Plan）导出为**确定性、可哈希的
纸面清单**（规范 JSON + 安全 YAML 渲染子集），供文档与合规使用。按 §16.4 承诺
范围：**仅纸面清单，不实现 reconcile loop、不依赖 Kubernetes、零 IO**。

## 入口

- `generate_listing_json(input)`：构建规范清单结构（apiVersion / kind /
  metadata / spec）；
- `generate_listing(input)`：规范 JSON 字节（排序键、紧凑分隔、ASCII 转义）；
- `listing_fingerprint(input)`：规范字节 SHA-256（审计/版本比对）；
- `render_yaml(bytes)`：安全 YAML 子集渲染（字符串双引号、布尔/数字原样、
  嵌套确定性缩进）；
- `validate_listing_bytes(bytes)`：严格解析（BOM / 重复键 / 未知字段 / 64 KiB
  上限全部拒绝）；
- `ListingInput.to_audit_record()`：审计投影（固定键摘要 + listing_fingerprint，
  不含 spec 明细）。

## 结构

```text
apiVersion: coevo.framework/v1
kind: DeclarativeListing
metadata: { schema_version, generated_at }
spec: { capabilities[], tools[], policies[], plans[] }
```

## 安全边界

- YAML 渲染对字符串做安全引号（内嵌引号/冒号/井号不破坏结构）；
- 清单校验白名单字段，未知/重复键显式拒绝；
- 生成器纯函数、零 IO 副作用（opt-in 沙箱可直接运行）；
- 纯函数、仅标准库、可离线运行（L15）；文档守卫（L17）。

## 测试覆盖

`tests/unit/test_framework_k8s_listing.py`（AC-9.1..9.5，含确定性/哈希、YAML
安全引号、空输入、重复键/未知字段/BOM/超限负例、stdlib 断言）。
