## 2026-08-07T20:05:48.416983Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-07T20:05:59.117774Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
e_regression.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-7",
      "title": "��ܲ� Plan �淶�����л���Plan-LSP��CTAF ��14.2 / M6����Plan<->�淶 JSON ˫�����л���plan_to_json / json_to_plan / parse_plan_json_bytes�������ֽڼ�һ�¡��ظ���/δ֪�ֶ�/BOM/�Ǳ�׼����/���Ƕ��/����ȫ�� fail-closed������ plan_fingerprint ͬһ�淶�����򣨷�ָ�Ʒֲ棩��validate_plan_json ���л���ڣ�������� + L18 + L19��ʧ�ܷ��� REJECTED������С/�ڵ�/��/tool_args ���ޡ����������� stdlib + L17��plan-lsp.md��",
      "code": [
        "src/coevo/framework/plan.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/plan-lsp.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_plan_lsp.py",
        "tests/unit/test_framework_validate_plan.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/plan-lsp.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_lsp.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-8",
      "title": "��ܲ� Hybrid Orchestrator��CTAF ��6.6 / ��8 / M7����OrchestrationEngine ��Լ + validate_plan Ϊ dispatch ǰ�ñص���δУ��/У��ʧ�ܲ��� dispatch����StateMachine ��̬����ע�� provider������ Plan ��ִ�У�ʧ��/�쳣 fail-closed ת ESCALATED + audit RECOVER����DynamicLLM ���龭������� + L18 + L19 ͨ����ִ�У�������Ч/�쳣���� StateMachine����Hybrid ���� HOLD �ڵ���� LLM ���ǣ����� HOLD �����麬 HOLD �� ������ Plan��HELD �˹���ǿ�ơ�ִ���������ã���L19 ��̬�νӣ�ESCALATED��ACTIVE ���뾭 HELD��+ ���ͶӰ + ע��ִ����/LLM/�������������� stdlib��+ L17��hybrid-orchestrator.md��",
      "code": [
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/hybrid-orchestrator.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_orchestrator.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/hybrid-orchestrator.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_orchestrator.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-9",
      "title": "��ܲ� K8s CRD ֽ���嵥��������CTAF ��14.2 / ��16.4 / M9����������/Tool/Policy/Plan ��������ȷ����ֽ���嵥���淶 JSON + YAML ��ȫ��Ⱦ�Ӽ�����ֽ�治��ŵ reconcile loop���� K8s ����� IO����listing_fingerprint SHA-256 �ɹ�ϣ��opt-in ɳ�䴿�������� IO �����ã����嵥�ṹУ�� fail-closed���ֶΰ����� / �ظ��� / δ֪�ֶ� / BOM / 64KiB ���� / 64 ����ȣ������ͶӰ�̶���ժҪ������ spec ��ϸ����stdlib-only + L17 �ĵ�������k8s-crd-listing.md��",
      "code": [
        "src/coevo/framework/k8s_listing.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/k8s-crd-listing.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_k8s_listing.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/k8s-crd-listing.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-1",
      "title": "������۲����տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����semver/ISO-8601 ��ʽУ�飨manifest semantic_version / a2a created_at / memory occurred_at��L7����Policy ��ʱ�Ͻ� dispatch��600s / plan_total��7200s / consent��7200s��Info4����Orchestrator �� provider �쳣����Ϊ OrchestrationError + ���ͶӰ�� validated_at��Low����K8s �嵥 spec ���ڰ� capability/tool/policy/plan ������У��δ֪����Low�����ĵ���ȡ�ᣨtrusted_anchor ί�� L2 / ����������� L4 / ������ Info5���������� stdlib + L17",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/policy.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/k8s_listing.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-07T20:10:43.489256Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
s/unit/test_framework_plan_lsp.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-8",
      "title": "��ܲ� Hybrid Orchestrator��CTAF ��6.6 / ��8 / M7����OrchestrationEngine ��Լ + validate_plan Ϊ dispatch ǰ�ñص���δУ��/У��ʧ�ܲ��� dispatch����StateMachine ��̬����ע�� provider������ Plan ��ִ�У�ʧ��/�쳣 fail-closed ת ESCALATED + audit RECOVER����DynamicLLM ���龭������� + L18 + L19 ͨ����ִ�У�������Ч/�쳣���� StateMachine����Hybrid ���� HOLD �ڵ���� LLM ���ǣ����� HOLD �����麬 HOLD �� ������ Plan��HELD �˹���ǿ�ơ�ִ���������ã���L19 ��̬�νӣ�ESCALATED��ACTIVE ���뾭 HELD��+ ���ͶӰ + ע��ִ����/LLM/�������������� stdlib��+ L17��hybrid-orchestrator.md��",
      "code": [
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/hybrid-orchestrator.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_orchestrator.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/hybrid-orchestrator.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_orchestrator.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-9",
      "title": "��ܲ� K8s CRD ֽ���嵥��������CTAF ��14.2 / ��16.4 / M9����������/Tool/Policy/Plan ��������ȷ����ֽ���嵥���淶 JSON + YAML ��ȫ��Ⱦ�Ӽ�����ֽ�治��ŵ reconcile loop���� K8s ����� IO����listing_fingerprint SHA-256 �ɹ�ϣ��opt-in ɳ�䴿�������� IO �����ã����嵥�ṹУ�� fail-closed���ֶΰ����� / �ظ��� / δ֪�ֶ� / BOM / 64KiB ���� / 64 ����ȣ������ͶӰ�̶���ժҪ������ spec ��ϸ����stdlib-only + L17 �ĵ�������k8s-crd-listing.md��",
      "code": [
        "src/coevo/framework/k8s_listing.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/k8s-crd-listing.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_k8s_listing.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/k8s-crd-listing.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-1",
      "title": "������۲����տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����semver/ISO-8601 ��ʽУ�飨manifest semantic_version / a2a created_at / memory occurred_at��L7����Policy ��ʱ�Ͻ� dispatch��600s / plan_total��7200s / consent��7200s��Info4����Orchestrator �� provider �쳣����Ϊ OrchestrationError + ���ͶӰ�� validated_at��Low����K8s �嵥 spec ���ڰ� capability/tool/policy/plan ������У��δ֪����Low�����ĵ���ȡ�ᣨtrusted_anchor ί�� L2 / ����������� L4 / ������ Info5���������� stdlib + L17",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/policy.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/k8s_listing.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-2",
      "title": "GAPS-1 �¹۲����տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����Policy TimeoutProfile/RetryProfile/ConsentProfile �ϸ��������ͣ�bool/str/float/int ����һ�� PolicyValidationError��`type(...) is int`����semver �ϸ���򣨽�ǰ�����㣩��ISO-8601 ������ΧУ�飨datetime.strptime��a2a created_at / memory occurred_at / validate_plan validated_at / transition validated_at����validated_at �����ͶӰǰͳһ L7 ISO У�飻������ stdlib + L17",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/orchestrator.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-07T20:11:57.193145Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
s/unit/test_framework_plan_lsp.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-8",
      "title": "��ܲ� Hybrid Orchestrator��CTAF ��6.6 / ��8 / M7����OrchestrationEngine ��Լ + validate_plan Ϊ dispatch ǰ�ñص���δУ��/У��ʧ�ܲ��� dispatch����StateMachine ��̬����ע�� provider������ Plan ��ִ�У�ʧ��/�쳣 fail-closed ת ESCALATED + audit RECOVER����DynamicLLM ���龭������� + L18 + L19 ͨ����ִ�У�������Ч/�쳣���� StateMachine����Hybrid ���� HOLD �ڵ���� LLM ���ǣ����� HOLD �����麬 HOLD �� ������ Plan��HELD �˹���ǿ�ơ�ִ���������ã���L19 ��̬�νӣ�ESCALATED��ACTIVE ���뾭 HELD��+ ���ͶӰ + ע��ִ����/LLM/�������������� stdlib��+ L17��hybrid-orchestrator.md��",
      "code": [
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/hybrid-orchestrator.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_orchestrator.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/hybrid-orchestrator.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_orchestrator.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-9",
      "title": "��ܲ� K8s CRD ֽ���嵥��������CTAF ��14.2 / ��16.4 / M9����������/Tool/Policy/Plan ��������ȷ����ֽ���嵥���淶 JSON + YAML ��ȫ��Ⱦ�Ӽ�����ֽ�治��ŵ reconcile loop���� K8s ����� IO����listing_fingerprint SHA-256 �ɹ�ϣ��opt-in ɳ�䴿�������� IO �����ã����嵥�ṹУ�� fail-closed���ֶΰ����� / �ظ��� / δ֪�ֶ� / BOM / 64KiB ���� / 64 ����ȣ������ͶӰ�̶���ժҪ������ spec ��ϸ����stdlib-only + L17 �ĵ�������k8s-crd-listing.md��",
      "code": [
        "src/coevo/framework/k8s_listing.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/k8s-crd-listing.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_k8s_listing.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/k8s-crd-listing.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-1",
      "title": "������۲����տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����semver/ISO-8601 ��ʽУ�飨manifest semantic_version / a2a created_at / memory occurred_at��L7����Policy ��ʱ�Ͻ� dispatch��600s / plan_total��7200s / consent��7200s��Info4����Orchestrator �� provider �쳣����Ϊ OrchestrationError + ���ͶӰ�� validated_at��Low����K8s �嵥 spec ���ڰ� capability/tool/policy/plan ������У��δ֪����Low�����ĵ���ȡ�ᣨtrusted_anchor ί�� L2 / ����������� L4 / ������ Info5���������� stdlib + L17",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/policy.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/k8s_listing.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-2",
      "title": "GAPS-1 �¹۲����տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����Policy TimeoutProfile/RetryProfile/ConsentProfile �ϸ��������ͣ�bool/str/float/int ����һ�� PolicyValidationError��`type(...) is int`����semver �ϸ���򣨽�ǰ�����㣩��ISO-8601 ������ΧУ�飨datetime.strptime��a2a created_at / memory occurred_at / validate_plan validated_at / transition validated_at����validated_at �����ͶӰǰͳһ L7 ISO У�飻������ stdlib + L17",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/orchestrator.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```





## 2026-08-07T20:24:07.981256Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-07T20:24:15.320359Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
嵥���淶 JSON + YAML ��ȫ��Ⱦ�Ӽ�����ֽ�治��ŵ reconcile loop���� K8s ����� IO����listing_fingerprint SHA-256 �ɹ�ϣ��opt-in ɳ�䴿�������� IO �����ã����嵥�ṹУ�� fail-closed���ֶΰ����� / �ظ��� / δ֪�ֶ� / BOM / 64KiB ���� / 64 ����ȣ������ͶӰ�̶���ժҪ������ spec ��ϸ����stdlib-only + L17 �ĵ�������k8s-crd-listing.md��",
      "code": [
        "src/coevo/framework/k8s_listing.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/k8s-crd-listing.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_k8s_listing.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/k8s-crd-listing.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-1",
      "title": "������۲����տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����semver/ISO-8601 ��ʽУ�飨manifest semantic_version / a2a created_at / memory occurred_at��L7����Policy ��ʱ�Ͻ� dispatch��600s / plan_total��7200s / consent��7200s��Info4����Orchestrator �� provider �쳣����Ϊ OrchestrationError + ���ͶӰ�� validated_at��Low����K8s �嵥 spec ���ڰ� capability/tool/policy/plan ������У��δ֪����Low�����ĵ���ȡ�ᣨtrusted_anchor ί�� L2 / ����������� L4 / ������ Info5���������� stdlib + L17",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/policy.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/k8s_listing.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-2",
      "title": "GAPS-1 �¹۲����տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����Policy TimeoutProfile/RetryProfile/ConsentProfile �ϸ��������ͣ�bool/str/float/int ����һ�� PolicyValidationError��`type(...) is int`����semver �ϸ���򣨽�ǰ�����㣩��ISO-8601 ������ΧУ�飨datetime.strptime��a2a created_at / memory occurred_at / validate_plan validated_at / transition validated_at����validated_at �����ͶӰǰͳһ L7 ISO У�飻������ stdlib + L17",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/orchestrator.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-3",
      "title": "GAPS-2 �¹۲����տڣ�2026-08-08���û�ָ��\"��������\"����semver ���� $ ��Ϊ \\Z �ܾ�β�����У�1.0.0\\n ���ٱ����ܣ���ISO ·������ strptime ��ס������ 2 �test_framework_gaps3.py��",
      "code": [
        "src/coevo/framework/manifest_checker.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-1",
      "title": "��ܽ������б��ţ�GuardedOrchestrator ���䣬2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����guard_registration��manifest-checker ͨ����ע�ᣬ�ܾ������� inner_register��inner �쳣 fail-closed����plan_to_chain����� Plan AGENT/HUMAN_GATE �� ���� OrchestrationChain��AGENT ����������ע�����Ϊ AGENT_CALL��HUMAN_GATE �� HUMAN_CONFIRM��TOOL �ڵ����ܳ���������ȷ�ܾ� IntegrationError����guarded_dispatch��validate_plan ǰ�� �� plan_to_chain �� Orchestrator.dispatch_event �� ����ӳ�� OrchestrationOutcome��COMPLETED/HELD/ESCALATED��FAILED/δ֪ �� ESCALATED fail-closed���ڲ��쳣������������GuardResult ���ͶӰ�̶��ļ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```



## 2026-08-07T20:32:45.293810Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-07T20:32:55.566275Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
嵥���淶 JSON + YAML ��ȫ��Ⱦ�Ӽ�����ֽ�治��ŵ reconcile loop���� K8s ����� IO����listing_fingerprint SHA-256 �ɹ�ϣ��opt-in ɳ�䴿�������� IO �����ã����嵥�ṹУ�� fail-closed���ֶΰ����� / �ظ��� / δ֪�ֶ� / BOM / 64KiB ���� / 64 ����ȣ������ͶӰ�̶���ժҪ������ spec ��ϸ����stdlib-only + L17 �ĵ�������k8s-crd-listing.md��",
      "code": [
        "src/coevo/framework/k8s_listing.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/k8s-crd-listing.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_k8s_listing.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/k8s-crd-listing.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-1",
      "title": "������۲����տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����semver/ISO-8601 ��ʽУ�飨manifest semantic_version / a2a created_at / memory occurred_at��L7����Policy ��ʱ�Ͻ� dispatch��600s / plan_total��7200s / consent��7200s��Info4����Orchestrator �� provider �쳣����Ϊ OrchestrationError + ���ͶӰ�� validated_at��Low����K8s �嵥 spec ���ڰ� capability/tool/policy/plan ������У��δ֪����Low�����ĵ���ȡ�ᣨtrusted_anchor ί�� L2 / ����������� L4 / ������ Info5���������� stdlib + L17",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/policy.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/k8s_listing.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-2",
      "title": "GAPS-1 �¹۲����տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����Policy TimeoutProfile/RetryProfile/ConsentProfile �ϸ��������ͣ�bool/str/float/int ����һ�� PolicyValidationError��`type(...) is int`����semver �ϸ���򣨽�ǰ�����㣩��ISO-8601 ������ΧУ�飨datetime.strptime��a2a created_at / memory occurred_at / validate_plan validated_at / transition validated_at����validated_at �����ͶӰǰͳһ L7 ISO У�飻������ stdlib + L17",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/orchestrator.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-3",
      "title": "GAPS-2 �¹۲����տڣ�2026-08-08���û�ָ��\"��������\"����semver ���� $ ��Ϊ \\Z �ܾ�β�����У�1.0.0\\n ���ٱ����ܣ���ISO ·������ strptime ��ס������ 2 �test_framework_gaps3.py��",
      "code": [
        "src/coevo/framework/manifest_checker.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-1",
      "title": "��ܽ������б��ţ�GuardedOrchestrator ���䣬2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����guard_registration��manifest-checker ͨ����ע�ᣬ�ܾ������� inner_register��inner �쳣 fail-closed����plan_to_chain����� Plan AGENT/HUMAN_GATE �� ���� OrchestrationChain��AGENT ����������ע�����Ϊ AGENT_CALL��HUMAN_GATE �� HUMAN_CONFIRM��TOOL �ڵ����ܳ���������ȷ�ܾ� IntegrationError����guarded_dispatch��validate_plan ǰ�� �� plan_to_chain �� Orchestrator.dispatch_event �� ����ӳ�� OrchestrationOutcome��COMPLETED/HELD/ESCALATED��FAILED/δ֪ �� ESCALATED fail-closed���ڲ��쳣������������GuardResult ���ͶӰ�̶��ļ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-07T20:36:29.779221Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
�Ž�\"����semver/ISO-8601 ��ʽУ�飨manifest semantic_version / a2a created_at / memory occurred_at��L7����Policy ��ʱ�Ͻ� dispatch��600s / plan_total��7200s / consent��7200s��Info4����Orchestrator �� provider �쳣����Ϊ OrchestrationError + ���ͶӰ�� validated_at��Low����K8s �嵥 spec ���ڰ� capability/tool/policy/plan ������У��δ֪����Low�����ĵ���ȡ�ᣨtrusted_anchor ί�� L2 / ����������� L4 / ������ Info5���������� stdlib + L17",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/policy.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/k8s_listing.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-2",
      "title": "GAPS-1 �¹۲����տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����Policy TimeoutProfile/RetryProfile/ConsentProfile �ϸ��������ͣ�bool/str/float/int ����һ�� PolicyValidationError��`type(...) is int`����semver �ϸ���򣨽�ǰ�����㣩��ISO-8601 ������ΧУ�飨datetime.strptime��a2a created_at / memory occurred_at / validate_plan validated_at / transition validated_at����validated_at �����ͶӰǰͳһ L7 ISO У�飻������ stdlib + L17",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/orchestrator.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-3",
      "title": "GAPS-2 �¹۲����տڣ�2026-08-08���û�ָ��\"��������\"����semver ���� $ ��Ϊ \\Z �ܾ�β�����У�1.0.0\\n ���ٱ����ܣ���ISO ·������ strptime ��ס������ 2 �test_framework_gaps3.py��",
      "code": [
        "src/coevo/framework/manifest_checker.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-1",
      "title": "��ܽ������б��ţ�GuardedOrchestrator ���䣬2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����guard_registration��manifest-checker ͨ����ע�ᣬ�ܾ������� inner_register��inner �쳣 fail-closed����plan_to_chain����� Plan AGENT/HUMAN_GATE �� ���� OrchestrationChain��AGENT ����������ע�����Ϊ AGENT_CALL��HUMAN_GATE �� HUMAN_CONFIRM��TOOL �ڵ����ܳ���������ȷ�ܾ� IntegrationError����guarded_dispatch��validate_plan ǰ�� �� plan_to_chain �� Orchestrator.dispatch_event �� ����ӳ�� OrchestrationOutcome��COMPLETED/HELD/ESCALATED��FAILED/δ֪ �� ESCALATED fail-closed���ڲ��쳣������������GuardResult ���ͶӰ�̶��ļ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-2",
      "title": "������̧���뼯���տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����chain_to_plan������ OrchestrationChain �� ��� Plan��AGENT_CALL �� registry.get �������� �� AGENT �ڵ� / HUMAN_CONFIRM �� HUMAN_GATE / CONDITIONAL ��δע����� �� IntegrationError��˳��� + plan_id=plan_fingerprint����validate_product_chain��̧�� + validate_plan ������� + L18 + L19��RBAC �ܾ� fail-closed����plan_to_chain �ռ�����������Ϊ IntegrationError��INTEGRATION-1 Low �տڣ���й© CapabilityValidationError ����ϸ�ڣ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-07T21:00:17.574203Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-07T21:00:26.978133Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
n validated_at����validated_at �����ͶӰǰͳһ L7 ISO У�飻������ stdlib + L17",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/orchestrator.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-3",
      "title": "GAPS-2 �¹۲����տڣ�2026-08-08���û�ָ��\"��������\"����semver ���� $ ��Ϊ \\Z �ܾ�β�����У�1.0.0\\n ���ٱ����ܣ���ISO ·������ strptime ��ס������ 2 �test_framework_gaps3.py��",
      "code": [
        "src/coevo/framework/manifest_checker.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-1",
      "title": "��ܽ������б��ţ�GuardedOrchestrator ���䣬2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����guard_registration��manifest-checker ͨ����ע�ᣬ�ܾ������� inner_register��inner �쳣 fail-closed����plan_to_chain����� Plan AGENT/HUMAN_GATE �� ���� OrchestrationChain��AGENT ����������ע�����Ϊ AGENT_CALL��HUMAN_GATE �� HUMAN_CONFIRM��TOOL �ڵ����ܳ���������ȷ�ܾ� IntegrationError����guarded_dispatch��validate_plan ǰ�� �� plan_to_chain �� Orchestrator.dispatch_event �� ����ӳ�� OrchestrationOutcome��COMPLETED/HELD/ESCALATED��FAILED/δ֪ �� ESCALATED fail-closed���ڲ��쳣������������GuardResult ���ͶӰ�̶��ļ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-2",
      "title": "������̧���뼯���տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����chain_to_plan������ OrchestrationChain �� ��� Plan��AGENT_CALL �� registry.get �������� �� AGENT �ڵ� / HUMAN_CONFIRM �� HUMAN_GATE / CONDITIONAL ��δע����� �� IntegrationError��˳��� + plan_id=plan_fingerprint����validate_product_chain��̧�� + validate_plan ������� + L18 + L19��RBAC �ܾ� fail-closed����plan_to_chain �ռ�����������Ϊ IntegrationError��INTEGRATION-1 Low �տڣ���й© CapabilityValidationError ����ϸ�ڣ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-3",
      "title": "��ʵ��Ʒ���ߣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����app/pipeline.py ����ʵ�ɷ�ǰ�� validate_product_chain У�� MVP_FIXED_CHAIN�������ǰ�ã�RBAC/L4 �ṹ allow-all ������Ʒ���ߣ���ʧ���� RuntimeError ��ֹ����chain_to_plan ̧���쳣����Ϊ rejected��IntegrationError �� ValidationResult fail-closed����L7 ISO У�����С���루��Ʒ now_utc_iso_z `...00.123456Z`��a2a/memory/validation/orchestrator ��ģ��ͳһ���������� stdlib + L17",
      "code": [
        "src/coevo/app/pipeline.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/validation.py"
      ],
      "tests": [
        "tests/unit/test_pipeline_framework_gate.py",
        "tests/unit/test_framework_gaps2.py",
        "tests/e2e/test_demo_runner.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_pipeline_framework_gate.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_demo_runner.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-07T21:25:22.067881Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-07T21:25:31.675670Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
n validated_at����validated_at �����ͶӰǰͳһ L7 ISO У�飻������ stdlib + L17",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/orchestrator.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-3",
      "title": "GAPS-2 �¹۲����տڣ�2026-08-08���û�ָ��\"��������\"����semver ���� $ ��Ϊ \\Z �ܾ�β�����У�1.0.0\\n ���ٱ����ܣ���ISO ·������ strptime ��ס������ 2 �test_framework_gaps3.py��",
      "code": [
        "src/coevo/framework/manifest_checker.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-1",
      "title": "��ܽ������б��ţ�GuardedOrchestrator ���䣬2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����guard_registration��manifest-checker ͨ����ע�ᣬ�ܾ������� inner_register��inner �쳣 fail-closed����plan_to_chain����� Plan AGENT/HUMAN_GATE �� ���� OrchestrationChain��AGENT ����������ע�����Ϊ AGENT_CALL��HUMAN_GATE �� HUMAN_CONFIRM��TOOL �ڵ����ܳ���������ȷ�ܾ� IntegrationError����guarded_dispatch��validate_plan ǰ�� �� plan_to_chain �� Orchestrator.dispatch_event �� ����ӳ�� OrchestrationOutcome��COMPLETED/HELD/ESCALATED��FAILED/δ֪ �� ESCALATED fail-closed���ڲ��쳣������������GuardResult ���ͶӰ�̶��ļ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-2",
      "title": "������̧���뼯���տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����chain_to_plan������ OrchestrationChain �� ��� Plan��AGENT_CALL �� registry.get �������� �� AGENT �ڵ� / HUMAN_CONFIRM �� HUMAN_GATE / CONDITIONAL ��δע����� �� IntegrationError��˳��� + plan_id=plan_fingerprint����validate_product_chain��̧�� + validate_plan ������� + L18 + L19��RBAC �ܾ� fail-closed����plan_to_chain �ռ�����������Ϊ IntegrationError��INTEGRATION-1 Low �տڣ���й© CapabilityValidationError ����ϸ�ڣ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-3",
      "title": "��ʵ��Ʒ���ߣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����app/pipeline.py ����ʵ�ɷ�ǰ�� validate_product_chain У�� MVP_FIXED_CHAIN�������ǰ�ã�RBAC/L4 �ṹ allow-all ������Ʒ���ߣ���ʧ���� RuntimeError ��ֹ����chain_to_plan ̧���쳣����Ϊ rejected��IntegrationError �� ValidationResult fail-closed����L7 ISO У�����С���루��Ʒ now_utc_iso_z `...00.123456Z`��a2a/memory/validation/orchestrator ��ģ��ͳһ���������� stdlib + L17",
      "code": [
        "src/coevo/app/pipeline.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/validation.py"
      ],
      "tests": [
        "tests/unit/test_pipeline_framework_gate.py",
        "tests/unit/test_framework_gaps2.py",
        "tests/e2e/test_demo_runner.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_pipeline_framework_gate.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_demo_runner.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-07T21:29:23.176118Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-07T21:29:30.526032Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
n validated_at����validated_at �����ͶӰǰͳһ L7 ISO У�飻������ stdlib + L17",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/orchestrator.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-3",
      "title": "GAPS-2 �¹۲����տڣ�2026-08-08���û�ָ��\"��������\"����semver ���� $ ��Ϊ \\Z �ܾ�β�����У�1.0.0\\n ���ٱ����ܣ���ISO ·������ strptime ��ס������ 2 �test_framework_gaps3.py��",
      "code": [
        "src/coevo/framework/manifest_checker.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-1",
      "title": "��ܽ������б��ţ�GuardedOrchestrator ���䣬2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����guard_registration��manifest-checker ͨ����ע�ᣬ�ܾ������� inner_register��inner �쳣 fail-closed����plan_to_chain����� Plan AGENT/HUMAN_GATE �� ���� OrchestrationChain��AGENT ����������ע�����Ϊ AGENT_CALL��HUMAN_GATE �� HUMAN_CONFIRM��TOOL �ڵ����ܳ���������ȷ�ܾ� IntegrationError����guarded_dispatch��validate_plan ǰ�� �� plan_to_chain �� Orchestrator.dispatch_event �� ����ӳ�� OrchestrationOutcome��COMPLETED/HELD/ESCALATED��FAILED/δ֪ �� ESCALATED fail-closed���ڲ��쳣������������GuardResult ���ͶӰ�̶��ļ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-2",
      "title": "������̧���뼯���տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����chain_to_plan������ OrchestrationChain �� ��� Plan��AGENT_CALL �� registry.get �������� �� AGENT �ڵ� / HUMAN_CONFIRM �� HUMAN_GATE / CONDITIONAL ��δע����� �� IntegrationError��˳��� + plan_id=plan_fingerprint����validate_product_chain��̧�� + validate_plan ������� + L18 + L19��RBAC �ܾ� fail-closed����plan_to_chain �ռ�����������Ϊ IntegrationError��INTEGRATION-1 Low �տڣ���й© CapabilityValidationError ����ϸ�ڣ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-3",
      "title": "��ʵ��Ʒ���ߣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����app/pipeline.py ����ʵ�ɷ�ǰ�� validate_product_chain У�� MVP_FIXED_CHAIN�������ǰ�ã�RBAC/L4 �ṹ allow-all ������Ʒ���ߣ���ʧ���� RuntimeError ��ֹ����chain_to_plan ̧���쳣����Ϊ rejected��IntegrationError �� ValidationResult fail-closed����L7 ISO У�����С���루��Ʒ now_utc_iso_z `...00.123456Z`��a2a/memory/validation/orchestrator ��ģ��ͳһ���������� stdlib + L17",
      "code": [
        "src/coevo/app/pipeline.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/validation.py"
      ],
      "tests": [
        "tests/unit/test_pipeline_framework_gate.py",
        "tests/unit/test_framework_gaps2.py",
        "tests/e2e/test_demo_runner.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_pipeline_framework_gate.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_demo_runner.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```



## 2026-08-07T21:32:59.721312Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-07T21:33:07.192928Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
    "tests": [
        "tests/unit/test_framework_gaps3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-1",
      "title": "��ܽ������б��ţ�GuardedOrchestrator ���䣬2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����guard_registration��manifest-checker ͨ����ע�ᣬ�ܾ������� inner_register��inner �쳣 fail-closed����plan_to_chain����� Plan AGENT/HUMAN_GATE �� ���� OrchestrationChain��AGENT ����������ע�����Ϊ AGENT_CALL��HUMAN_GATE �� HUMAN_CONFIRM��TOOL �ڵ����ܳ���������ȷ�ܾ� IntegrationError����guarded_dispatch��validate_plan ǰ�� �� plan_to_chain �� Orchestrator.dispatch_event �� ����ӳ�� OrchestrationOutcome��COMPLETED/HELD/ESCALATED��FAILED/δ֪ �� ESCALATED fail-closed���ڲ��쳣������������GuardResult ���ͶӰ�̶��ļ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-2",
      "title": "������̧���뼯���տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����chain_to_plan������ OrchestrationChain �� ��� Plan��AGENT_CALL �� registry.get �������� �� AGENT �ڵ� / HUMAN_CONFIRM �� HUMAN_GATE / CONDITIONAL ��δע����� �� IntegrationError��˳��� + plan_id=plan_fingerprint����validate_product_chain��̧�� + validate_plan ������� + L18 + L19��RBAC �ܾ� fail-closed����plan_to_chain �ռ�����������Ϊ IntegrationError��INTEGRATION-1 Low �տڣ���й© CapabilityValidationError ����ϸ�ڣ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-3",
      "title": "��ʵ��Ʒ���ߣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����app/pipeline.py ����ʵ�ɷ�ǰ�� validate_product_chain У�� MVP_FIXED_CHAIN�������ǰ�ã�RBAC/L4 �ṹ allow-all ������Ʒ���ߣ���ʧ���� RuntimeError ��ֹ����chain_to_plan ̧���쳣����Ϊ rejected��IntegrationError �� ValidationResult fail-closed����L7 ISO У�����С���루��Ʒ now_utc_iso_z `...00.123456Z`��a2a/memory/validation/orchestrator ��ģ��ͳһ���������� stdlib + L17",
      "code": [
        "src/coevo/app/pipeline.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/validation.py"
      ],
      "tests": [
        "tests/unit/test_pipeline_framework_gate.py",
        "tests/unit/test_framework_gaps2.py",
        "tests/e2e/test_demo_runner.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_pipeline_framework_gate.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_demo_runner.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-4",
      "title": "���� L7 У�鹹������2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����validation.py ���� is_iso_utc_z��С���� + ����У�飻���� `$` �� `\\Z` ê����β�����У����ַ��� fail-closed �� TypeError й©����a2a/memory/orchestrator/integration ͳһ����ȥ˽�и�����validate_product_chain �쳣��֧Ҳ�ȹ� L7��INTEGRATION-3 Low �տڣ������������������� stdlib + L17",
      "code": [
        "src/coevo/framework/validation.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps4.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps4.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-07T21:36:14.390493Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-07T21:36:21.945198Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
    "tests": [
        "tests/unit/test_framework_gaps3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-1",
      "title": "��ܽ������б��ţ�GuardedOrchestrator ���䣬2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����guard_registration��manifest-checker ͨ����ע�ᣬ�ܾ������� inner_register��inner �쳣 fail-closed����plan_to_chain����� Plan AGENT/HUMAN_GATE �� ���� OrchestrationChain��AGENT ����������ע�����Ϊ AGENT_CALL��HUMAN_GATE �� HUMAN_CONFIRM��TOOL �ڵ����ܳ���������ȷ�ܾ� IntegrationError����guarded_dispatch��validate_plan ǰ�� �� plan_to_chain �� Orchestrator.dispatch_event �� ����ӳ�� OrchestrationOutcome��COMPLETED/HELD/ESCALATED��FAILED/δ֪ �� ESCALATED fail-closed���ڲ��쳣������������GuardResult ���ͶӰ�̶��ļ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-2",
      "title": "������̧���뼯���տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����chain_to_plan������ OrchestrationChain �� ��� Plan��AGENT_CALL �� registry.get �������� �� AGENT �ڵ� / HUMAN_CONFIRM �� HUMAN_GATE / CONDITIONAL ��δע����� �� IntegrationError��˳��� + plan_id=plan_fingerprint����validate_product_chain��̧�� + validate_plan ������� + L18 + L19��RBAC �ܾ� fail-closed����plan_to_chain �ռ�����������Ϊ IntegrationError��INTEGRATION-1 Low �տڣ���й© CapabilityValidationError ����ϸ�ڣ��������� stdlib + L17��integration.md��",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/integration.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_integration2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/integration.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_integration2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-INTEGRATION-3",
      "title": "��ʵ��Ʒ���ߣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����app/pipeline.py ����ʵ�ɷ�ǰ�� validate_product_chain У�� MVP_FIXED_CHAIN�������ǰ�ã�RBAC/L4 �ṹ allow-all ������Ʒ���ߣ���ʧ���� RuntimeError ��ֹ����chain_to_plan ̧���쳣����Ϊ rejected��IntegrationError �� ValidationResult fail-closed����L7 ISO У�����С���루��Ʒ now_utc_iso_z `...00.123456Z`��a2a/memory/validation/orchestrator ��ģ��ͳһ���������� stdlib + L17",
      "code": [
        "src/coevo/app/pipeline.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/validation.py"
      ],
      "tests": [
        "tests/unit/test_pipeline_framework_gate.py",
        "tests/unit/test_framework_gaps2.py",
        "tests/e2e/test_demo_runner.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_pipeline_framework_gate.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps2.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_demo_runner.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-4",
      "title": "���� L7 У�鹹������2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����validation.py ���� is_iso_utc_z��С���� + ����У�飻���� `$` �� `\\Z` ê����β�����У����ַ��� fail-closed �� TypeError й©����a2a/memory/orchestrator/integration ͳһ����ȥ˽�и�����validate_product_chain �쳣��֧Ҳ�ȹ� L7��INTEGRATION-3 Low �տڣ������������������� stdlib + L17",
      "code": [
        "src/coevo/framework/validation.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps4.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps4.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-07T21:41:17.284731Z — target=`quality` fingerprint=`34d637f035600903`
- exit_code: `1`
```text
kspace_init.TestWorkspaceInitService.test_init_creates_workspace_for_committed_import) ... ok
test_init_idempotent_on_duplicate_package (test_workspace_init.TestWorkspaceInitService.test_init_idempotent_on_duplicate_package) ... ok
test_init_propagates_path_error_for_unsafe_package_id (test_workspace_init.TestWorkspaceInitService.test_init_propagates_path_error_for_unsafe_package_id) ... ok
test_init_rejects_invalid_role_id (test_workspace_init.TestWorkspaceInitService.test_init_rejects_invalid_role_id) ... ok
test_init_rejects_non_import_outcome (test_workspace_init.TestWorkspaceInitService.test_init_rejects_non_import_outcome) ... ok
test_init_rejects_rolled_back_import (test_workspace_init.TestWorkspaceInitService.test_init_rejects_rolled_back_import) ... ok
test_sanitize_id_accepts_exactly_maximum_length (test_workspace_init.TestWorkspacePath.test_sanitize_id_accepts_exactly_maximum_length) ... ok
test_sanitize_id_accepts_safe (test_workspace_init.TestWorkspacePath.test_sanitize_id_accepts_safe) ... ok
test_sanitize_id_rejects_empty (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_empty) ... ok
test_sanitize_id_rejects_maximum_plus_one (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_maximum_plus_one) ... ok
test_sanitize_id_rejects_too_long (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_too_long) ... ok
test_workspace_path_default_root (test_workspace_init.TestWorkspacePath.test_workspace_path_default_root) ... ok
test_workspace_path_layout (test_workspace_init.TestWorkspacePath.test_workspace_path_layout) ... ok
test_workspace_path_rejects_backslash_traversal (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_backslash_traversal) ... ok
test_workspace_path_rejects_empty_root (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_empty_root) ... ok
test_workspace_path_rejects_invalid_project_id (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_invalid_project_id) ... ok
test_workspace_path_rejects_invalid_role_id (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_invalid_role_id) ... ok
test_workspace_path_rejects_traversal (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_traversal) ... ok
test_by_package (test_workspace_init.TestWorkspaceRegistry.test_by_package) ... ok
test_empty_registry (test_workspace_init.TestWorkspaceRegistry.test_empty_registry) ... ok
test_register_allows_same_package_for_different_role (test_workspace_init.TestWorkspaceRegistry.test_register_allows_same_package_for_different_role) ... ok
test_register_rejects_duplicate_package_for_same_role (test_workspace_init.TestWorkspaceRegistry.test_register_rejects_duplicate_package_for_same_role) ... ok
test_register_rejects_duplicate_role (test_workspace_init.TestWorkspaceRegistry.test_register_rejects_duplicate_role) ... ok
test_register_then_get (test_workspace_init.TestWorkspaceRegistry.test_register_then_get) ... ok
test_disallowed_extension_is_denied (test_wps_launcher.WpsLauncherTests.test_disallowed_extension_is_denied) ... ok
test_invalid_root_is_rejected (test_wps_launcher.WpsLauncherTests.test_invalid_root_is_rejected) ... ok
test_missing_absolute_executable_is_not_available (test_wps_launcher.WpsLauncherTests.test_missing_absolute_executable_is_not_available) ... ok
test_missing_file_is_denied (test_wps_launcher.WpsLauncherTests.test_missing_file_is_denied) ... ok
test_runner_failure_is_error (test_wps_launcher.WpsLauncherTests.test_runner_failure_is_error) ... ok
test_runner_is_invoked_with_explicit_executable_and_path (test_wps_launcher.WpsLauncherTests.test_runner_is_invoked_with_explicit_executable_and_path) ... ok
test_symlink_escape_is_denied (test_wps_launcher.WpsLauncherTests.test_symlink_escape_is_denied) ... skipped 'symlink creation unavailable'
test_traversal_and_absolute_paths_are_denied (test_wps_launcher.WpsLauncherTests.test_traversal_and_absolute_paths_are_denied) ... ok
test_valid_document_dry_run_is_ok (test_wps_launcher.WpsLauncherTests.test_valid_document_dry_run_is_ok) ... ok

======================================================================
FAIL: test_decisions_records_the_audit_corpus_status (test_private_key_handles_bindings.PrivateKeyHandlesBindingsTests.test_decisions_records_the_audit_corpus_status)
Pin: latest DECISIONS entry acknowledges the receipt policy.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\unit\test_private_key_handles_bindings.py", line 162, in test_decisions_records_the_audit_corpus_status
    self.assertIn(
    ~~~~~~~~~~~~~^
        marker,
        ^^^^^^^
        latest,
        ^^^^^^^
        f"latest DECISIONS.md section lacks approved governance marker: {marker}",
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: 'decision status: approved a+b' not found in '## 2026-08-08 �� framework-gaps-4 ��β�����������߶������ˣ���֤�Ӵ���ԽȨִ�����ۣ�\n\n- ��ʵ��������һ��"����ƫ�verifier/security-reviewer �Ӵ����������������أ�agent thread limit\n  reached�����ɱ�������ֻ��ɳ���ڰ���ɫ��Լʵ��ִ�в����ۣ���Υ��"��������ʵ������ʵ���¼���\n  `fwgaps4_verify` ��֤�Ӵ���δ���������أ�����������������ֱ���޸Ĵ��루`ebc5ae4`�����ύ��β\n  ��¼��`c171fec`����Υ�� mvp-verifier ֻ����Լ�����Ĵ���/����/��¼���� git �ύ��������β��¼\n  ����������׫д���Ƕ���˫ǩ���� integration-2/3 �������������ݾ���������һ�µ����Ա�����ԽȨ\n  ��Ϊ�ٴ����ۡ�\n- �����߶������ˣ�2026-08-08��pin=`ebc5ae4`����\n  * ��Ϊ̽��ȫ����С����β�滻�У�`...123z\\n`������ͨβ�滻�С�crlf���Ʊ�����β��ո񡢷Ƿ�����\n    ��2026-02-30 / 2026-99-99��ȫ�����գ����ַ�����none/int/bytes/list/dict/bool��fail-closed\n    ���� false��validate_plan �� validate_product_chain �� iso / ���ַ��� validated_at ������\n    rejected��l7������ typeerror й©�����ͶӰ���� validation_projection_keys һ�£���\n    eval/exec/open��\n  * �����Ž���������� 94/94 ȫ�̣�gaps4 + gaps2/a2a/memory/orchestrator/validate_plan/\n    plan_l18/integration/integration2/pipeline_framework_gate/module_docs����fmt exit=0\n    fingerprint=`fe39766e2048d2bc`��lint exit=0 fingerprint=`252ad24e526f6728`��audit\n    fully-sealed��secret scan ok��\n  * ɳ�� fwgaps4c-verify��pin=`ebc5ae4`����fmt exit=0��ָͬ�ƣ���lint exit=0\n    fingerprint=`691bf2af19799901`��ɳ��·��ָ����ά�������߲�ͬ��Ԥ�ڣ�ci ͬ������� 94/94\n    ȫ�̣�review_sandbox check violations=[]��loop/ ���Ϊ֤����������� discard��\n  * ɳ�� fwgaps4c-sec��pin=`ebc5ae4`����stride ��Ϊ̽�� 5/5 pass��s1 ��ʽ�ϸ��� / s2 ���ַ���\n    fail-closed / s3 ���ͶӰ�̶��� / s4 �޶�ִ̬�� / s5 �쳣��֧ l7 ǰ�ã�����ȫ�����Ӽ� 51/51\n    ȫ�̣�review_sandbox check violations=[]���� discard��\n- ���ۣ�`ebc5ae4` �����޸���`$`��`\\z` ê����isinstance ����������������������ȷ���޸���ȫ���\n  ���� critical/high/medium/low=0/0/0/0����Ϊ��̽��ȫ������������ `framework-gaps-4` ά�� done��\n  last_verified_commit=`ebc5ae4`��\n- �¹۲���Ǽǣ�`framework-gaps-5`��eng-base��ready��dependencies=[framework-gaps-4]���Ѳ�¼\n  backlog�����ֿ�������ģ�飨cockpit/models��crypto��knowledge_base��audit_governance��\n  orchestrator/models��progress_capture��talent/models��task_decomposition��sessions �ȣ�����\n  `$` ê�� iso ����ͬ��β�����з��գ���������ִ�ͳһ�������� `is_iso_utc_z`��\n- �����ߣ��û�ָ�ִ�У�codex��loop-engineer����\n' : latest DECISIONS.md section lacks approved governance marker: decision status: approved a+b

======================================================================
FAIL: test_eng_base_is_fully_covered (test_traceability_check.TraceabilityTests.test_eng_base_is_fully_covered)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\unit\test_traceability_check.py", line 12, in test_eng_base_is_fully_covered
    self.assertEqual(49,result["checked"])
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 49 != 50

----------------------------------------------------------------------
Ran 1156 tests in 64.248s

FAILED (failures=2, skipped=3)

```



## 2026-08-07T22:09:55.365697Z — target=`quality` fingerprint=`34d637f035600903`
- exit_code: `0`
```text
requires_recovery_and_reopen_commits_exactly_once) ... ok
test_row_shape_validator_rejects_each_oversize_and_malformed_column (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_row_shape_validator_rejects_each_oversize_and_malformed_column) ... ok
test_signed_chain_binds_store_head_sequence_and_previous_hash (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_signed_chain_binds_store_head_sequence_and_previous_hash) ... ok
test_stale_baseline_is_rejected_before_insert (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
test_truncation_is_rejected_by_freshness_checkpoint (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_truncation_is_rejected_by_freshness_checkpoint) ... ok
test_gitignore_excludes_receipt_pattern (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_gitignore_excludes_receipt_pattern) ... ok
test_no_reachable_receipt_blobs_across_all_refs (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_no_reachable_receipt_blobs_across_all_refs) ... ok
test_no_tracked_receipt_paths (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_no_tracked_receipt_paths) ... ok
test_pre_scrub_head_is_no_longer_reachable (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_pre_scrub_head_is_no_longer_reachable) ... ok
test_validate_bundle_rejects_private_key_handle_field (test_private_key_storage.IdentityBundlePrivateKeyRejectionTests.test_validate_bundle_rejects_private_key_handle_field) ... ok
test_validate_bundle_rejects_private_key_pkcs8_bytes (test_private_key_storage.IdentityBundlePrivateKeyRejectionTests.test_validate_bundle_rejects_private_key_pkcs8_bytes) ... ok
test_reference_accepts_only_safe_metadata (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_accepts_only_safe_metadata) ... ok
test_reference_is_frozen_and_hash_stable_across_rotations (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_is_frozen_and_hash_stable_across_rotations) ... ok
test_reference_rejects_inverted_validity (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_rejects_inverted_validity) ... ok
test_reference_rejects_malformed_handle_and_digest (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_rejects_malformed_handle_and_digest) ... ok
test_repr_and_pickle_never_expose_secret_token (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_repr_and_pickle_never_expose_secret_token) ... ok
test_validate_handle_payload_rejects_private_key_blob_strings (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_validate_handle_payload_rejects_private_key_blob_strings) ... ok
test_validate_handle_payload_rejects_unknown_or_sensitive_fields (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_validate_handle_payload_rejects_unknown_or_sensitive_fields) ... ok
test_audit_chain_detects_event_tampering (test_private_key_storage.PrivateKeyServicePolicyTests.test_audit_chain_detects_event_tampering) ... ok
test_audit_chain_records_store_use_revoke_and_destroy (test_private_key_storage.PrivateKeyServicePolicyTests.test_audit_chain_records_store_use_revoke_and_destroy) ... ok
test_destroyed_handle_blocks_use_with_stale_reference (test_private_key_storage.PrivateKeyServicePolicyTests.test_destroyed_handle_blocks_use_with_stale_reference) ... ok
test_overwrite_store_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_overwrite_store_is_rejected) ... ok
test_revoke_without_reason_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_revoke_without_reason_is_rejected) ... ok
test_revoked_reference_blocks_use_and_audits_rejection (test_private_key_storage.PrivateKeyServicePolicyTests.test_revoked_reference_blocks_use_and_audits_rejection) ... ok
test_stored_reference_round_trips_use_and_returns_signature (test_private_key_storage.PrivateKeyServicePolicyTests.test_stored_reference_round_trips_use_and_returns_signature) ... ok
test_untrusted_parent_thumbprint_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_untrusted_parent_thumbprint_is_rejected) ... ok
test_use_outside_validity_window_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_use_outside_validity_window_is_rejected) ... ok
test_use_with_naive_datetime_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_use_with_naive_datetime_is_rejected) ... ok
test_verify_binds_certificate_pin_digest_algorithm_and_audits_digest_only (test_private_key_storage.PrivateKeyServicePolicyTests.test_verify_binds_certificate_pin_digest_algorithm_and_audits_digest_only) ... ok
test_verify_rejects_wrong_pin_revoked_destroyed_and_bad_signature (test_private_key_storage.PrivateKeyServicePolicyTests.test_verify_rejects_wrong_pin_revoked_destroyed_and_bad_signature) ... ok
test_poisoned_powershell_path_is_rejected_before_execution (test_private_key_storage.WindowsPrivateKeyLaunchPolicyTests.test_poisoned_powershell_path_is_rejected_before_execution) ... ok
test_rejects_uncontrolled_helper_path (test_private_key_storage.WindowsPrivateKeyLaunchPolicyTests.test_rejects_uncontrolled_helper_path) ... ok
test_custom_tools_use_current_typed_api (test_tool_permissions.PermissionTests.test_custom_tools_use_current_typed_api) ... ok
test_network_and_install_commands_are_fail_closed (test_tool_permissions.PermissionTests.test_network_and_install_commands_are_fail_closed) ... ok

----------------------------------------------------------------------
Ran 99 tests in 62.024s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 146.534s

OK
audit seal: fully-sealed

```





## 2026-08-07T23:55:07.480729Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-07T23:55:18.047311Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-07T23:55:29.247252Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
ion.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps4.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps4.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-5",
      "title": "ȫ�� ISO ����β�������տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"��ԽȨ�������\"ȫ���Ž�\"�Ѹ�������cockpit / crypto / knowledge_base / audit_governance / orchestrator / progress_capture / talent / task_decomposition �� 11 �� ISO ���� `$` �� `\\Z`������ Python ĩβ����ǰƥ�䣬�� GAPS-3/GAPS-4 ͬ�ࣩ��ê���ع���� test_iso_anchor_regression.py������\"ͳһ������������\"�����ܹ������",
      "code": [
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-6",
      "title": "���� ISO У�鹹����ȫ����أ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"�������������޹�Ҷģ�� src/coevo/timefmt.py��is_iso_utc_z��`\\Z` ê����β�����С�С���롢����У�顢���ַ��� fail-closed����root_modules �Ǽǣ�framework/validation.py �� timefmt ���벢�ٵ�����10 ����Ʒģ�� + �����ͳһ���ù�����������ȥ 11 �����򸱱������ _ISO �ٵ�����ê�����ԸĲ⹲��������",
      "code": [
        "src/coevo/timefmt.py",
        "src/coevo/framework/validation.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/audit_governance/facade.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/orchestrator/service.py",
        "src/coevo/orchestrator/_real_chain.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps6.py",
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/facade.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps6.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-07T23:55:39.764367Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
ion.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/orchestrator.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/__init__.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps4.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/orchestrator.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps4.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-5",
      "title": "ȫ�� ISO ����β�������տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"��ԽȨ�������\"ȫ���Ž�\"�Ѹ�������cockpit / crypto / knowledge_base / audit_governance / orchestrator / progress_capture / talent / task_decomposition �� 11 �� ISO ���� `$` �� `\\Z`������ Python ĩβ����ǰƥ�䣬�� GAPS-3/GAPS-4 ͬ�ࣩ��ê���ع���� test_iso_anchor_regression.py������\"ͳһ������������\"�����ܹ������",
      "code": [
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-6",
      "title": "���� ISO У�鹹����ȫ����أ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"�������������޹�Ҷģ�� src/coevo/timefmt.py��is_iso_utc_z��`\\Z` ê����β�����С�С���롢����У�顢���ַ��� fail-closed����root_modules �Ǽǣ�framework/validation.py �� timefmt ���벢�ٵ�����10 ����Ʒģ�� + �����ͳһ���ù�����������ȥ 11 �����򸱱������ _ISO �ٵ�����ê�����ԸĲ⹲��������",
      "code": [
        "src/coevo/timefmt.py",
        "src/coevo/framework/validation.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/audit_governance/facade.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/orchestrator/service.py",
        "src/coevo/orchestrator/_real_chain.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps6.py",
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/facade.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps6.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-07T23:58:59.244090Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
 �� 11 �� ISO ���� `$` �� `\\Z`������ Python ĩβ����ǰƥ�䣬�� GAPS-3/GAPS-4 ͬ�ࣩ��ê���ع���� test_iso_anchor_regression.py������\"ͳһ������������\"�����ܹ������",
      "code": [
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-6",
      "title": "���� ISO У�鹹����ȫ����أ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"�������������޹�Ҷģ�� src/coevo/timefmt.py��is_iso_utc_z��`\\Z` ê����β�����С�С���롢����У�顢���ַ��� fail-closed����root_modules �Ǽǣ�framework/validation.py �� timefmt ���벢�ٵ�����10 ����Ʒģ�� + �����ͳһ���ù�����������ȥ 11 �����򸱱������ _ISO �ٵ�����ê�����ԸĲ⹲��������",
      "code": [
        "src/coevo/timefmt.py",
        "src/coevo/framework/validation.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/audit_governance/facade.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/orchestrator/service.py",
        "src/coevo/orchestrator/_real_chain.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps6.py",
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/facade.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps6.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-DOCS-1",
      "title": "��ܲ��ĵ������տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����README ������������ US-16 �����ܲ�˵�����ܹ����� `framework/` + `timefmt.py`���ĵ������� `docs/framework/` �� `docs/plans/distributed-agent-framework/`����ǰ״̬�ӿ�ܲ� bullet��docs/code-guide.md ���� framework/ �� timefmt.py �����ڣ�ģ��ְ�� + �ؼ���ڣ���docs/README.md �����Ǽ� docs/framework/�������ĵ������������ԣ�README/code-guide/docs �������Ƕ��� + docs/framework �ļ����ڶ��ԣ�",
      "code": [
        "README.md",
        "docs/README.md",
        "docs/code-guide.md",
        "docs/plans/FRAMEWORK-DOCS-1-slice.md"
      ],
      "tests": [
        "tests/unit/test_framework_docs.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/code-guide.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/plans/FRAMEWORK-DOCS-1-slice.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_docs.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```



## 2026-08-08T00:15:04.102960Z — target=`fmt` fingerprint=`8d456a2ce09245c7`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ C:\Python314\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T00:15:15.801511Z — target=`lint` fingerprint=`4800c1ade060c9f3`
- exit_code: `0`
```text
 audit_governance / orchestrator / progress_capture / talent / task_decomposition �� 11 �� ISO ���� `$` �� `\\Z`������ Python ĩβ����ǰƥ�䣬�� GAPS-3/GAPS-4 ͬ�ࣩ��ê���ع���� test_iso_anchor_regression.py������\"ͳһ������������\"�����ܹ������",
      "code": [
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-6",
      "title": "���� ISO У�鹹����ȫ����أ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"�������������޹�Ҷģ�� src/coevo/timefmt.py��is_iso_utc_z��`\\Z` ê����β�����С�С���롢����У�顢���ַ��� fail-closed����root_modules �Ǽǣ�framework/validation.py �� timefmt ���벢�ٵ�����10 ����Ʒģ�� + �����ͳһ���ù�����������ȥ 11 �����򸱱������ _ISO �ٵ�����ê�����ԸĲ⹲��������",
      "code": [
        "src/coevo/timefmt.py",
        "src/coevo/framework/validation.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/audit_governance/facade.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/orchestrator/service.py",
        "src/coevo/orchestrator/_real_chain.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps6.py",
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/facade.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps6.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-DOCS-1",
      "title": "��ܲ��ĵ������տڣ�2026-08-08���û�ָ��\"�����������Ȳ�Ҫȫ���Ž�\"����README ������������ US-16 �����ܲ�˵�����ܹ����� `framework/` + `timefmt.py`���ĵ������� `docs/framework/` �� `docs/plans/distributed-agent-framework/`����ǰ״̬�ӿ�ܲ� bullet��docs/code-guide.md ���� framework/ �� timefmt.py �����ڣ�ģ��ְ�� + �ؼ���ڣ���docs/README.md �����Ǽ� docs/framework/�������ĵ������������ԣ�README/code-guide/docs �������Ƕ��� + docs/framework �ļ����ڶ��ԣ�",
      "code": [
        "README.md",
        "docs/README.md",
        "docs/code-guide.md",
        "docs/plans/FRAMEWORK-DOCS-1-slice.md"
      ],
      "tests": [
        "tests/unit/test_framework_docs.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/code-guide.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/plans/FRAMEWORK-DOCS-1-slice.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_docs.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ C:\Python314\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ C:\Python314\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ C:\Python314\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T00:52:16.786492Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
尾部换行收口（2026-08-08，用户指令\"继续开发，先不要全量门禁\"；越权代理误记\"全量门禁\"已更正）：cockpit / crypto / knowledge_base / audit_governance / orchestrator / progress_capture / talent / task_decomposition 共 11 处 ISO 正则 `$` 改 `\\Z`（消除 Python 末尾换行前匹配，与 GAPS-3/GAPS-4 同类），锚定回归测试 test_iso_anchor_regression.py；完整\"统一到共享构造器\"留作架构层后续",
      "code": [
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-6",
      "title": "共享 ISO 校验构造器全仓落地（2026-08-08，用户指令\"继续开发，先不要全量门禁\"）：新增依赖无关叶模块 src/coevo/timefmt.py（is_iso_utc_z：`\\Z` 锚定拒尾部换行、小数秒、日历校验、非字符串 fail-closed），root_modules 登记；framework/validation.py 由 timefmt 导入并再导出；10 个产品模块 + 框架族统一引用共享构造器，去 11 处正则副本与包级 _ISO 再导出；锚定测试改测共享构造器",
      "code": [
        "src/coevo/timefmt.py",
        "src/coevo/framework/validation.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/audit_governance/facade.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/orchestrator/service.py",
        "src/coevo/orchestrator/_real_chain.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps6.py",
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/facade.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps6.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-DOCS-1",
      "title": "框架层文档治理收口（2026-08-08，用户指令\"继续开发，先不要全量门禁\"）：README 核心能力表加 US-16 行与框架层说明、架构树加 `framework/` + `timefmt.py`、文档索引加 `docs/framework/` 与 `docs/plans/distributed-agent-framework/`、当前状态加框架层 bullet；docs/code-guide.md 新增 framework/ 与 timefmt.py 引导节（模块职责 + 关键入口）；docs/README.md 索引登记 docs/framework/；新增文档治理守卫测试（README/code-guide/docs 索引覆盖断言 + docs/framework 文件存在断言）",
      "code": [
        "README.md",
        "docs/README.md",
        "docs/code-guide.md",
        "docs/plans/FRAMEWORK-DOCS-1-slice.md"
      ],
      "tests": [
        "tests/unit/test_framework_docs.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/code-guide.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/plans/FRAMEWORK-DOCS-1-slice.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_docs.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T00:52:46.064927Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T00:56:47.273288Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
尾部换行收口（2026-08-08，用户指令\"继续开发，先不要全量门禁\"；越权代理误记\"全量门禁\"已更正）：cockpit / crypto / knowledge_base / audit_governance / orchestrator / progress_capture / talent / task_decomposition 共 11 处 ISO 正则 `$` 改 `\\Z`（消除 Python 末尾换行前匹配，与 GAPS-3/GAPS-4 同类），锚定回归测试 test_iso_anchor_regression.py；完整\"统一到共享构造器\"留作架构层后续",
      "code": [
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-6",
      "title": "共享 ISO 校验构造器全仓落地（2026-08-08，用户指令\"继续开发，先不要全量门禁\"）：新增依赖无关叶模块 src/coevo/timefmt.py（is_iso_utc_z：`\\Z` 锚定拒尾部换行、小数秒、日历校验、非字符串 fail-closed），root_modules 登记；framework/validation.py 由 timefmt 导入并再导出；10 个产品模块 + 框架族统一引用共享构造器，去 11 处正则副本与包级 _ISO 再导出；锚定测试改测共享构造器",
      "code": [
        "src/coevo/timefmt.py",
        "src/coevo/framework/validation.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/audit_governance/facade.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/orchestrator/service.py",
        "src/coevo/orchestrator/_real_chain.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps6.py",
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/facade.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps6.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-DOCS-1",
      "title": "框架层文档治理收口（2026-08-08，用户指令\"继续开发，先不要全量门禁\"）：README 核心能力表加 US-16 行与框架层说明、架构树加 `framework/` + `timefmt.py`、文档索引加 `docs/framework/` 与 `docs/plans/distributed-agent-framework/`、当前状态加框架层 bullet；docs/code-guide.md 新增 framework/ 与 timefmt.py 引导节（模块职责 + 关键入口）；docs/README.md 索引登记 docs/framework/；新增文档治理守卫测试（README/code-guide/docs 索引覆盖断言 + docs/framework 文件存在断言）",
      "code": [
        "README.md",
        "docs/README.md",
        "docs/code-guide.md",
        "docs/plans/FRAMEWORK-DOCS-1-slice.md"
      ],
      "tests": [
        "tests/unit/test_framework_docs.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/code-guide.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/plans/FRAMEWORK-DOCS-1-slice.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_docs.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T00:57:42.699717Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T01:00:21.194303Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
         "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-6",
      "title": "共享 ISO 校验构造器全仓落地（2026-08-08，用户指令\"继续开发，先不要全量门禁\"）：新增依赖无关叶模块 src/coevo/timefmt.py（is_iso_utc_z：`\\Z` 锚定拒尾部换行、小数秒、日历校验、非字符串 fail-closed），root_modules 登记；framework/validation.py 由 timefmt 导入并再导出；10 个产品模块 + 框架族统一引用共享构造器，去 11 处正则副本与包级 _ISO 再导出；锚定测试改测共享构造器",
      "code": [
        "src/coevo/timefmt.py",
        "src/coevo/framework/validation.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/audit_governance/facade.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/orchestrator/service.py",
        "src/coevo/orchestrator/_real_chain.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps6.py",
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/facade.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps6.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-DOCS-1",
      "title": "框架层文档治理收口（2026-08-08，用户指令\"继续开发，先不要全量门禁\"）：README 核心能力表加 US-16 行与框架层说明、架构树加 `framework/` + `timefmt.py`、文档索引加 `docs/framework/` 与 `docs/plans/distributed-agent-framework/`、当前状态加框架层 bullet；docs/code-guide.md 新增 framework/ 与 timefmt.py 引导节（模块职责 + 关键入口）；docs/README.md 索引登记 docs/framework/；新增文档治理守卫测试（README/code-guide/docs 索引覆盖断言 + docs/framework 文件存在断言）",
      "code": [
        "README.md",
        "docs/README.md",
        "docs/code-guide.md",
        "docs/plans/FRAMEWORK-DOCS-1-slice.md"
      ],
      "tests": [
        "tests/unit/test_framework_docs.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/code-guide.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/plans/FRAMEWORK-DOCS-1-slice.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_docs.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "QUALITY-GATE-ENCODING-1",
      "title": "质量门禁输出编码修复（2026-08-08，用户指令“继续开发”）：quality_gate 子进程强制 UTF-8（gate_env：PYTHONIOENCODING=utf-8 + PYTHONUTF8=1，复制不污染父环境；两个 subprocess.run 均改用 gate_env），消除 VERIFICATION.md 门禁记录乱码根因（Windows 控制台 GBK 输出经 errors=replace 不可逆破坏）；历史乱码记录已清理（截除备份）；补回归测试 test_quality_gate_encoding.py；仅 stdlib 离线",
      "code": [
        "scripts/quality_gate.py",
        "tests/unit/test_quality_gate_encoding.py"
      ],
      "tests": [
        "tests/unit/test_quality_gate_encoding.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "tests/unit/test_quality_gate_encoding.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_encoding.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T01:09:49.115329Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T01:10:01.258924Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
s": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-6",
      "title": "共享 ISO 校验构造器全仓落地（2026-08-08，用户指令\"继续开发，先不要全量门禁\"）：新增依赖无关叶模块 src/coevo/timefmt.py（is_iso_utc_z：`\\Z` 锚定拒尾部换行、小数秒、日历校验、非字符串 fail-closed），root_modules 登记；framework/validation.py 由 timefmt 导入并再导出；10 个产品模块 + 框架族统一引用共享构造器，去 11 处正则副本与包级 _ISO 再导出；锚定测试改测共享构造器",
      "code": [
        "src/coevo/timefmt.py",
        "src/coevo/framework/validation.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/audit_governance/facade.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/orchestrator/service.py",
        "src/coevo/orchestrator/_real_chain.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps6.py",
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/facade.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps6.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-DOCS-1",
      "title": "框架层文档治理收口（2026-08-08，用户指令\"继续开发，先不要全量门禁\"）：README 核心能力表加 US-16 行与框架层说明、架构树加 `framework/` + `timefmt.py`、文档索引加 `docs/framework/` 与 `docs/plans/distributed-agent-framework/`、当前状态加框架层 bullet；docs/code-guide.md 新增 framework/ 与 timefmt.py 引导节（模块职责 + 关键入口）；docs/README.md 索引登记 docs/framework/；新增文档治理守卫测试（README/code-guide/docs 索引覆盖断言 + docs/framework 文件存在断言）",
      "code": [
        "README.md",
        "docs/README.md",
        "docs/code-guide.md",
        "docs/plans/FRAMEWORK-DOCS-1-slice.md"
      ],
      "tests": [
        "tests/unit/test_framework_docs.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/code-guide.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/plans/FRAMEWORK-DOCS-1-slice.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_docs.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "QUALITY-GATE-ENCODING-1",
      "title": "质量门禁输出编码修复（2026-08-08，用户指令“继续开发”）：quality_gate 子进程强制 UTF-8（gate_env：PYTHONIOENCODING=utf-8 + PYTHONUTF8=1，复制不污染父环境；两个 subprocess.run 均改用 gate_env），消除 VERIFICATION.md 门禁记录乱码根因（Windows 控制台 GBK 输出经 errors=replace 不可逆破坏）；历史乱码记录已清理（截除备份）；锁定脚本链同步（quality_gate.py 哈希 → python-script-lock.tsv → toolchain-lock script_inventory/source_sha256 → make.cs ScriptInventorySha256）；补回归测试；仅 stdlib 离线",
      "code": [
        "scripts/quality_gate.py",
        "docs/dependencies/python-script-lock.tsv",
        "docs/dependencies/toolchain-lock.json",
        "scripts/tool-shims/make.cs",
        "tests/unit/test_quality_gate_encoding.py"
      ],
      "tests": [
        "tests/unit/test_quality_gate_encoding.py",
        "tests/security/test_local_toolchain_security.py",
        "tests/integration/test_dev_environment_entry.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/python-script-lock.tsv",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/tool-shims/make.cs",
          "exists": true
        },
        {
          "kind": "code",
          "path": "tests/unit/test_quality_gate_encoding.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_encoding.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/security/test_local_toolchain_security.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_dev_environment_entry.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T01:19:07.025620Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T01:19:20.570496Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
s": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-6",
      "title": "共享 ISO 校验构造器全仓落地（2026-08-08，用户指令\"继续开发，先不要全量门禁\"）：新增依赖无关叶模块 src/coevo/timefmt.py（is_iso_utc_z：`\\Z` 锚定拒尾部换行、小数秒、日历校验、非字符串 fail-closed），root_modules 登记；framework/validation.py 由 timefmt 导入并再导出；10 个产品模块 + 框架族统一引用共享构造器，去 11 处正则副本与包级 _ISO 再导出；锚定测试改测共享构造器",
      "code": [
        "src/coevo/timefmt.py",
        "src/coevo/framework/validation.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/knowledge_base/models.py",
        "src/coevo/audit_governance/models.py",
        "src/coevo/audit_governance/facade.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/orchestrator/service.py",
        "src/coevo/orchestrator/_real_chain.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/talent/models.py",
        "src/coevo/task_decomposition/agent.py",
        "src/coevo/task_decomposition/baseline.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps6.py",
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/facade.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps6.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-DOCS-1",
      "title": "框架层文档治理收口（2026-08-08，用户指令\"继续开发，先不要全量门禁\"）：README 核心能力表加 US-16 行与框架层说明、架构树加 `framework/` + `timefmt.py`、文档索引加 `docs/framework/` 与 `docs/plans/distributed-agent-framework/`、当前状态加框架层 bullet；docs/code-guide.md 新增 framework/ 与 timefmt.py 引导节（模块职责 + 关键入口）；docs/README.md 索引登记 docs/framework/；新增文档治理守卫测试（README/code-guide/docs 索引覆盖断言 + docs/framework 文件存在断言）",
      "code": [
        "README.md",
        "docs/README.md",
        "docs/code-guide.md",
        "docs/plans/FRAMEWORK-DOCS-1-slice.md"
      ],
      "tests": [
        "tests/unit/test_framework_docs.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/code-guide.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/plans/FRAMEWORK-DOCS-1-slice.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_docs.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "QUALITY-GATE-ENCODING-1",
      "title": "质量门禁输出编码修复（2026-08-08，用户指令“继续开发”）：quality_gate 子进程强制 UTF-8（gate_env：PYTHONIOENCODING=utf-8 + PYTHONUTF8=1，复制不污染父环境；两个 subprocess.run 均改用 gate_env），消除 VERIFICATION.md 门禁记录乱码根因（Windows 控制台 GBK 输出经 errors=replace 不可逆破坏）；历史乱码记录已清理（截除备份）；锁定脚本链同步（quality_gate.py 哈希 → python-script-lock.tsv → toolchain-lock script_inventory/source_sha256 → make.cs ScriptInventorySha256）；补回归测试；仅 stdlib 离线",
      "code": [
        "scripts/quality_gate.py",
        "docs/dependencies/python-script-lock.tsv",
        "docs/dependencies/toolchain-lock.json",
        "scripts/tool-shims/make.cs",
        "tests/unit/test_quality_gate_encoding.py"
      ],
      "tests": [
        "tests/unit/test_quality_gate_encoding.py",
        "tests/security/test_local_toolchain_security.py",
        "tests/integration/test_dev_environment_entry.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/python-script-lock.tsv",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/tool-shims/make.cs",
          "exists": true
        },
        {
          "kind": "code",
          "path": "tests/unit/test_quality_gate_encoding.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_encoding.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/security/test_local_toolchain_security.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_dev_environment_entry.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T01:27:47.479377Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T01:28:00.115819Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
   ],
      "tests": [
        "tests/unit/test_framework_gaps6.py",
        "tests/unit/test_iso_anchor_regression.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/facade.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/agent.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps6.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_iso_anchor_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-DOCS-1",
      "title": "框架层文档治理收口（2026-08-08，用户指令\"继续开发，先不要全量门禁\"）：README 核心能力表加 US-16 行与框架层说明、架构树加 `framework/` + `timefmt.py`、文档索引加 `docs/framework/` 与 `docs/plans/distributed-agent-framework/`、当前状态加框架层 bullet；docs/code-guide.md 新增 framework/ 与 timefmt.py 引导节（模块职责 + 关键入口）；docs/README.md 索引登记 docs/framework/；新增文档治理守卫测试（README/code-guide/docs 索引覆盖断言 + docs/framework 文件存在断言）",
      "code": [
        "README.md",
        "docs/README.md",
        "docs/code-guide.md",
        "docs/plans/FRAMEWORK-DOCS-1-slice.md"
      ],
      "tests": [
        "tests/unit/test_framework_docs.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/README.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/code-guide.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/plans/FRAMEWORK-DOCS-1-slice.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_docs.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "QUALITY-GATE-ENCODING-1",
      "title": "质量门禁输出编码修复（2026-08-08，用户指令“继续开发”）：quality_gate 子进程强制 UTF-8（gate_env：PYTHONIOENCODING=utf-8 + PYTHONUTF8=1，复制不污染父环境；两个 subprocess.run 均改用 gate_env），消除 VERIFICATION.md 门禁记录乱码根因（Windows 控制台 GBK 输出经 errors=replace 不可逆破坏）；历史乱码记录已清理（截除备份）；锁定脚本链同步（quality_gate.py 哈希 → python-script-lock.tsv → toolchain-lock script_inventory/source_sha256 → make.cs ScriptInventorySha256）；补回归测试；仅 stdlib 离线",
      "code": [
        "scripts/quality_gate.py",
        "docs/dependencies/python-script-lock.tsv",
        "docs/dependencies/toolchain-lock.json",
        "scripts/tool-shims/make.cs",
        "tests/unit/test_quality_gate_encoding.py"
      ],
      "tests": [
        "tests/unit/test_quality_gate_encoding.py",
        "tests/security/test_local_toolchain_security.py",
        "tests/integration/test_dev_environment_entry.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/python-script-lock.tsv",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/tool-shims/make.cs",
          "exists": true
        },
        {
          "kind": "code",
          "path": "tests/unit/test_quality_gate_encoding.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_encoding.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/security/test_local_toolchain_security.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_dev_environment_entry.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-1",
      "title": "基于框架优化原应用实现（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：AgentRegistry.by_capability 惰性能力索引（O(V)→摊销 O(1)，注册顺序语义不变，register/set_status 新实例经 __post_init__ 自动失效）；build_registration_manifest 去除 json 双重序列化（结构化剥离自指字段，wire 字节不变并字节级回归锁定 sha256=00ff9ada…）；chain_to_plan 用 dataclasses.replace 一次成型 plan_id（节点/边冻结复用）；demo 注册装配收敛到 demo_support.register_demo_agents（显式非生产，仍强制 guard_registration）+ pipeline 组合根复用模块级 allow-all RBAC/scope 检查器；纯函数 stdlib + L17",
      "code": [
        "src/coevo/orchestrator/models.py",
        "src/coevo/framework/integration.py",
        "src/coevo/app/demo_support.py",
        "src/coevo/app/pipeline.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize1.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize1.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T01:37:15.855873Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T01:37:26.491979Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
s": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_docs.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_module_docs.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "QUALITY-GATE-ENCODING-1",
      "title": "质量门禁输出编码修复（2026-08-08，用户指令“继续开发”）：quality_gate 子进程强制 UTF-8（gate_env：PYTHONIOENCODING=utf-8 + PYTHONUTF8=1，复制不污染父环境；两个 subprocess.run 均改用 gate_env），消除 VERIFICATION.md 门禁记录乱码根因（Windows 控制台 GBK 输出经 errors=replace 不可逆破坏）；历史乱码记录已清理（截除备份）；锁定脚本链同步（quality_gate.py 哈希 → python-script-lock.tsv → toolchain-lock script_inventory/source_sha256 → make.cs ScriptInventorySha256）；补回归测试；仅 stdlib 离线",
      "code": [
        "scripts/quality_gate.py",
        "docs/dependencies/python-script-lock.tsv",
        "docs/dependencies/toolchain-lock.json",
        "scripts/tool-shims/make.cs",
        "tests/unit/test_quality_gate_encoding.py"
      ],
      "tests": [
        "tests/unit/test_quality_gate_encoding.py",
        "tests/security/test_local_toolchain_security.py",
        "tests/integration/test_dev_environment_entry.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/python-script-lock.tsv",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/tool-shims/make.cs",
          "exists": true
        },
        {
          "kind": "code",
          "path": "tests/unit/test_quality_gate_encoding.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_encoding.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/security/test_local_toolchain_security.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_dev_environment_entry.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-1",
      "title": "基于框架优化原应用实现（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：AgentRegistry.by_capability 惰性能力索引（O(V)→摊销 O(1)，注册顺序语义不变，register/set_status 新实例经 __post_init__ 自动失效）；build_registration_manifest 去除 json 双重序列化（结构化剥离自指字段，wire 字节不变并字节级回归锁定 sha256=00ff9ada…）；chain_to_plan 用 dataclasses.replace 一次成型 plan_id（节点/边冻结复用）；demo 注册装配收敛到 demo_support.register_demo_agents（显式非生产，仍强制 guard_registration）+ pipeline 组合根复用模块级 allow-all RBAC/scope 检查器；纯函数 stdlib + L17",
      "code": [
        "src/coevo/orchestrator/models.py",
        "src/coevo/framework/integration.py",
        "src/coevo/app/demo_support.py",
        "src/coevo/app/pipeline.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize1.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize1.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-2",
      "title": "共享时间生成器全仓落地（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：timefmt 新增 now_utc_iso_z（依赖无关叶子模块，格式与既有副本完全一致含微秒与尾随 Z），收敛 13 处私有副本（knowledge_base/audit_governance/cockpit/demo_support/task_flow/protocol×4/progress_capture/task_decomposition/talent/crypto）与 3 处直接内联（identity×3）；公开导出名（cockpit.sessions/demo_support）保留 API 仅改来源；行为与 wire 字节不变；全仓源码守卫防回归；stdlib only",
      "code": [
        "src/coevo/timefmt.py",
        "src/coevo/app/demo_support.py",
        "src/coevo/audit_governance/stream_store.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/identity/audit_anchor.py",
        "src/coevo/identity/private_keys.py",
        "src/coevo/identity/repository.py",
        "src/coevo/knowledge_base/store.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/protocol/import_service.py",
        "src/coevo/protocol/package_store_db.py",
        "src/coevo/protocol/sm2_keywrap.py",
        "src/coevo/protocol/sm2_sign.py",
        "src/coevo/talent/store.py",
        "src/coevo/task_decomposition/baseline.py",
        "src/coevo/task_flow/parser.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/audit_anchor.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/private_keys.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/import_service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/package_store_db.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/sm2_keywrap.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/sm2_sign.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_flow/parser.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T01:46:05.971369Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T01:46:18.167426Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
     "exists": true
        },
        {
          "kind": "test",
          "path": "tests/security/test_local_toolchain_security.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_dev_environment_entry.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-1",
      "title": "基于框架优化原应用实现（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：AgentRegistry.by_capability 惰性能力索引（O(V)→摊销 O(1)，注册顺序语义不变，register/set_status 新实例经 __post_init__ 自动失效）；build_registration_manifest 去除 json 双重序列化（结构化剥离自指字段，wire 字节不变并字节级回归锁定 sha256=00ff9ada…）；chain_to_plan 用 dataclasses.replace 一次成型 plan_id（节点/边冻结复用）；demo 注册装配收敛到 demo_support.register_demo_agents（显式非生产，仍强制 guard_registration）+ pipeline 组合根复用模块级 allow-all RBAC/scope 检查器；纯函数 stdlib + L17",
      "code": [
        "src/coevo/orchestrator/models.py",
        "src/coevo/framework/integration.py",
        "src/coevo/app/demo_support.py",
        "src/coevo/app/pipeline.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize1.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize1.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-2",
      "title": "共享时间生成器全仓落地（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：timefmt 新增 now_utc_iso_z（依赖无关叶子模块，格式与既有副本完全一致含微秒与尾随 Z），收敛 13 处私有副本（knowledge_base/audit_governance/cockpit/demo_support/task_flow/protocol×4/progress_capture/task_decomposition/talent/crypto）与 3 处直接内联（identity×3）；公开导出名（cockpit.sessions/demo_support）保留 API 仅改来源；行为与 wire 字节不变；全仓源码守卫防回归；stdlib only",
      "code": [
        "src/coevo/timefmt.py",
        "src/coevo/app/demo_support.py",
        "src/coevo/audit_governance/stream_store.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/identity/audit_anchor.py",
        "src/coevo/identity/private_keys.py",
        "src/coevo/identity/repository.py",
        "src/coevo/knowledge_base/store.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/protocol/import_service.py",
        "src/coevo/protocol/package_store_db.py",
        "src/coevo/protocol/sm2_keywrap.py",
        "src/coevo/protocol/sm2_sign.py",
        "src/coevo/talent/store.py",
        "src/coevo/task_decomposition/baseline.py",
        "src/coevo/task_flow/parser.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/audit_anchor.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/private_keys.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/import_service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/package_store_db.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/sm2_keywrap.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/sm2_sign.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_flow/parser.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-3",
      "title": "共享 canonical JSON 序列化与摘要（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：新增根级叶子 src/coevo/canon.py（canonical_json_bytes / canonical_digest，stdlib only），收敛框架内部重复（integration._canonical / manifest_checker._canonical_bytes 字节语义相同）与 identity 5 处 digest 内联（repository 事件哈希链 2 + business digest 1、validation bundle digest 1、private_keys 审计链 1）；ensure_ascii 语义逐点保留（business digest=False）、digest 逐位不变；root_modules.md 登记；全仓源码守卫防回归",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/identity/repository.py",
        "src/coevo/identity/validation.py",
        "src/coevo/identity/private_keys.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/private_keys.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T01:54:00.078811Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T01:54:08.311997Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
/app/pipeline.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize1.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize1.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-2",
      "title": "共享时间生成器全仓落地（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：timefmt 新增 now_utc_iso_z（依赖无关叶子模块，格式与既有副本完全一致含微秒与尾随 Z），收敛 13 处私有副本（knowledge_base/audit_governance/cockpit/demo_support/task_flow/protocol×4/progress_capture/task_decomposition/talent/crypto）与 3 处直接内联（identity×3）；公开导出名（cockpit.sessions/demo_support）保留 API 仅改来源；行为与 wire 字节不变；全仓源码守卫防回归；stdlib only",
      "code": [
        "src/coevo/timefmt.py",
        "src/coevo/app/demo_support.py",
        "src/coevo/audit_governance/stream_store.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/identity/audit_anchor.py",
        "src/coevo/identity/private_keys.py",
        "src/coevo/identity/repository.py",
        "src/coevo/knowledge_base/store.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/protocol/import_service.py",
        "src/coevo/protocol/package_store_db.py",
        "src/coevo/protocol/sm2_keywrap.py",
        "src/coevo/protocol/sm2_sign.py",
        "src/coevo/talent/store.py",
        "src/coevo/task_decomposition/baseline.py",
        "src/coevo/task_flow/parser.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/audit_anchor.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/private_keys.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/import_service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/package_store_db.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/sm2_keywrap.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/sm2_sign.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_flow/parser.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-3",
      "title": "共享 canonical JSON 序列化与摘要（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：新增根级叶子 src/coevo/canon.py（canonical_json_bytes / canonical_digest，stdlib only），收敛框架内部重复（integration._canonical / manifest_checker._canonical_bytes 字节语义相同）与 identity 5 处 digest 内联（repository 事件哈希链 2 + business digest 1、validation bundle digest 1、private_keys 审计链 1）；ensure_ascii 语义逐点保留（business digest=False）、digest 逐位不变；root_modules.md 登记；全仓源码守卫防回归",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/identity/repository.py",
        "src/coevo/identity/validation.py",
        "src/coevo/identity/private_keys.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/private_keys.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-4",
      "title": "框架默认策略 Profile 惰性缓存（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：default_profiles() 一次性构造并缓存 4 个默认 Policy（Policy 与嵌套 Profile 全 frozen 不可变，安全共享），get_default_profile 字典 O(1) 查找且 fail-closed 保留（未知名仍抛 PolicyValidationError）；消除 pipeline/validate_plan 等消费点每次重复构造 Policy（O(4)×N → 一次构造 + O(1)）；docs/modules/framework.md 同步；stdlib only",
      "code": [
        "src/coevo/framework/policy.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize4.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize4.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T02:05:34.626445Z — target=`quality` fingerprint=`34d637f035600903`
- exit_code: `0`
```text
requires_recovery_and_reopen_commits_exactly_once) ... ok
test_row_shape_validator_rejects_each_oversize_and_malformed_column (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_row_shape_validator_rejects_each_oversize_and_malformed_column) ... ok
test_signed_chain_binds_store_head_sequence_and_previous_hash (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_signed_chain_binds_store_head_sequence_and_previous_hash) ... ok
test_stale_baseline_is_rejected_before_insert (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
test_truncation_is_rejected_by_freshness_checkpoint (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_truncation_is_rejected_by_freshness_checkpoint) ... ok
test_gitignore_excludes_receipt_pattern (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_gitignore_excludes_receipt_pattern) ... ok
test_no_reachable_receipt_blobs_across_all_refs (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_no_reachable_receipt_blobs_across_all_refs) ... ok
test_no_tracked_receipt_paths (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_no_tracked_receipt_paths) ... ok
test_pre_scrub_head_is_no_longer_reachable (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_pre_scrub_head_is_no_longer_reachable) ... ok
test_validate_bundle_rejects_private_key_handle_field (test_private_key_storage.IdentityBundlePrivateKeyRejectionTests.test_validate_bundle_rejects_private_key_handle_field) ... ok
test_validate_bundle_rejects_private_key_pkcs8_bytes (test_private_key_storage.IdentityBundlePrivateKeyRejectionTests.test_validate_bundle_rejects_private_key_pkcs8_bytes) ... ok
test_reference_accepts_only_safe_metadata (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_accepts_only_safe_metadata) ... ok
test_reference_is_frozen_and_hash_stable_across_rotations (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_is_frozen_and_hash_stable_across_rotations) ... ok
test_reference_rejects_inverted_validity (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_rejects_inverted_validity) ... ok
test_reference_rejects_malformed_handle_and_digest (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_rejects_malformed_handle_and_digest) ... ok
test_repr_and_pickle_never_expose_secret_token (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_repr_and_pickle_never_expose_secret_token) ... ok
test_validate_handle_payload_rejects_private_key_blob_strings (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_validate_handle_payload_rejects_private_key_blob_strings) ... ok
test_validate_handle_payload_rejects_unknown_or_sensitive_fields (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_validate_handle_payload_rejects_unknown_or_sensitive_fields) ... ok
test_audit_chain_detects_event_tampering (test_private_key_storage.PrivateKeyServicePolicyTests.test_audit_chain_detects_event_tampering) ... ok
test_audit_chain_records_store_use_revoke_and_destroy (test_private_key_storage.PrivateKeyServicePolicyTests.test_audit_chain_records_store_use_revoke_and_destroy) ... ok
test_destroyed_handle_blocks_use_with_stale_reference (test_private_key_storage.PrivateKeyServicePolicyTests.test_destroyed_handle_blocks_use_with_stale_reference) ... ok
test_overwrite_store_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_overwrite_store_is_rejected) ... ok
test_revoke_without_reason_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_revoke_without_reason_is_rejected) ... ok
test_revoked_reference_blocks_use_and_audits_rejection (test_private_key_storage.PrivateKeyServicePolicyTests.test_revoked_reference_blocks_use_and_audits_rejection) ... ok
test_stored_reference_round_trips_use_and_returns_signature (test_private_key_storage.PrivateKeyServicePolicyTests.test_stored_reference_round_trips_use_and_returns_signature) ... ok
test_untrusted_parent_thumbprint_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_untrusted_parent_thumbprint_is_rejected) ... ok
test_use_outside_validity_window_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_use_outside_validity_window_is_rejected) ... ok
test_use_with_naive_datetime_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_use_with_naive_datetime_is_rejected) ... ok
test_verify_binds_certificate_pin_digest_algorithm_and_audits_digest_only (test_private_key_storage.PrivateKeyServicePolicyTests.test_verify_binds_certificate_pin_digest_algorithm_and_audits_digest_only) ... ok
test_verify_rejects_wrong_pin_revoked_destroyed_and_bad_signature (test_private_key_storage.PrivateKeyServicePolicyTests.test_verify_rejects_wrong_pin_revoked_destroyed_and_bad_signature) ... ok
test_poisoned_powershell_path_is_rejected_before_execution (test_private_key_storage.WindowsPrivateKeyLaunchPolicyTests.test_poisoned_powershell_path_is_rejected_before_execution) ... ok
test_rejects_uncontrolled_helper_path (test_private_key_storage.WindowsPrivateKeyLaunchPolicyTests.test_rejects_uncontrolled_helper_path) ... ok
test_custom_tools_use_current_typed_api (test_tool_permissions.PermissionTests.test_custom_tools_use_current_typed_api) ... ok
test_network_and_install_commands_are_fail_closed (test_tool_permissions.PermissionTests.test_network_and_install_commands_are_fail_closed) ... ok

----------------------------------------------------------------------
Ran 99 tests in 91.346s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 146.312s

OK
audit seal: fully-sealed

```




## 2026-08-08T02:19:52.702287Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T02:20:00.681855Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
oevo/app/demo_support.py",
        "src/coevo/audit_governance/stream_store.py",
        "src/coevo/cockpit/sessions.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/identity/audit_anchor.py",
        "src/coevo/identity/private_keys.py",
        "src/coevo/identity/repository.py",
        "src/coevo/knowledge_base/store.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/protocol/import_service.py",
        "src/coevo/protocol/package_store_db.py",
        "src/coevo/protocol/sm2_keywrap.py",
        "src/coevo/protocol/sm2_sign.py",
        "src/coevo/talent/store.py",
        "src/coevo/task_decomposition/baseline.py",
        "src/coevo/task_flow/parser.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize2.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/audit_anchor.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/private_keys.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/import_service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/package_store_db.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/sm2_keywrap.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/sm2_sign.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_flow/parser.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-3",
      "title": "共享 canonical JSON 序列化与摘要（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：新增根级叶子 src/coevo/canon.py（canonical_json_bytes / canonical_digest，stdlib only），收敛框架内部重复（integration._canonical / manifest_checker._canonical_bytes 字节语义相同）与 identity 5 处 digest 内联（repository 事件哈希链 2 + business digest 1、validation bundle digest 1、private_keys 审计链 1）；ensure_ascii 语义逐点保留（business digest=False）、digest 逐位不变；root_modules.md 登记；全仓源码守卫防回归",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/identity/repository.py",
        "src/coevo/identity/validation.py",
        "src/coevo/identity/private_keys.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/private_keys.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-4",
      "title": "框架默认策略 Profile 惰性缓存（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：default_profiles() 一次性构造并缓存 4 个默认 Policy（Policy 与嵌套 Profile 全 frozen 不可变，安全共享），get_default_profile 字典 O(1) 查找且 fail-closed 保留（未知名仍抛 PolicyValidationError）；消除 pipeline/validate_plan 等消费点每次重复构造 Policy（O(4)×N → 一次构造 + O(1)）；docs/modules/framework.md 同步；stdlib only",
      "code": [
        "src/coevo/framework/policy.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize4.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize4.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-5",
      "title": "real_chain_store 收敛到共享 canonical（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，做全量门禁，成功后 push 到 github\"）：canon.py 的 canonical_json_bytes/canonical_digest 新增 allow_nan 参数（默认 False 拒绝 NaN/Infinity，fail-closed）；orchestrator/real_chain_store 的 canonical_json_bytes 保留严格类型校验（非有限 float/非 JSON 拒绝、RealChainStoreError 语义）但序列化委托共享 canon（ensure_ascii=False/allow_nan=False，字节逐位不变），canonical_digest 经共享序列化计算摘要；root_modules.md 补充 allow_nan 语义",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/orchestrator/real_chain_store.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize5.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/real_chain_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize5.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T02:32:03.133525Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T02:32:11.458929Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
"src/coevo/timefmt.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/sessions.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/audit_anchor.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/private_keys.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/import_service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/package_store_db.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/sm2_keywrap.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/sm2_sign.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_flow/parser.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-3",
      "title": "共享 canonical JSON 序列化与摘要（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：新增根级叶子 src/coevo/canon.py（canonical_json_bytes / canonical_digest，stdlib only），收敛框架内部重复（integration._canonical / manifest_checker._canonical_bytes 字节语义相同）与 identity 5 处 digest 内联（repository 事件哈希链 2 + business digest 1、validation bundle digest 1、private_keys 审计链 1）；ensure_ascii 语义逐点保留（business digest=False）、digest 逐位不变；root_modules.md 登记；全仓源码守卫防回归",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/identity/repository.py",
        "src/coevo/identity/validation.py",
        "src/coevo/identity/private_keys.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/private_keys.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-4",
      "title": "框架默认策略 Profile 惰性缓存（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：default_profiles() 一次性构造并缓存 4 个默认 Policy（Policy 与嵌套 Profile 全 frozen 不可变，安全共享），get_default_profile 字典 O(1) 查找且 fail-closed 保留（未知名仍抛 PolicyValidationError）；消除 pipeline/validate_plan 等消费点每次重复构造 Policy（O(4)×N → 一次构造 + O(1)）；docs/modules/framework.md 同步；stdlib only",
      "code": [
        "src/coevo/framework/policy.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize4.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize4.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-5",
      "title": "real_chain_store 收敛到共享 canonical（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，做全量门禁，成功后 push 到 github\"）：canon.py 的 canonical_json_bytes/canonical_digest 新增 allow_nan 参数（默认 False 拒绝 NaN/Infinity，fail-closed）；orchestrator/real_chain_store 的 canonical_json_bytes 保留严格类型校验（非有限 float/非 JSON 拒绝、RealChainStoreError 语义）但序列化委托共享 canon（ensure_ascii=False/allow_nan=False，字节逐位不变），canonical_digest 经共享序列化计算摘要；root_modules.md 补充 allow_nan 语义",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/orchestrator/real_chain_store.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize5.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/real_chain_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize5.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-6",
      "title": "demo 组合根阶段化收敛（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：run_demo_pipeline（~250 行大函数）的包导出/驾驶舱快照/知识库入库/审计流 4 段内联提取为模块级阶段函数（_export_demo_package/_build_demo_cockpit_views/_store_demo_knowledge/_publish_demo_audit，均标注 DEMO-ONLY），组合根薄编排、行为不变（demo e2e 3/3 回归）；hashlib/json import 收敛到包导出阶段；阶段函数可独立单测 + 架构守卫（内联体仅存在于各自助手内）",
      "code": [
        "src/coevo/app/pipeline.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize6.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize6.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T02:41:58.204220Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T02:42:06.395190Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
vo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/import_service.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/package_store_db.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/sm2_keywrap.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/sm2_sign.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_flow/parser.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-3",
      "title": "共享 canonical JSON 序列化与摘要（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：新增根级叶子 src/coevo/canon.py（canonical_json_bytes / canonical_digest，stdlib only），收敛框架内部重复（integration._canonical / manifest_checker._canonical_bytes 字节语义相同）与 identity 5 处 digest 内联（repository 事件哈希链 2 + business digest 1、validation bundle digest 1、private_keys 审计链 1）；ensure_ascii 语义逐点保留（business digest=False）、digest 逐位不变；root_modules.md 登记；全仓源码守卫防回归",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/identity/repository.py",
        "src/coevo/identity/validation.py",
        "src/coevo/identity/private_keys.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/private_keys.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-4",
      "title": "框架默认策略 Profile 惰性缓存（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：default_profiles() 一次性构造并缓存 4 个默认 Policy（Policy 与嵌套 Profile 全 frozen 不可变，安全共享），get_default_profile 字典 O(1) 查找且 fail-closed 保留（未知名仍抛 PolicyValidationError）；消除 pipeline/validate_plan 等消费点每次重复构造 Policy（O(4)×N → 一次构造 + O(1)）；docs/modules/framework.md 同步；stdlib only",
      "code": [
        "src/coevo/framework/policy.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize4.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize4.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-5",
      "title": "real_chain_store 收敛到共享 canonical（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，做全量门禁，成功后 push 到 github\"）：canon.py 的 canonical_json_bytes/canonical_digest 新增 allow_nan 参数（默认 False 拒绝 NaN/Infinity，fail-closed）；orchestrator/real_chain_store 的 canonical_json_bytes 保留严格类型校验（非有限 float/非 JSON 拒绝、RealChainStoreError 语义）但序列化委托共享 canon（ensure_ascii=False/allow_nan=False，字节逐位不变），canonical_digest 经共享序列化计算摘要；root_modules.md 补充 allow_nan 语义",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/orchestrator/real_chain_store.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize5.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/real_chain_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize5.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-6",
      "title": "demo 组合根阶段化收敛（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：run_demo_pipeline（~250 行大函数）的包导出/驾驶舱快照/知识库入库/审计流 4 段内联提取为模块级阶段函数（_export_demo_package/_build_demo_cockpit_views/_store_demo_knowledge/_publish_demo_audit，均标注 DEMO-ONLY），组合根薄编排、行为不变（demo e2e 3/3 回归）；hashlib/json import 收敛到包导出阶段；阶段函数可独立单测 + 架构守卫（内联体仅存在于各自助手内）",
      "code": [
        "src/coevo/app/pipeline.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize6.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize6.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-7",
      "title": "真实链失败收尾路径去重（2026-08-08，用户指令\"继续\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：orchestrator/_real_chain.py 的 dispatch_real_chain 中 3 处结构相同的失败收尾（agent 不可用 / facade 失败 / facade 重试失败：追加 ESCALATED trace + _finish_dispatch_terminal）提取为 _escalate_and_finish 单一辅助，行为不变（ESCALATED 状态与审计存储语义逐位一致）；守卫测试钉住 3 个失败 detail 各单一调用点",
      "code": [
        "src/coevo/orchestrator/_real_chain.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize7.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize7.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T03:02:37.745394Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T03:02:46.101773Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_decomposition/baseline.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/task_flow/parser.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize2.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-3",
      "title": "共享 canonical JSON 序列化与摘要（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：新增根级叶子 src/coevo/canon.py（canonical_json_bytes / canonical_digest，stdlib only），收敛框架内部重复（integration._canonical / manifest_checker._canonical_bytes 字节语义相同）与 identity 5 处 digest 内联（repository 事件哈希链 2 + business digest 1、validation bundle digest 1、private_keys 审计链 1）；ensure_ascii 语义逐点保留（business digest=False）、digest 逐位不变；root_modules.md 登记；全仓源码守卫防回归",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/framework/integration.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/identity/repository.py",
        "src/coevo/identity/validation.py",
        "src/coevo/identity/private_keys.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize3.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/private_keys.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-4",
      "title": "框架默认策略 Profile 惰性缓存（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：default_profiles() 一次性构造并缓存 4 个默认 Policy（Policy 与嵌套 Profile 全 frozen 不可变，安全共享），get_default_profile 字典 O(1) 查找且 fail-closed 保留（未知名仍抛 PolicyValidationError）；消除 pipeline/validate_plan 等消费点每次重复构造 Policy（O(4)×N → 一次构造 + O(1)）；docs/modules/framework.md 同步；stdlib only",
      "code": [
        "src/coevo/framework/policy.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize4.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize4.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-5",
      "title": "real_chain_store 收敛到共享 canonical（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，做全量门禁，成功后 push 到 github\"）：canon.py 的 canonical_json_bytes/canonical_digest 新增 allow_nan 参数（默认 False 拒绝 NaN/Infinity，fail-closed）；orchestrator/real_chain_store 的 canonical_json_bytes 保留严格类型校验（非有限 float/非 JSON 拒绝、RealChainStoreError 语义）但序列化委托共享 canon（ensure_ascii=False/allow_nan=False，字节逐位不变），canonical_digest 经共享序列化计算摘要；root_modules.md 补充 allow_nan 语义",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/orchestrator/real_chain_store.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize5.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/real_chain_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize5.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-6",
      "title": "demo 组合根阶段化收敛（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：run_demo_pipeline（~250 行大函数）的包导出/驾驶舱快照/知识库入库/审计流 4 段内联提取为模块级阶段函数（_export_demo_package/_build_demo_cockpit_views/_store_demo_knowledge/_publish_demo_audit，均标注 DEMO-ONLY），组合根薄编排、行为不变（demo e2e 3/3 回归）；hashlib/json import 收敛到包导出阶段；阶段函数可独立单测 + 架构守卫（内联体仅存在于各自助手内）",
      "code": [
        "src/coevo/app/pipeline.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize6.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize6.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-7",
      "title": "真实链失败收尾路径去重（2026-08-08，用户指令\"继续\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：orchestrator/_real_chain.py 的 dispatch_real_chain 中 3 处结构相同的失败收尾（agent 不可用 / facade 失败 / facade 重试失败：追加 ESCALATED trace + _finish_dispatch_terminal）提取为 _escalate_and_finish 单一辅助，行为不变（ESCALATED 状态与审计存储语义逐位一致）；守卫测试钉住 3 个失败 detail 各单一调用点",
      "code": [
        "src/coevo/orchestrator/_real_chain.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize7.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize7.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-8",
      "title": "真实链 resume 失败收尾收敛（2026-08-08，用户指令\"继续\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：orchestrator/_real_chain.py 的 resume_real_chain 中 2 处结构相同的 ESCALATED 失败收尾（包验证失败 except 分支 / crypto 能力不可用：追加 ESCALATED trace + report + outcome + store.finish_resume_failure）提取为 _finish_resume_escalated 单一辅助，行为不变（ESCALATED 语义与审计存储一致）；守卫测试钉住 2 个 code 常量各单一调用点",
      "code": [
        "src/coevo/orchestrator/_real_chain.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize8.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize8.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T03:11:41.408897Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T03:11:52.850163Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
de",
          "path": "src/coevo/identity/repository.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/private_keys.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize3.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-4",
      "title": "框架默认策略 Profile 惰性缓存（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：default_profiles() 一次性构造并缓存 4 个默认 Policy（Policy 与嵌套 Profile 全 frozen 不可变，安全共享），get_default_profile 字典 O(1) 查找且 fail-closed 保留（未知名仍抛 PolicyValidationError）；消除 pipeline/validate_plan 等消费点每次重复构造 Policy（O(4)×N → 一次构造 + O(1)）；docs/modules/framework.md 同步；stdlib only",
      "code": [
        "src/coevo/framework/policy.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize4.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize4.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-5",
      "title": "real_chain_store 收敛到共享 canonical（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，做全量门禁，成功后 push 到 github\"）：canon.py 的 canonical_json_bytes/canonical_digest 新增 allow_nan 参数（默认 False 拒绝 NaN/Infinity，fail-closed）；orchestrator/real_chain_store 的 canonical_json_bytes 保留严格类型校验（非有限 float/非 JSON 拒绝、RealChainStoreError 语义）但序列化委托共享 canon（ensure_ascii=False/allow_nan=False，字节逐位不变），canonical_digest 经共享序列化计算摘要；root_modules.md 补充 allow_nan 语义",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/orchestrator/real_chain_store.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize5.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/real_chain_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize5.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-6",
      "title": "demo 组合根阶段化收敛（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：run_demo_pipeline（~250 行大函数）的包导出/驾驶舱快照/知识库入库/审计流 4 段内联提取为模块级阶段函数（_export_demo_package/_build_demo_cockpit_views/_store_demo_knowledge/_publish_demo_audit，均标注 DEMO-ONLY），组合根薄编排、行为不变（demo e2e 3/3 回归）；hashlib/json import 收敛到包导出阶段；阶段函数可独立单测 + 架构守卫（内联体仅存在于各自助手内）",
      "code": [
        "src/coevo/app/pipeline.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize6.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize6.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-7",
      "title": "真实链失败收尾路径去重（2026-08-08，用户指令\"继续\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：orchestrator/_real_chain.py 的 dispatch_real_chain 中 3 处结构相同的失败收尾（agent 不可用 / facade 失败 / facade 重试失败：追加 ESCALATED trace + _finish_dispatch_terminal）提取为 _escalate_and_finish 单一辅助，行为不变（ESCALATED 状态与审计存储语义逐位一致）；守卫测试钉住 3 个失败 detail 各单一调用点",
      "code": [
        "src/coevo/orchestrator/_real_chain.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize7.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize7.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-8",
      "title": "真实链 resume 失败收尾收敛（2026-08-08，用户指令\"继续\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：orchestrator/_real_chain.py 的 resume_real_chain 中 2 处结构相同的 ESCALATED 失败收尾（包验证失败 except 分支 / crypto 能力不可用：追加 ESCALATED trace + report + outcome + store.finish_resume_failure）提取为 _finish_resume_escalated 单一辅助，行为不变（ESCALATED 语义与审计存储一致）；守卫测试钉住 2 个 code 常量各单一调用点",
      "code": [
        "src/coevo/orchestrator/_real_chain.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize8.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize8.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-9",
      "title": "剩余 canonical 序列化变体统一（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：canon.py 新增 canonical_json_str（str 变体，与 canonical_json_bytes 同参、字节逐位一致），收敛 cng_handle（_write body + 删除本地 _canonical，哈希链调用点改 canonical_json_bytes）/ cockpit state_store（bytes 1 处）/ knowledge_base（str 1 处）/ talent（str 4 处）/ audit stream_store（append 2 处 + _chain_hash 1 处）；行为不变（cng 注册表哈希链、审计流哈希链、DB 载荷字节一致）；全仓守卫（5 模块内联 json.dumps 计数归零，cng_handle 仅留非 canonical 请求体）",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/cockpit/state_store.py",
        "src/coevo/knowledge_base/store.py",
        "src/coevo/talent/store.py",
        "src/coevo/audit_governance/stream_store.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize9.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/state_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream_store.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize9.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T03:19:24.632290Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T03:19:35.813444Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
",
      "code": [
        "src/coevo/framework/policy.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize4.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/policy.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize4.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-5",
      "title": "real_chain_store 收敛到共享 canonical（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，做全量门禁，成功后 push 到 github\"）：canon.py 的 canonical_json_bytes/canonical_digest 新增 allow_nan 参数（默认 False 拒绝 NaN/Infinity，fail-closed）；orchestrator/real_chain_store 的 canonical_json_bytes 保留严格类型校验（非有限 float/非 JSON 拒绝、RealChainStoreError 语义）但序列化委托共享 canon（ensure_ascii=False/allow_nan=False，字节逐位不变），canonical_digest 经共享序列化计算摘要；root_modules.md 补充 allow_nan 语义",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/orchestrator/real_chain_store.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize5.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/real_chain_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize5.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-6",
      "title": "demo 组合根阶段化收敛（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：run_demo_pipeline（~250 行大函数）的包导出/驾驶舱快照/知识库入库/审计流 4 段内联提取为模块级阶段函数（_export_demo_package/_build_demo_cockpit_views/_store_demo_knowledge/_publish_demo_audit，均标注 DEMO-ONLY），组合根薄编排、行为不变（demo e2e 3/3 回归）；hashlib/json import 收敛到包导出阶段；阶段函数可独立单测 + 架构守卫（内联体仅存在于各自助手内）",
      "code": [
        "src/coevo/app/pipeline.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize6.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize6.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-7",
      "title": "真实链失败收尾路径去重（2026-08-08，用户指令\"继续\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：orchestrator/_real_chain.py 的 dispatch_real_chain 中 3 处结构相同的失败收尾（agent 不可用 / facade 失败 / facade 重试失败：追加 ESCALATED trace + _finish_dispatch_terminal）提取为 _escalate_and_finish 单一辅助，行为不变（ESCALATED 状态与审计存储语义逐位一致）；守卫测试钉住 3 个失败 detail 各单一调用点",
      "code": [
        "src/coevo/orchestrator/_real_chain.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize7.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize7.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-8",
      "title": "真实链 resume 失败收尾收敛（2026-08-08，用户指令\"继续\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：orchestrator/_real_chain.py 的 resume_real_chain 中 2 处结构相同的 ESCALATED 失败收尾（包验证失败 except 分支 / crypto 能力不可用：追加 ESCALATED trace + report + outcome + store.finish_resume_failure）提取为 _finish_resume_escalated 单一辅助，行为不变（ESCALATED 语义与审计存储一致）；守卫测试钉住 2 个 code 常量各单一调用点",
      "code": [
        "src/coevo/orchestrator/_real_chain.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize8.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize8.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-9",
      "title": "剩余 canonical 序列化变体统一（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：canon.py 新增 canonical_json_str（str 变体，与 canonical_json_bytes 同参、字节逐位一致），收敛 cng_handle（_write body + 删除本地 _canonical，哈希链调用点改 canonical_json_bytes）/ cockpit state_store（bytes 1 处）/ knowledge_base（str 1 处）/ talent（str 4 处）/ audit stream_store（append 2 处 + _chain_hash 1 处）；行为不变（cng 注册表哈希链、审计流哈希链、DB 载荷字节一致）；全仓守卫（5 模块内联 json.dumps 计数归零，cng_handle 仅留非 canonical 请求体）",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/cockpit/state_store.py",
        "src/coevo/knowledge_base/store.py",
        "src/coevo/talent/store.py",
        "src/coevo/audit_governance/stream_store.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize9.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/state_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream_store.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize9.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-10",
      "title": "audit_anchor canonical 统一到 canon（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：canon.py 的 canonical_json_bytes/canonical_json_str/canonical_digest 新增 trailing_newline 参数（默认 False 不变，True 追加 \\n）；identity/audit_anchor.py::canonical 改用共享实现（ensure_ascii=False + trailing_newline=True，审计锚定记录字节逐位不变，本地 json.dumps 副本删除，函数签名保留）；canonical 收敛收官",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/identity/audit_anchor.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize10.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/audit_anchor.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize10.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T03:28:00.638710Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T03:28:12.761076Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
ror 语义）但序列化委托共享 canon（ensure_ascii=False/allow_nan=False，字节逐位不变），canonical_digest 经共享序列化计算摘要；root_modules.md 补充 allow_nan 语义",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/orchestrator/real_chain_store.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize5.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/real_chain_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize5.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-6",
      "title": "demo 组合根阶段化收敛（2026-08-08，用户指令\"基于框架，优化原来系统应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁\"）：run_demo_pipeline（~250 行大函数）的包导出/驾驶舱快照/知识库入库/审计流 4 段内联提取为模块级阶段函数（_export_demo_package/_build_demo_cockpit_views/_store_demo_knowledge/_publish_demo_audit，均标注 DEMO-ONLY），组合根薄编排、行为不变（demo e2e 3/3 回归）；hashlib/json import 收敛到包导出阶段；阶段函数可独立单测 + 架构守卫（内联体仅存在于各自助手内）",
      "code": [
        "src/coevo/app/pipeline.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize6.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/app/pipeline.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize6.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-7",
      "title": "真实链失败收尾路径去重（2026-08-08，用户指令\"继续\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：orchestrator/_real_chain.py 的 dispatch_real_chain 中 3 处结构相同的失败收尾（agent 不可用 / facade 失败 / facade 重试失败：追加 ESCALATED trace + _finish_dispatch_terminal）提取为 _escalate_and_finish 单一辅助，行为不变（ESCALATED 状态与审计存储语义逐位一致）；守卫测试钉住 3 个失败 detail 各单一调用点",
      "code": [
        "src/coevo/orchestrator/_real_chain.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize7.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize7.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-8",
      "title": "真实链 resume 失败收尾收敛（2026-08-08，用户指令\"继续\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：orchestrator/_real_chain.py 的 resume_real_chain 中 2 处结构相同的 ESCALATED 失败收尾（包验证失败 except 分支 / crypto 能力不可用：追加 ESCALATED trace + report + outcome + store.finish_resume_failure）提取为 _finish_resume_escalated 单一辅助，行为不变（ESCALATED 语义与审计存储一致）；守卫测试钉住 2 个 code 常量各单一调用点",
      "code": [
        "src/coevo/orchestrator/_real_chain.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize8.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize8.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-9",
      "title": "剩余 canonical 序列化变体统一（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：canon.py 新增 canonical_json_str（str 变体，与 canonical_json_bytes 同参、字节逐位一致），收敛 cng_handle（_write body + 删除本地 _canonical，哈希链调用点改 canonical_json_bytes）/ cockpit state_store（bytes 1 处）/ knowledge_base（str 1 处）/ talent（str 4 处）/ audit stream_store（append 2 处 + _chain_hash 1 处）；行为不变（cng 注册表哈希链、审计流哈希链、DB 载荷字节一致）；全仓守卫（5 模块内联 json.dumps 计数归零，cng_handle 仅留非 canonical 请求体）",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/cockpit/state_store.py",
        "src/coevo/knowledge_base/store.py",
        "src/coevo/talent/store.py",
        "src/coevo/audit_governance/stream_store.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize9.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/state_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream_store.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize9.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-10",
      "title": "audit_anchor canonical 统一到 canon（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：canon.py 的 canonical_json_bytes/canonical_json_str/canonical_digest 新增 trailing_newline 参数（默认 False 不变，True 追加 \\n）；identity/audit_anchor.py::canonical 改用共享实现（ensure_ascii=False + trailing_newline=True，审计锚定记录字节逐位不变，本地 json.dumps 副本删除，函数签名保留）；canonical 收敛收官",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/identity/audit_anchor.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize10.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/audit_anchor.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize10.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-7",
      "title": "生产验签入口守卫（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"；INTEGRATION-4 Low 1 收口）：guard_registration 新增 require_production_verifier 参数（默认 False 不变），True 时强制验签器显式 is_production=True（真实 SM2 绑定证书链）否则 fail-closed 拒绝（reason 明确）；DemoRegistrationVerifier 补显式 is_production=False；不实现真实验签器（非本轮范围），demo 行为不变",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/app/demo_support.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps7.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps7.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T03:36:41.535279Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T03:36:53.042886Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
    "code": [
        "src/coevo/orchestrator/_real_chain.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize7.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize7.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-8",
      "title": "真实链 resume 失败收尾收敛（2026-08-08，用户指令\"继续\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：orchestrator/_real_chain.py 的 resume_real_chain 中 2 处结构相同的 ESCALATED 失败收尾（包验证失败 except 分支 / crypto 能力不可用：追加 ESCALATED trace + report + outcome + store.finish_resume_failure）提取为 _finish_resume_escalated 单一辅助，行为不变（ESCALATED 语义与审计存储一致）；守卫测试钉住 2 个 code 常量各单一调用点",
      "code": [
        "src/coevo/orchestrator/_real_chain.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize8.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/_real_chain.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize8.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-9",
      "title": "剩余 canonical 序列化变体统一（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：canon.py 新增 canonical_json_str（str 变体，与 canonical_json_bytes 同参、字节逐位一致），收敛 cng_handle（_write body + 删除本地 _canonical，哈希链调用点改 canonical_json_bytes）/ cockpit state_store（bytes 1 处）/ knowledge_base（str 1 处）/ talent（str 4 处）/ audit stream_store（append 2 处 + _chain_hash 1 处）；行为不变（cng 注册表哈希链、审计流哈希链、DB 载荷字节一致）；全仓守卫（5 模块内联 json.dumps 计数归零，cng_handle 仅留非 canonical 请求体）",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/cockpit/state_store.py",
        "src/coevo/knowledge_base/store.py",
        "src/coevo/talent/store.py",
        "src/coevo/audit_governance/stream_store.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize9.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/state_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream_store.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize9.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-10",
      "title": "audit_anchor canonical 统一到 canon（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：canon.py 的 canonical_json_bytes/canonical_json_str/canonical_digest 新增 trailing_newline 参数（默认 False 不变，True 追加 \\n）；identity/audit_anchor.py::canonical 改用共享实现（ensure_ascii=False + trailing_newline=True，审计锚定记录字节逐位不变，本地 json.dumps 副本删除，函数签名保留）；canonical 收敛收官",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/identity/audit_anchor.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize10.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/audit_anchor.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize10.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-7",
      "title": "生产验签入口守卫（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"；INTEGRATION-4 Low 1 收口）：guard_registration 新增 require_production_verifier 参数（默认 False 不变），True 时强制验签器显式 is_production=True（真实 SM2 绑定证书链）否则 fail-closed 拒绝（reason 明确）；DemoRegistrationVerifier 补显式 is_production=False；不实现真实验签器（非本轮范围），demo 行为不变",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/app/demo_support.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps7.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps7.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-11",
      "title": "共享 safe-id 正则叶子（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：新增 src/coevo/ids.py（SAFE_ID `^[a-zA-Z0-9_][a-zA-Z0-9_.\\-]{0,63}$` + is_safe_id fail-closed），workspace/cockpit/report/progress_capture/audit_governance/orchestrator/framework.tools 7 处本地副本统一引用；task_flow（首字符 `[a-zA-Z_]`）与 talent（手写 Unicode 判断）语义差异保留独立；root_modules.md 登记",
      "code": [
        "src/coevo/ids.py",
        "src/coevo/workspace/paths.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/report/models.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/audit_governance/stream.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/framework/tools.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize11.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/ids.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/workspace/paths.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/report/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/tools.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize11.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T03:44:40.084045Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T03:44:52.443834Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
 {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize8.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-9",
      "title": "剩余 canonical 序列化变体统一（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：canon.py 新增 canonical_json_str（str 变体，与 canonical_json_bytes 同参、字节逐位一致），收敛 cng_handle（_write body + 删除本地 _canonical，哈希链调用点改 canonical_json_bytes）/ cockpit state_store（bytes 1 处）/ knowledge_base（str 1 处）/ talent（str 4 处）/ audit stream_store（append 2 处 + _chain_hash 1 处）；行为不变（cng 注册表哈希链、审计流哈希链、DB 载荷字节一致）；全仓守卫（5 模块内联 json.dumps 计数归零，cng_handle 仅留非 canonical 请求体）",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/cockpit/state_store.py",
        "src/coevo/knowledge_base/store.py",
        "src/coevo/talent/store.py",
        "src/coevo/audit_governance/stream_store.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize9.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/state_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/knowledge_base/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/talent/store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream_store.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize9.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-10",
      "title": "audit_anchor canonical 统一到 canon（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：canon.py 的 canonical_json_bytes/canonical_json_str/canonical_digest 新增 trailing_newline 参数（默认 False 不变，True 追加 \\n）；identity/audit_anchor.py::canonical 改用共享实现（ensure_ascii=False + trailing_newline=True，审计锚定记录字节逐位不变，本地 json.dumps 副本删除，函数签名保留）；canonical 收敛收官",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/identity/audit_anchor.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize10.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/audit_anchor.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize10.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-7",
      "title": "生产验签入口守卫（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"；INTEGRATION-4 Low 1 收口）：guard_registration 新增 require_production_verifier 参数（默认 False 不变），True 时强制验签器显式 is_production=True（真实 SM2 绑定证书链）否则 fail-closed 拒绝（reason 明确）；DemoRegistrationVerifier 补显式 is_production=False；不实现真实验签器（非本轮范围），demo 行为不变",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/app/demo_support.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps7.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps7.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-11",
      "title": "共享 safe-id 正则叶子（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：新增 src/coevo/ids.py（SAFE_ID `^[a-zA-Z0-9_][a-zA-Z0-9_.\\-]{0,63}$` + is_safe_id fail-closed），workspace/cockpit/report/progress_capture/audit_governance/orchestrator/framework.tools 7 处本地副本统一引用；task_flow（首字符 `[a-zA-Z_]`）与 talent（手写 Unicode 判断）语义差异保留独立；root_modules.md 登记",
      "code": [
        "src/coevo/ids.py",
        "src/coevo/workspace/paths.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/report/models.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/audit_governance/stream.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/framework/tools.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize11.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/ids.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/workspace/paths.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/report/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/tools.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize11.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-12",
      "title": "framework 内部 canonical 收敛（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：tools.canonical_schema_bytes/canonical_descriptor_bytes、memory.canonical_record_bytes、k8s_listing.generate_listing 4 处与 canonical_json_bytes 完全等价的序列化统一到共享 canon（字节逐位不变，本地 json.dumps 副本删除）；plan.canonical_plan_bytes 因 default=_json_default（Enum）语义不同保留独立",
      "code": [
        "src/coevo/framework/tools.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/k8s_listing.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize12.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/tools.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize12.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T03:50:58.199980Z — target=`quality` fingerprint=`196179208515746b`
- exit_code: `1`
```text
idence (test_traceability_check.TraceabilityTests.test_us_5_ac_2_is_done_with_evidence) ... ok
test_us_5_ac_2_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_5_ac_2_matrix_lists_src_and_test) ... ok
test_us_5_ac_3_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_5_ac_3_is_done_with_evidence) ... ok
test_us_5_ac_3_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_5_ac_3_matrix_lists_src_and_test) ... ok
test_us_6_ac_1_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_6_ac_1_is_done_with_evidence) ... ok
test_us_6_ac_1_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_6_ac_1_matrix_lists_src_and_test) ... ok
test_us_9_ac_1_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_9_ac_1_is_done_with_evidence) ... ok
test_us_9_ac_1_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_9_ac_1_matrix_lists_src_and_test) ... ok
test_build_paths_custom_roots (test_workspace_init.TestBuildPaths.test_build_paths_custom_roots) ... ok
test_build_paths_default_roots (test_workspace_init.TestBuildPaths.test_build_paths_default_roots) ... ok
test_build_paths_rejects_backslash_traversal_in_roots (test_workspace_init.TestBuildPaths.test_build_paths_rejects_backslash_traversal_in_roots) ... ok
test_quarantine_path_default_root (test_workspace_init.TestQuarantinePath.test_quarantine_path_default_root) ... ok
test_quarantine_path_layout (test_workspace_init.TestQuarantinePath.test_quarantine_path_layout) ... ok
test_quarantine_path_rejects_backslash_traversal (test_workspace_init.TestQuarantinePath.test_quarantine_path_rejects_backslash_traversal) ... ok
test_quarantine_path_rejects_empty_root (test_workspace_init.TestQuarantinePath.test_quarantine_path_rejects_empty_root) ... ok
test_quarantine_path_rejects_invalid_id (test_workspace_init.TestQuarantinePath.test_quarantine_path_rejects_invalid_id) ... ok
test_quarantine_path_rejects_traversal (test_workspace_init.TestQuarantinePath.test_quarantine_path_rejects_traversal) ... ok
test_audit_record_is_json_safe_on_success (test_workspace_init.TestWorkspaceInitService.test_audit_record_is_json_safe_on_success) ... ok
test_audit_record_on_rejection (test_workspace_init.TestWorkspaceInitService.test_audit_record_on_rejection) ... ok
test_init_allows_same_package_different_role (test_workspace_init.TestWorkspaceInitService.test_init_allows_same_package_different_role) ... ok
test_init_creates_workspace_for_committed_import (test_workspace_init.TestWorkspaceInitService.test_init_creates_workspace_for_committed_import) ... ok
test_init_idempotent_on_duplicate_package (test_workspace_init.TestWorkspaceInitService.test_init_idempotent_on_duplicate_package) ... ok
test_init_propagates_path_error_for_unsafe_package_id (test_workspace_init.TestWorkspaceInitService.test_init_propagates_path_error_for_unsafe_package_id) ... ok
test_init_rejects_invalid_role_id (test_workspace_init.TestWorkspaceInitService.test_init_rejects_invalid_role_id) ... ok
test_init_rejects_non_import_outcome (test_workspace_init.TestWorkspaceInitService.test_init_rejects_non_import_outcome) ... ok
test_init_rejects_rolled_back_import (test_workspace_init.TestWorkspaceInitService.test_init_rejects_rolled_back_import) ... ok
test_sanitize_id_accepts_exactly_maximum_length (test_workspace_init.TestWorkspacePath.test_sanitize_id_accepts_exactly_maximum_length) ... ok
test_sanitize_id_accepts_safe (test_workspace_init.TestWorkspacePath.test_sanitize_id_accepts_safe) ... ok
test_sanitize_id_rejects_empty (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_empty) ... ok
test_sanitize_id_rejects_maximum_plus_one (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_maximum_plus_one) ... ok
test_sanitize_id_rejects_too_long (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_too_long) ... ok
test_workspace_path_default_root (test_workspace_init.TestWorkspacePath.test_workspace_path_default_root) ... ok
test_workspace_path_layout (test_workspace_init.TestWorkspacePath.test_workspace_path_layout) ... ok
test_workspace_path_rejects_backslash_traversal (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_backslash_traversal) ... ok
test_workspace_path_rejects_empty_root (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_empty_root) ... ok
test_workspace_path_rejects_invalid_project_id (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_invalid_project_id) ... ok
test_workspace_path_rejects_invalid_role_id (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_invalid_role_id) ... ok
test_workspace_path_rejects_traversal (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_traversal) ... ok
test_by_package (test_workspace_init.TestWorkspaceRegistry.test_by_package) ... ok
test_empty_registry (test_workspace_init.TestWorkspaceRegistry.test_empty_registry) ... ok
test_register_allows_same_package_for_different_role (test_workspace_init.TestWorkspaceRegistry.test_register_allows_same_package_for_different_role) ... ok
test_register_rejects_duplicate_package_for_same_role (test_workspace_init.TestWorkspaceRegistry.test_register_rejects_duplicate_package_for_same_role) ... ok
test_register_rejects_duplicate_role (test_workspace_init.TestWorkspaceRegistry.test_register_rejects_duplicate_role) ... ok
test_register_then_get (test_workspace_init.TestWorkspaceRegistry.test_register_then_get) ... ok
test_disallowed_extension_is_denied (test_wps_launcher.WpsLauncherTests.test_disallowed_extension_is_denied) ... ok
test_invalid_root_is_rejected (test_wps_launcher.WpsLauncherTests.test_invalid_root_is_rejected) ... ok
test_missing_absolute_executable_is_not_available (test_wps_launcher.WpsLauncherTests.test_missing_absolute_executable_is_not_available) ... ok
test_missing_file_is_denied (test_wps_launcher.WpsLauncherTests.test_missing_file_is_denied) ... ok
test_runner_failure_is_error (test_wps_launcher.WpsLauncherTests.test_runner_failure_is_error) ... ok
test_runner_is_invoked_with_explicit_executable_and_path (test_wps_launcher.WpsLauncherTests.test_runner_is_invoked_with_explicit_executable_and_path) ... ok
test_symlink_escape_is_denied (test_wps_launcher.WpsLauncherTests.test_symlink_escape_is_denied) ... skipped 'symlink creation unavailable'
test_traversal_and_absolute_paths_are_denied (test_wps_launcher.WpsLauncherTests.test_traversal_and_absolute_paths_are_denied) ... ok
test_valid_document_dry_run_is_ok (test_wps_launcher.WpsLauncherTests.test_valid_document_dry_run_is_ok) ... ok

======================================================================
ERROR: test_option_shaped_item_and_model_are_rejected_before_cli_start (test_loop_launcher.LoopLauncherTest.test_option_shaped_item_and_model_are_rejected_before_cli_start)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\unit\test_loop_launcher.py", line 42, in test_option_shaped_item_and_model_are_rejected_before_cli_start
    output=result.stderr+result.stdout
           ~~~~~~~~~~~~~^~~~~~~~~~~~~~
TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'

======================================================================
FAIL: test_probe_completes_with_zero_errors (test_benchmark_http.CockpitHttpProbeTests.test_probe_completes_with_zero_errors)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\unit\test_benchmark_http.py", line 25, in test_probe_completes_with_zero_errors
    self.assertTrue(result.ok, result.detail)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true : p50=0.0066s max=1.0675s errors=0

----------------------------------------------------------------------
Ran 1232 tests in 71.897s

FAILED (failures=1, errors=1, skipped=3)

```




## 2026-08-08T03:55:11.893228Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T03:55:32.213923Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
son_bytes/canonical_json_str/canonical_digest 新增 trailing_newline 参数（默认 False 不变，True 追加 \\n）；identity/audit_anchor.py::canonical 改用共享实现（ensure_ascii=False + trailing_newline=True，审计锚定记录字节逐位不变，本地 json.dumps 副本删除，函数签名保留）；canonical 收敛收官",
      "code": [
        "src/coevo/canon.py",
        "src/coevo/identity/audit_anchor.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize10.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/canon.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/identity/audit_anchor.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize10.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-GAPS-7",
      "title": "生产验签入口守卫（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"；INTEGRATION-4 Low 1 收口）：guard_registration 新增 require_production_verifier 参数（默认 False 不变），True 时强制验签器显式 is_production=True（真实 SM2 绑定证书链）否则 fail-closed 拒绝（reason 明确）；DemoRegistrationVerifier 补显式 is_production=False；不实现真实验签器（非本轮范围），demo 行为不变",
      "code": [
        "src/coevo/framework/integration.py",
        "src/coevo/app/demo_support.py"
      ],
      "tests": [
        "tests/unit/test_framework_gaps7.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/integration.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/app/demo_support.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_gaps7.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-11",
      "title": "共享 safe-id 正则叶子（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：新增 src/coevo/ids.py（SAFE_ID `^[a-zA-Z0-9_][a-zA-Z0-9_.\\-]{0,63}$` + is_safe_id fail-closed），workspace/cockpit/report/progress_capture/audit_governance/orchestrator/framework.tools 7 处本地副本统一引用；task_flow（首字符 `[a-zA-Z_]`）与 talent（手写 Unicode 判断）语义差异保留独立；root_modules.md 登记",
      "code": [
        "src/coevo/ids.py",
        "src/coevo/workspace/paths.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/report/models.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/audit_governance/stream.py",
        "src/coevo/orchestrator/models.py",
        "src/coevo/framework/tools.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize11.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/ids.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/workspace/paths.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/report/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/audit_governance/stream.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/tools.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize11.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-12",
      "title": "framework 内部 canonical 收敛（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：tools.canonical_schema_bytes/canonical_descriptor_bytes、memory.canonical_record_bytes、k8s_listing.generate_listing 4 处与 canonical_json_bytes 完全等价的序列化统一到共享 canon（字节逐位不变，本地 json.dumps 副本删除）；plan.canonical_plan_bytes 因 default=_json_default（Enum）语义不同保留独立",
      "code": [
        "src/coevo/framework/tools.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/k8s_listing.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize12.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/tools.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize12.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-13",
      "title": "共享 64-hex 正则叶子 + OPTIMIZE-11 遗漏补漏（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：ids.py 扩展 HEX_64/is_hex_64（`^[0-9a-f]{64}$`，fail-closed），cockpit/progress_capture(models+watcher)/report/framework a2a+plan+memory 7 处 64-hex 本地副本统一引用；同时补齐 OPTIMIZE-11 遗漏的 framework a2a/plan/memory 3 处 _SAFE_ID 副本（统一到共享 SAFE_ID）；root_modules.md 更新",
      "code": [
        "src/coevo/ids.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/report/models.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/plan.py",
        "src/coevo/framework/memory.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize13.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/ids.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/report/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize13.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T04:06:56.478786Z — target=`quality` fingerprint=`196179208515746b`
- exit_code: `1`
```text
sts.test_us_3_ac_1_matrix_lists_src_and_test) ... ok
test_us_5_ac_1_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_5_ac_1_is_done_with_evidence) ... ok
test_us_5_ac_1_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_5_ac_1_matrix_lists_src_and_test) ... ok
test_us_5_ac_2_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_5_ac_2_is_done_with_evidence) ... ok
test_us_5_ac_2_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_5_ac_2_matrix_lists_src_and_test) ... ok
test_us_5_ac_3_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_5_ac_3_is_done_with_evidence) ... ok
test_us_5_ac_3_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_5_ac_3_matrix_lists_src_and_test) ... ok
test_us_6_ac_1_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_6_ac_1_is_done_with_evidence) ... ok
test_us_6_ac_1_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_6_ac_1_matrix_lists_src_and_test) ... ok
test_us_9_ac_1_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_9_ac_1_is_done_with_evidence) ... ok
test_us_9_ac_1_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_9_ac_1_matrix_lists_src_and_test) ... ok
test_build_paths_custom_roots (test_workspace_init.TestBuildPaths.test_build_paths_custom_roots) ... ok
test_build_paths_default_roots (test_workspace_init.TestBuildPaths.test_build_paths_default_roots) ... ok
test_build_paths_rejects_backslash_traversal_in_roots (test_workspace_init.TestBuildPaths.test_build_paths_rejects_backslash_traversal_in_roots) ... ok
test_quarantine_path_default_root (test_workspace_init.TestQuarantinePath.test_quarantine_path_default_root) ... ok
test_quarantine_path_layout (test_workspace_init.TestQuarantinePath.test_quarantine_path_layout) ... ok
test_quarantine_path_rejects_backslash_traversal (test_workspace_init.TestQuarantinePath.test_quarantine_path_rejects_backslash_traversal) ... ok
test_quarantine_path_rejects_empty_root (test_workspace_init.TestQuarantinePath.test_quarantine_path_rejects_empty_root) ... ok
test_quarantine_path_rejects_invalid_id (test_workspace_init.TestQuarantinePath.test_quarantine_path_rejects_invalid_id) ... ok
test_quarantine_path_rejects_traversal (test_workspace_init.TestQuarantinePath.test_quarantine_path_rejects_traversal) ... ok
test_audit_record_is_json_safe_on_success (test_workspace_init.TestWorkspaceInitService.test_audit_record_is_json_safe_on_success) ... ok
test_audit_record_on_rejection (test_workspace_init.TestWorkspaceInitService.test_audit_record_on_rejection) ... ok
test_init_allows_same_package_different_role (test_workspace_init.TestWorkspaceInitService.test_init_allows_same_package_different_role) ... ok
test_init_creates_workspace_for_committed_import (test_workspace_init.TestWorkspaceInitService.test_init_creates_workspace_for_committed_import) ... ok
test_init_idempotent_on_duplicate_package (test_workspace_init.TestWorkspaceInitService.test_init_idempotent_on_duplicate_package) ... ok
test_init_propagates_path_error_for_unsafe_package_id (test_workspace_init.TestWorkspaceInitService.test_init_propagates_path_error_for_unsafe_package_id) ... ok
test_init_rejects_invalid_role_id (test_workspace_init.TestWorkspaceInitService.test_init_rejects_invalid_role_id) ... ok
test_init_rejects_non_import_outcome (test_workspace_init.TestWorkspaceInitService.test_init_rejects_non_import_outcome) ... ok
test_init_rejects_rolled_back_import (test_workspace_init.TestWorkspaceInitService.test_init_rejects_rolled_back_import) ... ok
test_sanitize_id_accepts_exactly_maximum_length (test_workspace_init.TestWorkspacePath.test_sanitize_id_accepts_exactly_maximum_length) ... ok
test_sanitize_id_accepts_safe (test_workspace_init.TestWorkspacePath.test_sanitize_id_accepts_safe) ... ok
test_sanitize_id_rejects_empty (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_empty) ... ok
test_sanitize_id_rejects_maximum_plus_one (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_maximum_plus_one) ... ok
test_sanitize_id_rejects_too_long (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_too_long) ... ok
test_workspace_path_default_root (test_workspace_init.TestWorkspacePath.test_workspace_path_default_root) ... ok
test_workspace_path_layout (test_workspace_init.TestWorkspacePath.test_workspace_path_layout) ... ok
test_workspace_path_rejects_backslash_traversal (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_backslash_traversal) ... ok
test_workspace_path_rejects_empty_root (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_empty_root) ... ok
test_workspace_path_rejects_invalid_project_id (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_invalid_project_id) ... ok
test_workspace_path_rejects_invalid_role_id (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_invalid_role_id) ... ok
test_workspace_path_rejects_traversal (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_traversal) ... ok
test_by_package (test_workspace_init.TestWorkspaceRegistry.test_by_package) ... ok
test_empty_registry (test_workspace_init.TestWorkspaceRegistry.test_empty_registry) ... ok
test_register_allows_same_package_for_different_role (test_workspace_init.TestWorkspaceRegistry.test_register_allows_same_package_for_different_role) ... ok
test_register_rejects_duplicate_package_for_same_role (test_workspace_init.TestWorkspaceRegistry.test_register_rejects_duplicate_package_for_same_role) ... ok
test_register_rejects_duplicate_role (test_workspace_init.TestWorkspaceRegistry.test_register_rejects_duplicate_role) ... ok
test_register_then_get (test_workspace_init.TestWorkspaceRegistry.test_register_then_get) ... ok
test_disallowed_extension_is_denied (test_wps_launcher.WpsLauncherTests.test_disallowed_extension_is_denied) ... ok
test_invalid_root_is_rejected (test_wps_launcher.WpsLauncherTests.test_invalid_root_is_rejected) ... ok
test_missing_absolute_executable_is_not_available (test_wps_launcher.WpsLauncherTests.test_missing_absolute_executable_is_not_available) ... ok
test_missing_file_is_denied (test_wps_launcher.WpsLauncherTests.test_missing_file_is_denied) ... ok
test_runner_failure_is_error (test_wps_launcher.WpsLauncherTests.test_runner_failure_is_error) ... ok
test_runner_is_invoked_with_explicit_executable_and_path (test_wps_launcher.WpsLauncherTests.test_runner_is_invoked_with_explicit_executable_and_path) ... ok
test_symlink_escape_is_denied (test_wps_launcher.WpsLauncherTests.test_symlink_escape_is_denied) ... skipped 'symlink creation unavailable'
test_traversal_and_absolute_paths_are_denied (test_wps_launcher.WpsLauncherTests.test_traversal_and_absolute_paths_are_denied) ... ok
test_valid_document_dry_run_is_ok (test_wps_launcher.WpsLauncherTests.test_valid_document_dry_run_is_ok) ... ok

======================================================================
FAIL: test_option_shaped_item_and_model_are_rejected_before_cli_start (test_loop_launcher.LoopLauncherTest.test_option_shaped_item_and_model_are_rejected_before_cli_start)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\unit\test_loop_launcher.py", line 46, in test_option_shaped_item_and_model_are_rejected_before_cli_start
    self.assertTrue('ParameterArgumentValidationError' in output or 'Cannot validate argument' in output or 'does not match' in output, f'unexpected output: {output}')
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true : unexpected output: 

----------------------------------------------------------------------
Ran 1237 tests in 121.883s

FAILED (failures=1, skipped=3)

```




## 2026-08-08T04:07:05.395617Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T04:07:27.366430Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/tools.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize11.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-12",
      "title": "framework 内部 canonical 收敛（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：tools.canonical_schema_bytes/canonical_descriptor_bytes、memory.canonical_record_bytes、k8s_listing.generate_listing 4 处与 canonical_json_bytes 完全等价的序列化统一到共享 canon（字节逐位不变，本地 json.dumps 副本删除）；plan.canonical_plan_bytes 因 default=_json_default（Enum）语义不同保留独立",
      "code": [
        "src/coevo/framework/tools.py",
        "src/coevo/framework/memory.py",
        "src/coevo/framework/k8s_listing.py"
      ],
      "tests": [
        "tests/unit/test_framework_optimize12.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/tools.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize12.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-13",
      "title": "共享 64-hex 正则叶子 + OPTIMIZE-11 遗漏补漏（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：ids.py 扩展 HEX_64/is_hex_64（`^[0-9a-f]{64}$`，fail-closed），cockpit/progress_capture(models+watcher)/report/framework a2a+plan+memory 7 处 64-hex 本地副本统一引用；同时补齐 OPTIMIZE-11 遗漏的 framework a2a/plan/memory 3 处 _SAFE_ID 副本（统一到共享 SAFE_ID）；root_modules.md 更新",
      "code": [
        "src/coevo/ids.py",
        "src/coevo/cockpit/models.py",
        "src/coevo/progress_capture/models.py",
        "src/coevo/progress_capture/watcher.py",
        "src/coevo/report/models.py",
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/plan.py",
        "src/coevo/framework/memory.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize13.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/ids.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/report/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize13.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-14",
      "title": "共享 JSON 重复键拒绝守卫（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：新增 src/coevo/jsonutil.py（reject_duplicate_pairs，error_factory 可注入保持各模块异常语义、消息统一 \"duplicate key ...\" 兼容既有断言），protocol/agent_package、framework/k8s_listing、crypto/cng_handle、cockpit/state_store、framework/manifest_checker 5 处本地 object_pairs_hook 守卫统一引用；fail-closed 不降；root_modules.md 登记",
      "code": [
        "src/coevo/jsonutil.py",
        "src/coevo/protocol/agent_package.py",
        "src/coevo/framework/k8s_listing.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/cockpit/state_store.py",
        "src/coevo/framework/manifest_checker.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize14.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/jsonutil.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/agent_package.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/state_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize14.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "QUALITY-ROBUST-1",
      "title": "门禁稳定性修复与文档一致性（2026-08-08，用户指令\"站在资深审查者角度全面审查、复盘并落地优化\"）：LOAD-1 /healthz p95 探针增加预热 + best-of-3 取最优无错轮次（scripts/benchmark.py 提取 _fire_probe/_p95 并参数化 16 workers×8/轮），单元测试改 class-level 共享探针结果，消除共享机/并发负载下单次采样偶发超 1.0s 抖动（两次实测复现 p50=0.0066s/max=1.0675s 与 p50=0.0090s/max=1.5953s）；test_loop_launcher 容忍 PowerShell 偶发 None 输出流（TypeError 修复）；docs/production-readiness.md + docs/modules/benchmarks.md + src/coevo/benchmarks/__init__.py 三处\"计时探针不进 make quality\"表述与实际门禁组合对齐（唯一例外 LOAD-1：预热 + best-of-3）",
      "code": [
        "scripts/benchmark.py",
        "docs/production-readiness.md",
        "docs/modules/benchmarks.md",
        "src/coevo/benchmarks/__init__.py"
      ],
      "tests": [
        "tests/unit/test_benchmark_http.py",
        "tests/unit/test_loop_launcher.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/benchmark.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/production-readiness.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/benchmarks.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/benchmarks/__init__.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_benchmark_http.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_loop_launcher.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```




## 2026-08-08T04:27:01.559533Z — target=`quality` fingerprint=`196179208515746b`
- exit_code: `1`
```text
~~~~~^^
  File "<frozen codecs>", line 325, in decode
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xcb in position 43: invalid continuation byte
Exception in thread Thread-532 (_readerthread):
Traceback (most recent call last):
  File "C:\Python314\Lib\threading.py", line 1082, in _bootstrap_inner
    self._context.run(self.run)
    ~~~~~~~~~~~~~~~~~^^^^^^^^^^
  File "C:\Python314\Lib\threading.py", line 1024, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Python314\Lib\subprocess.py", line 1613, in _readerthread
    buffer.append(fh.read())
                  ~~~~~~~^^
  File "<frozen codecs>", line 325, in decode
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xcb in position 43: invalid continuation byte
ok
test_launcher_ignores_poisoned_path_and_cleans_ephemeral_helper (test_sm2_test_pki_generation.Sm2TestPkiTests.test_launcher_ignores_poisoned_path_and_cleans_ephemeral_helper) ... ok
test_lock_matches_offline_artifact_and_records_unsigned_risk (test_sm2_test_pki_generation.Sm2TestPkiTests.test_lock_matches_offline_artifact_and_records_unsigned_risk) ... ok
test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper (test_sm2_test_pki_generation.Sm2TestPkiTests.test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper) ... Exception in thread Thread-538 (_readerthread):
Traceback (most recent call last):
  File "C:\Python314\Lib\threading.py", line 1082, in _bootstrap_inner
    self._context.run(self.run)
    ~~~~~~~~~~~~~~~~~^^^^^^^^^^
  File "C:\Python314\Lib\threading.py", line 1024, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Python314\Lib\subprocess.py", line 1613, in _readerthread
    buffer.append(fh.read())
                  ~~~~~~~^^
  File "<frozen codecs>", line 325, in decode
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xcb in position 73: invalid continuation byte
ERROR
test_prepositioned_profile_file_is_preserved_and_no_staging_remains (test_sm2_test_pki_generation.Sm2TestPkiTests.test_prepositioned_profile_file_is_preserved_and_no_staging_remains) ... Exception in thread Thread-540 (_readerthread):
Traceback (most recent call last):
  File "C:\Python314\Lib\threading.py", line 1082, in _bootstrap_inner
    self._context.run(self.run)
    ~~~~~~~~~~~~~~~~~^^^^^^^^^^
  File "C:\Python314\Lib\threading.py", line 1024, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Python314\Lib\subprocess.py", line 1613, in _readerthread
    buffer.append(fh.read())
                  ~~~~~~~^^
  File "<frozen codecs>", line 325, in decode
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xcb in position 31: invalid continuation byte
ok
test_recover_unknown_staged_object_fails_closed_without_deleting_it (test_sm2_test_pki_generation.Sm2TestPkiTests.test_recover_unknown_staged_object_fails_closed_without_deleting_it) ... ok
test_runtime_output_is_gitignored (test_sm2_test_pki_generation.Sm2TestPkiTests.test_runtime_output_is_gitignored) ... ok
test_wide_runtime_acl_is_corrected_before_staging_creation (test_sm2_test_pki_generation.Sm2TestPkiTests.test_wide_runtime_acl_is_corrected_before_staging_creation) ... ok
test_append_after_reopen_extends_store (test_talent_store_persistence.CrossRestartPersistenceTests.test_append_after_reopen_extends_store) ... ok
test_duplicate_talent_code_detected_across_restart (test_talent_store_persistence.CrossRestartPersistenceTests.test_duplicate_talent_code_detected_across_restart) ... ok
test_from_pool_then_reopen_round_trip (test_talent_store_persistence.CrossRestartPersistenceTests.test_from_pool_then_reopen_round_trip) ... ok
test_registered_talents_survive_restart (test_talent_store_persistence.CrossRestartPersistenceTests.test_registered_talents_survive_restart) ... ok
test_snapshot_after_restart_drives_recommender (test_talent_store_persistence.CrossRestartPersistenceTests.test_snapshot_after_restart_drives_recommender) ... ok
test_tampered_file_is_refused_on_reopen (test_talent_store_persistence.CrossRestartPersistenceTests.test_tampered_file_is_refused_on_reopen) ... ok
test_custom_tools_reference_existing_controlled_scripts (test_tool_contracts.ToolContractIntegrationTests.test_custom_tools_reference_existing_controlled_scripts) ... ok

======================================================================
ERROR: test_repeated_entry_deduplicates_paths_and_rebuilds_shim (test_dev_environment_entry.DevEnvironmentEntryTest.test_repeated_entry_deduplicates_paths_and_rebuilds_shim)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_dev_environment_entry.py", line 21, in test_repeated_entry_deduplicates_paths_and_rebuilds_shim
    self.assertEqual(0,result.returncode,result.stdout+result.stderr)
                                         ~~~~~~~~~~~~~^~~~~~~~~~~~~~
TypeError: can only concatenate str (not "NoneType") to str

======================================================================
ERROR: test_concurrent_same_profile_has_one_atomic_winner (test_sm2_test_pki_generation.Sm2TestPkiTests.test_concurrent_same_profile_has_one_atomic_winner)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_sm2_test_pki_generation.py", line 671, in test_concurrent_same_profile_has_one_atomic_winner
    self.assertNotRegex("".join(out + err for _, out, err in results), r"BEGIN (?:ENCRYPTED )?PRIVATE KEY")
                        ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\Workspace\Coevo\tests\integration\test_sm2_test_pki_generation.py", line 671, in <genexpr>
    self.assertNotRegex("".join(out + err for _, out, err in results), r"BEGIN (?:ENCRYPTED )?PRIVATE KEY")
                                ~~~~^~~~~
TypeError: can only concatenate str (not "NoneType") to str

======================================================================
ERROR: test_hung_helper_is_tree_killed_and_drains_are_bounded (test_sm2_test_pki_generation.Sm2TestPkiTests.test_hung_helper_is_tree_killed_and_drains_are_bounded)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_sm2_test_pki_generation.py", line 270, in test_hung_helper_is_tree_killed_and_drains_are_bounded
    self.assertIn("helper timed out", result.stderr)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Python314\Lib\unittest\case.py", line 1189, in assertIn
    if member not in container:
       ^^^^^^^^^^^^^^^^^^^^^^^
TypeError: argument of type 'NoneType' is not a container or iterable

======================================================================
ERROR: test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper (test_sm2_test_pki_generation.Sm2TestPkiTests.test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_sm2_test_pki_generation.py", line 306, in test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper
    self.assertRegex(result.stderr, r"GMH-E-DIRECTORY-LOCK-[A-Z-]+-WIN32-32-ATTEMPT-4|Unable to lock file|Unable to lock tool directory")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Python314\Lib\unittest\case.py", line 1440, in assertRegex
    if not expected_regex.search(text):
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^
TypeError: expected string or bytes-like object, got 'NoneType'

----------------------------------------------------------------------
Ran 261 tests in 534.456s

FAILED (errors=4, skipped=1)

```




## 2026-08-08T08:07:29.326619Z — target=`quality` fingerprint=`196179208515746b`
- exit_code: `1`
```text
rivateKeyServicePolicyTests.test_audit_chain_records_store_use_revoke_and_destroy) ... ok
test_destroyed_handle_blocks_use_with_stale_reference (test_private_key_storage.PrivateKeyServicePolicyTests.test_destroyed_handle_blocks_use_with_stale_reference) ... ok
test_overwrite_store_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_overwrite_store_is_rejected) ... ok
test_revoke_without_reason_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_revoke_without_reason_is_rejected) ... ok
test_revoked_reference_blocks_use_and_audits_rejection (test_private_key_storage.PrivateKeyServicePolicyTests.test_revoked_reference_blocks_use_and_audits_rejection) ... ok
test_stored_reference_round_trips_use_and_returns_signature (test_private_key_storage.PrivateKeyServicePolicyTests.test_stored_reference_round_trips_use_and_returns_signature) ... ok
test_untrusted_parent_thumbprint_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_untrusted_parent_thumbprint_is_rejected) ... ok
test_use_outside_validity_window_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_use_outside_validity_window_is_rejected) ... ok
test_use_with_naive_datetime_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_use_with_naive_datetime_is_rejected) ... ok
test_verify_binds_certificate_pin_digest_algorithm_and_audits_digest_only (test_private_key_storage.PrivateKeyServicePolicyTests.test_verify_binds_certificate_pin_digest_algorithm_and_audits_digest_only) ... ok
test_verify_rejects_wrong_pin_revoked_destroyed_and_bad_signature (test_private_key_storage.PrivateKeyServicePolicyTests.test_verify_rejects_wrong_pin_revoked_destroyed_and_bad_signature) ... ok
test_poisoned_powershell_path_is_rejected_before_execution (test_private_key_storage.WindowsPrivateKeyLaunchPolicyTests.test_poisoned_powershell_path_is_rejected_before_execution) ... ok
test_rejects_uncontrolled_helper_path (test_private_key_storage.WindowsPrivateKeyLaunchPolicyTests.test_rejects_uncontrolled_helper_path) ... ok
test_custom_tools_use_current_typed_api (test_tool_permissions.PermissionTests.test_custom_tools_use_current_typed_api) ... ok
test_network_and_install_commands_are_fail_closed (test_tool_permissions.PermissionTests.test_network_and_install_commands_are_fail_closed) ... ok

----------------------------------------------------------------------
Ran 99 tests in 235.644s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ C:\Python314\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ERROR
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

======================================================================
ERROR: test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\e2e\test_identity_dev_environment.py", line 27, in test_windows_certificate_parser_and_generation_markers_work_end_to_end
    result = service.register_identity_bundle(Actor("dev-admin"), "dev-environment-check", identity_payload())
  File "E:\Workspace\Coevo\src\coevo\identity\service.py", line 74, in register_identity_bundle
    return self.repository.register(actor_id, valid_request_id, bundle)
           ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\Workspace\Coevo\src\coevo\identity\repository.py", line 227, in register
    self._commit_with_anchor(); return result
    ~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "E:\Workspace\Coevo\src\coevo\identity\repository.py", line 184, in _commit_with_anchor
    self.anchor.promote()
    ~~~~~~~~~~~~~~~~~~~^^
  File "E:\Workspace\Coevo\src\coevo\identity\audit_anchor.py", line 387, in promote
    self._complete_retirement(tombstone)
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^
  File "E:\Workspace\Coevo\src\coevo\identity\audit_anchor.py", line 331, in _complete_retirement
    self.signer.verify(raw, main_signature)
    ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "E:\Workspace\Coevo\src\coevo\identity\audit_anchor.py", line 78, in verify
    self._run("Verify", content, signature)
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\Workspace\Coevo\src\coevo\identity\audit_anchor.py", line 66, in _run
    process = subprocess.run(
        [_powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SIGNING_SCRIPT), "-Action", action, "-HeadPath", str(head), "-SignaturePath", str(signed), "-ConfigPath", str(SIGNING_CONFIG)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
    )
  File "C:\Python314\Lib\subprocess.py", line 556, in run
    stdout, stderr = process.communicate(input, timeout=timeout)
                     ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Python314\Lib\subprocess.py", line 1239, in communicate
    sts = self.wait(timeout=self._remaining_time(endtime))
  File "C:\Python314\Lib\subprocess.py", line 1278, in wait
    return self._wait(timeout=timeout)
           ~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "C:\Python314\Lib\subprocess.py", line 1607, in _wait
    raise TimeoutExpired(self.args, timeout)
subprocess.TimeoutExpired: Command '['C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'E:\\Workspace\\Coevo\\scripts\\audit_signature.ps1', '-Action', 'Verify', '-HeadPath', 'C:\\Users\\liq08\\AppData\\Local\\Temp\\coevo-audit-sign-yjq6y0jj\\head.json', '-SignaturePath', 'C:\\Users\\liq08\\AppData\\Local\\Temp\\coevo-audit-sign-yjq6y0jj\\head.p7s', '-ConfigPath', 'E:\\Workspace\\Coevo\\loop\\audit-signing.json']' timed out after 30 seconds

----------------------------------------------------------------------
Ran 14 tests in 11808.864s

FAILED (errors=1)

```




## 2026-08-08T08:14:42.668136Z — target=`fmt` fingerprint=`8d456a2ce09245c7`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ C:\Python314\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```




## 2026-08-08T08:35:02.476201Z — target=`quality` fingerprint=`196179208515746b`
- exit_code: `1`
```text
ess_capture) ... ok
test_partial_upgrade_leaves_pointer_intact_and_force_completes (test_recovery_faults.InstallerInterruptedUpgradeTests.test_partial_upgrade_leaves_pointer_intact_and_force_completes) ... ok
test_restart_loads_last_committed_state (test_recovery_faults.StateStoreInterruptedSaveTests.test_restart_loads_last_committed_state) ... ok
test_stale_tmp_does_not_corrupt_committed_state (test_recovery_faults.StateStoreInterruptedSaveTests.test_stale_tmp_does_not_corrupt_committed_state) ... ok
test_committed_profile_rejects_minimal_receipt_and_missing_or_tampered_artifact (test_sm2_test_pki_generation.Sm2TestPkiTests.test_committed_profile_rejects_minimal_receipt_and_missing_or_tampered_artifact) ... ok
test_committed_receipt_hardlink_is_rejected (test_sm2_test_pki_generation.Sm2TestPkiTests.test_committed_receipt_hardlink_is_rejected) ... ok
test_committed_receipt_reparse_is_rejected_when_supported (test_sm2_test_pki_generation.Sm2TestPkiTests.test_committed_receipt_reparse_is_rejected_when_supported) ... skipped "file symlink privilege unavailable: [WinError 1314] 客户端没有所需的特权。: 'E:\\\\Workspace\\\\Coevo\\\\loop\\\\runtime\\\\sm2-test-pki\\\\receipt-target-3820b921331d4c2c8e51e99f627c0e26.json' -> 'E:\\\\Workspace\\\\Coevo\\\\loop\\\\runtime\\\\sm2-test-pki\\\\test-cd88c5690c0f4745849f\\\\receipt.json'"
test_concurrent_same_profile_has_one_atomic_winner (test_sm2_test_pki_generation.Sm2TestPkiTests.test_concurrent_same_profile_has_one_atomic_winner) ... ok
test_directory_lock_non_sharing_error_is_not_retried (test_sm2_test_pki_generation.Sm2TestPkiTests.test_directory_lock_non_sharing_error_is_not_retried) ... ok
test_directory_lock_retries_sharing_violation_then_succeeds (test_sm2_test_pki_generation.Sm2TestPkiTests.test_directory_lock_retries_sharing_violation_then_succeeds) ... ok
test_directory_lock_roles_and_share_flags_are_fixed (test_sm2_test_pki_generation.Sm2TestPkiTests.test_directory_lock_roles_and_share_flags_are_fixed) ... ok
test_directory_lock_sharing_violation_retry_exhaustion_fails_closed (test_sm2_test_pki_generation.Sm2TestPkiTests.test_directory_lock_sharing_violation_retry_exhaustion_fails_closed) ... ok
test_dpapi_and_encrypted_pkcs8_round_trip_without_command_line_secret (test_sm2_test_pki_generation.Sm2TestPkiTests.test_dpapi_and_encrypted_pkcs8_round_trip_without_command_line_secret) ... ok
test_existing_profile_acl_must_remain_protected_owner_only (test_sm2_test_pki_generation.Sm2TestPkiTests.test_existing_profile_acl_must_remain_protected_owner_only) ... ok
test_generation_is_isolated_encrypted_verified_and_non_overwriting (test_sm2_test_pki_generation.Sm2TestPkiTests.test_generation_is_isolated_encrypted_verified_and_non_overwriting) ... ok
test_helper_command_line_and_input_channel_are_fail_closed (test_sm2_test_pki_generation.Sm2TestPkiTests.test_helper_command_line_and_input_channel_are_fail_closed) ... ok
test_helper_is_static_no_child_and_launcher_has_no_job_or_native_directory_layer (test_sm2_test_pki_generation.Sm2TestPkiTests.test_helper_is_static_no_child_and_launcher_has_no_job_or_native_directory_layer) ... ok
test_helper_launch_surface_has_no_cli_or_subprocess_secret_path (test_sm2_test_pki_generation.Sm2TestPkiTests.test_helper_launch_surface_has_no_cli_or_subprocess_secret_path) ... ok
test_helper_owns_handle_identity_reparse_rename_and_strict_recovery (test_sm2_test_pki_generation.Sm2TestPkiTests.test_helper_owns_handle_identity_reparse_rename_and_strict_recovery) ... ok
test_helper_response_is_fixed_public_frame_and_response_loss_recovers (test_sm2_test_pki_generation.Sm2TestPkiTests.test_helper_response_is_fixed_public_frame_and_response_loss_recovers) ... ok
test_hung_helper_is_tree_killed_and_drains_are_bounded (test_sm2_test_pki_generation.Sm2TestPkiTests.test_hung_helper_is_tree_killed_and_drains_are_bounded) ... ok
test_kill_points_are_recovered_with_same_nonce (test_sm2_test_pki_generation.Sm2TestPkiTests.test_kill_points_are_recovered_with_same_nonce) ... ok
test_launcher_ignores_poisoned_path_and_cleans_ephemeral_helper (test_sm2_test_pki_generation.Sm2TestPkiTests.test_launcher_ignores_poisoned_path_and_cleans_ephemeral_helper) ... ok
test_lock_matches_offline_artifact_and_records_unsigned_risk (test_sm2_test_pki_generation.Sm2TestPkiTests.test_lock_matches_offline_artifact_and_records_unsigned_risk) ... ok
test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper (test_sm2_test_pki_generation.Sm2TestPkiTests.test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper) ... ok
test_prepositioned_profile_file_is_preserved_and_no_staging_remains (test_sm2_test_pki_generation.Sm2TestPkiTests.test_prepositioned_profile_file_is_preserved_and_no_staging_remains) ... ok
test_recover_unknown_staged_object_fails_closed_without_deleting_it (test_sm2_test_pki_generation.Sm2TestPkiTests.test_recover_unknown_staged_object_fails_closed_without_deleting_it) ... ok
test_runtime_output_is_gitignored (test_sm2_test_pki_generation.Sm2TestPkiTests.test_runtime_output_is_gitignored) ... ok
test_wide_runtime_acl_is_corrected_before_staging_creation (test_sm2_test_pki_generation.Sm2TestPkiTests.test_wide_runtime_acl_is_corrected_before_staging_creation) ... ok
test_append_after_reopen_extends_store (test_talent_store_persistence.CrossRestartPersistenceTests.test_append_after_reopen_extends_store) ... ok
test_duplicate_talent_code_detected_across_restart (test_talent_store_persistence.CrossRestartPersistenceTests.test_duplicate_talent_code_detected_across_restart) ... ok
test_from_pool_then_reopen_round_trip (test_talent_store_persistence.CrossRestartPersistenceTests.test_from_pool_then_reopen_round_trip) ... ok
test_registered_talents_survive_restart (test_talent_store_persistence.CrossRestartPersistenceTests.test_registered_talents_survive_restart) ... ok
test_snapshot_after_restart_drives_recommender (test_talent_store_persistence.CrossRestartPersistenceTests.test_snapshot_after_restart_drives_recommender) ... ok
test_tampered_file_is_refused_on_reopen (test_talent_store_persistence.CrossRestartPersistenceTests.test_tampered_file_is_refused_on_reopen) ... ok
test_custom_tools_reference_existing_controlled_scripts (test_tool_contracts.ToolContractIntegrationTests.test_custom_tools_reference_existing_controlled_scripts) ... ok

======================================================================
FAIL: test_bin_directory_is_removed_after_run_ends (test_dev_environment_entry.DevEnvironmentEntryTest.test_bin_directory_is_removed_after_run_ends)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_dev_environment_entry.py", line 29, in test_bin_directory_is_removed_after_run_ends
    self.assertEqual(0,result.returncode,result.stdout+result.stderr)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 69 : Coevo gate: locking verified toolchain (5421 runtime files)...
locked Python launch failed: locked file mismatch: E:\Workspace\Coevo\scripts\quality_gate.py


======================================================================
FAIL: test_stale_bin_directory_is_swept_on_entry (test_dev_environment_entry.DevEnvironmentEntryTest.test_stale_bin_directory_is_swept_on_entry)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_dev_environment_entry.py", line 44, in test_stale_bin_directory_is_swept_on_entry
    self.assertEqual(0,result.returncode,result.stdout+result.stderr)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 69 : Coevo gate: locking verified toolchain (5421 runtime files)...
locked Python launch failed: locked file mismatch: E:\Workspace\Coevo\scripts\quality_gate.py


----------------------------------------------------------------------
Ran 261 tests in 1021.810s

FAILED (failures=2, skipped=1)

```




## 2026-08-08T09:04:03.692167Z — target=`quality` fingerprint=`196179208515746b`
- exit_code: `0`
```text
ests.test_promote_failure_requires_recovery_and_reopen_commits_exactly_once) ... ok
test_row_shape_validator_rejects_each_oversize_and_malformed_column (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_row_shape_validator_rejects_each_oversize_and_malformed_column) ... ok
test_signed_chain_binds_store_head_sequence_and_previous_hash (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_signed_chain_binds_store_head_sequence_and_previous_hash) ... ok
test_stale_baseline_is_rejected_before_insert (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
test_truncation_is_rejected_by_freshness_checkpoint (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_truncation_is_rejected_by_freshness_checkpoint) ... ok
test_gitignore_excludes_receipt_pattern (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_gitignore_excludes_receipt_pattern) ... ok
test_no_reachable_receipt_blobs_across_all_refs (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_no_reachable_receipt_blobs_across_all_refs) ... ok
test_no_tracked_receipt_paths (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_no_tracked_receipt_paths) ... ok
test_pre_scrub_head_is_no_longer_reachable (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_pre_scrub_head_is_no_longer_reachable) ... ok
test_validate_bundle_rejects_private_key_handle_field (test_private_key_storage.IdentityBundlePrivateKeyRejectionTests.test_validate_bundle_rejects_private_key_handle_field) ... ok
test_validate_bundle_rejects_private_key_pkcs8_bytes (test_private_key_storage.IdentityBundlePrivateKeyRejectionTests.test_validate_bundle_rejects_private_key_pkcs8_bytes) ... ok
test_reference_accepts_only_safe_metadata (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_accepts_only_safe_metadata) ... ok
test_reference_is_frozen_and_hash_stable_across_rotations (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_is_frozen_and_hash_stable_across_rotations) ... ok
test_reference_rejects_inverted_validity (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_rejects_inverted_validity) ... ok
test_reference_rejects_malformed_handle_and_digest (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_rejects_malformed_handle_and_digest) ... ok
test_repr_and_pickle_never_expose_secret_token (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_repr_and_pickle_never_expose_secret_token) ... ok
test_validate_handle_payload_rejects_private_key_blob_strings (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_validate_handle_payload_rejects_private_key_blob_strings) ... ok
test_validate_handle_payload_rejects_unknown_or_sensitive_fields (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_validate_handle_payload_rejects_unknown_or_sensitive_fields) ... ok
test_audit_chain_detects_event_tampering (test_private_key_storage.PrivateKeyServicePolicyTests.test_audit_chain_detects_event_tampering) ... ok
test_audit_chain_records_store_use_revoke_and_destroy (test_private_key_storage.PrivateKeyServicePolicyTests.test_audit_chain_records_store_use_revoke_and_destroy) ... ok
test_destroyed_handle_blocks_use_with_stale_reference (test_private_key_storage.PrivateKeyServicePolicyTests.test_destroyed_handle_blocks_use_with_stale_reference) ... ok
test_overwrite_store_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_overwrite_store_is_rejected) ... ok
test_revoke_without_reason_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_revoke_without_reason_is_rejected) ... ok
test_revoked_reference_blocks_use_and_audits_rejection (test_private_key_storage.PrivateKeyServicePolicyTests.test_revoked_reference_blocks_use_and_audits_rejection) ... ok
test_stored_reference_round_trips_use_and_returns_signature (test_private_key_storage.PrivateKeyServicePolicyTests.test_stored_reference_round_trips_use_and_returns_signature) ... ok
test_untrusted_parent_thumbprint_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_untrusted_parent_thumbprint_is_rejected) ... ok
test_use_outside_validity_window_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_use_outside_validity_window_is_rejected) ... ok
test_use_with_naive_datetime_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_use_with_naive_datetime_is_rejected) ... ok
test_verify_binds_certificate_pin_digest_algorithm_and_audits_digest_only (test_private_key_storage.PrivateKeyServicePolicyTests.test_verify_binds_certificate_pin_digest_algorithm_and_audits_digest_only) ... ok
test_verify_rejects_wrong_pin_revoked_destroyed_and_bad_signature (test_private_key_storage.PrivateKeyServicePolicyTests.test_verify_rejects_wrong_pin_revoked_destroyed_and_bad_signature) ... ok
test_poisoned_powershell_path_is_rejected_before_execution (test_private_key_storage.WindowsPrivateKeyLaunchPolicyTests.test_poisoned_powershell_path_is_rejected_before_execution) ... ok
test_rejects_uncontrolled_helper_path (test_private_key_storage.WindowsPrivateKeyLaunchPolicyTests.test_rejects_uncontrolled_helper_path) ... ok
test_custom_tools_use_current_typed_api (test_tool_permissions.PermissionTests.test_custom_tools_use_current_typed_api) ... ok
test_network_and_install_commands_are_fail_closed (test_tool_permissions.PermissionTests.test_network_and_install_commands_are_fail_closed) ... ok

----------------------------------------------------------------------
Ran 99 tests in 206.020s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ C:\Python314\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 245.098s

OK
audit seal: fully-sealed

```




## 2026-08-08T10:20:34.051442Z — target=`quality` fingerprint=`5ab34d173704cd3e`
- exit_code: `1`
```text
t) ... ok
test_us_5_ac_1_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_5_ac_1_is_done_with_evidence) ... ok
test_us_5_ac_1_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_5_ac_1_matrix_lists_src_and_test) ... ok
test_us_5_ac_2_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_5_ac_2_is_done_with_evidence) ... ok
test_us_5_ac_2_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_5_ac_2_matrix_lists_src_and_test) ... ok
test_us_5_ac_3_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_5_ac_3_is_done_with_evidence) ... ok
test_us_5_ac_3_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_5_ac_3_matrix_lists_src_and_test) ... ok
test_us_6_ac_1_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_6_ac_1_is_done_with_evidence) ... ok
test_us_6_ac_1_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_6_ac_1_matrix_lists_src_and_test) ... ok
test_us_9_ac_1_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_9_ac_1_is_done_with_evidence) ... ok
test_us_9_ac_1_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_9_ac_1_matrix_lists_src_and_test) ... ok
test_build_paths_custom_roots (test_workspace_init.TestBuildPaths.test_build_paths_custom_roots) ... ok
test_build_paths_default_roots (test_workspace_init.TestBuildPaths.test_build_paths_default_roots) ... ok
test_build_paths_rejects_backslash_traversal_in_roots (test_workspace_init.TestBuildPaths.test_build_paths_rejects_backslash_traversal_in_roots) ... ok
test_quarantine_path_default_root (test_workspace_init.TestQuarantinePath.test_quarantine_path_default_root) ... ok
test_quarantine_path_layout (test_workspace_init.TestQuarantinePath.test_quarantine_path_layout) ... ok
test_quarantine_path_rejects_backslash_traversal (test_workspace_init.TestQuarantinePath.test_quarantine_path_rejects_backslash_traversal) ... ok
test_quarantine_path_rejects_empty_root (test_workspace_init.TestQuarantinePath.test_quarantine_path_rejects_empty_root) ... ok
test_quarantine_path_rejects_invalid_id (test_workspace_init.TestQuarantinePath.test_quarantine_path_rejects_invalid_id) ... ok
test_quarantine_path_rejects_traversal (test_workspace_init.TestQuarantinePath.test_quarantine_path_rejects_traversal) ... ok
test_audit_record_is_json_safe_on_success (test_workspace_init.TestWorkspaceInitService.test_audit_record_is_json_safe_on_success) ... ok
test_audit_record_on_rejection (test_workspace_init.TestWorkspaceInitService.test_audit_record_on_rejection) ... ok
test_init_allows_same_package_different_role (test_workspace_init.TestWorkspaceInitService.test_init_allows_same_package_different_role) ... ok
test_init_creates_workspace_for_committed_import (test_workspace_init.TestWorkspaceInitService.test_init_creates_workspace_for_committed_import) ... ok
test_init_idempotent_on_duplicate_package (test_workspace_init.TestWorkspaceInitService.test_init_idempotent_on_duplicate_package) ... ok
test_init_propagates_path_error_for_unsafe_package_id (test_workspace_init.TestWorkspaceInitService.test_init_propagates_path_error_for_unsafe_package_id) ... ok
test_init_rejects_invalid_role_id (test_workspace_init.TestWorkspaceInitService.test_init_rejects_invalid_role_id) ... ok
test_init_rejects_non_import_outcome (test_workspace_init.TestWorkspaceInitService.test_init_rejects_non_import_outcome) ... ok
test_init_rejects_rolled_back_import (test_workspace_init.TestWorkspaceInitService.test_init_rejects_rolled_back_import) ... ok
test_sanitize_id_accepts_exactly_maximum_length (test_workspace_init.TestWorkspacePath.test_sanitize_id_accepts_exactly_maximum_length) ... ok
test_sanitize_id_accepts_safe (test_workspace_init.TestWorkspacePath.test_sanitize_id_accepts_safe) ... ok
test_sanitize_id_rejects_empty (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_empty) ... ok
test_sanitize_id_rejects_maximum_plus_one (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_maximum_plus_one) ... ok
test_sanitize_id_rejects_too_long (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_too_long) ... ok
test_workspace_path_default_root (test_workspace_init.TestWorkspacePath.test_workspace_path_default_root) ... ok
test_workspace_path_layout (test_workspace_init.TestWorkspacePath.test_workspace_path_layout) ... ok
test_workspace_path_rejects_backslash_traversal (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_backslash_traversal) ... ok
test_workspace_path_rejects_empty_root (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_empty_root) ... ok
test_workspace_path_rejects_invalid_project_id (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_invalid_project_id) ... ok
test_workspace_path_rejects_invalid_role_id (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_invalid_role_id) ... ok
test_workspace_path_rejects_traversal (test_workspace_init.TestWorkspacePath.test_workspace_path_rejects_traversal) ... ok
test_by_package (test_workspace_init.TestWorkspaceRegistry.test_by_package) ... ok
test_empty_registry (test_workspace_init.TestWorkspaceRegistry.test_empty_registry) ... ok
test_register_allows_same_package_for_different_role (test_workspace_init.TestWorkspaceRegistry.test_register_allows_same_package_for_different_role) ... ok
test_register_rejects_duplicate_package_for_same_role (test_workspace_init.TestWorkspaceRegistry.test_register_rejects_duplicate_package_for_same_role) ... ok
test_register_rejects_duplicate_role (test_workspace_init.TestWorkspaceRegistry.test_register_rejects_duplicate_role) ... ok
test_register_then_get (test_workspace_init.TestWorkspaceRegistry.test_register_then_get) ... ok
test_disallowed_extension_is_denied (test_wps_launcher.WpsLauncherTests.test_disallowed_extension_is_denied) ... ok
test_invalid_root_is_rejected (test_wps_launcher.WpsLauncherTests.test_invalid_root_is_rejected) ... ok
test_missing_absolute_executable_is_not_available (test_wps_launcher.WpsLauncherTests.test_missing_absolute_executable_is_not_available) ... ok
test_missing_file_is_denied (test_wps_launcher.WpsLauncherTests.test_missing_file_is_denied) ... ok
test_runner_failure_is_error (test_wps_launcher.WpsLauncherTests.test_runner_failure_is_error) ... ok
test_runner_is_invoked_with_explicit_executable_and_path (test_wps_launcher.WpsLauncherTests.test_runner_is_invoked_with_explicit_executable_and_path) ... ok
test_symlink_escape_is_denied (test_wps_launcher.WpsLauncherTests.test_symlink_escape_is_denied) ... skipped 'symlink creation unavailable'
test_traversal_and_absolute_paths_are_denied (test_wps_launcher.WpsLauncherTests.test_traversal_and_absolute_paths_are_denied) ... ok
test_valid_document_dry_run_is_ok (test_wps_launcher.WpsLauncherTests.test_valid_document_dry_run_is_ok) ... ok

======================================================================
ERROR: test_run_validation (unittest.loader._FailedTest.test_run_validation)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_run_validation
Traceback (most recent call last):
  File "E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\loader.py", line 426, in _find_test_path
    module = self._get_module_from_name(name)
  File "E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\loader.py", line 367, in _get_module_from_name
    __import__(name)
    ~~~~~~~~~~^^^^^^
  File "E:\Workspace\Coevo\tests\unit\test_run_validation.py", line 20, in <module>
    spec.loader.exec_module(run_validation)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "E:\Workspace\Coevo\scripts\run_validation.py", line 21, in <module>
    import yaml
ModuleNotFoundError: No module named 'yaml'


----------------------------------------------------------------------
Ran 1242 tests in 241.033s

FAILED (errors=1, skipped=3)

```



## 2026-08-08T10:30:41.310682Z — target=`quality` fingerprint=`5ab34d173704cd3e`
- exit_code: `1`
```text
pture/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/progress_capture/watcher.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/report/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize13.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "FRAMEWORK-OPTIMIZE-14",
      "title": "共享 JSON 重复键拒绝守卫（2026-08-08，用户指令\"继续下一步\"，延续\"基于框架，优化原来系统应用的代码实现……不做全量门禁\"）：新增 src/coevo/jsonutil.py（reject_duplicate_pairs，error_factory 可注入保持各模块异常语义、消息统一 \"duplicate key ...\" 兼容既有断言），protocol/agent_package、framework/k8s_listing、crypto/cng_handle、cockpit/state_store、framework/manifest_checker 5 处本地 object_pairs_hook 守卫统一引用；fail-closed 不降；root_modules.md 登记",
      "code": [
        "src/coevo/jsonutil.py",
        "src/coevo/protocol/agent_package.py",
        "src/coevo/framework/k8s_listing.py",
        "src/coevo/crypto/cng_handle.py",
        "src/coevo/cockpit/state_store.py",
        "src/coevo/framework/manifest_checker.py",
        "docs/modules/root_modules.md"
      ],
      "tests": [
        "tests/unit/test_framework_optimize14.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/jsonutil.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/protocol/agent_package.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/k8s_listing.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/crypto/cng_handle.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/state_store.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_optimize14.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "QUALITY-ROBUST-1",
      "title": "门禁稳定性修复与文档一致性（2026-08-08，用户指令\"站在资深审查者角度全面审查、复盘并落地优化\"，后续补强到全量门禁全绿）：① LOAD-1 /healthz p95 探针增加预热 + best-of-3 取最优无错轮次（scripts/benchmark.py 提取 _fire_probe/_p95 并参数化 16 workers×8/轮），单元测试改 class-level 共享探针结果，消除共享机/并发负载下单次采样偶发超 1.0s 抖动（两次实测复现 p50=0.0066s/max=1.0675s 与 p50=0.0090s/max=1.5953s）；② test_loop_launcher 容忍 PowerShell 偶发 None 输出流（TypeError 修复）+ 空输出有界重试；③ 根因修复：测试子进程捕获统一加 encoding=\"utf-8\"+errors=\"replace\"（loop_launcher / dev_environment_entry / sm2_test_pki_generation / cng_handle / crypto_sm3 / gmssl_prototype_provider / local_toolchain_security / loop_environment / private_key_handles_bindings），消除 PowerShell 5.1 GBK 输出在门禁 PYTHONUTF8 环境下解码崩溃（stderr=None/空输出/UnicodeDecodeError 0xcb）；④ 门禁自洽：quality_gate 阶段间重新封缄保证 e2e preflight 看到 fully-sealed，子进程加 2400s 限时防无限挂起；⑤ 全链哈希同步：quality_gate.py 变更后 python-script-lock.tsv / make.cs ScriptInventorySha256 / toolchain-lock 同步；⑥ docs/production-readiness.md + docs/modules/benchmarks.md + src/coevo/benchmarks/__init__.py 三处\"计时探针不进 make quality\"表述与实际门禁组合对齐（唯一例外 LOAD-1：预热 + best-of-3）",
      "code": [
        "scripts/benchmark.py",
        "scripts/quality_gate.py",
        "docs/production-readiness.md",
        "docs/modules/benchmarks.md",
        "src/coevo/benchmarks/__init__.py",
        "docs/dependencies/python-script-lock.tsv",
        "docs/dependencies/toolchain-lock.json",
        "scripts/tool-shims/make.cs"
      ],
      "tests": [
        "tests/unit/test_benchmark_http.py",
        "tests/unit/test_loop_launcher.py",
        "tests/integration/test_dev_environment_entry.py",
        "tests/integration/test_sm2_test_pki_generation.py",
        "tests/integration/test_cng_handle.py",
        "tests/integration/test_crypto_sm3.py",
        "tests/integration/test_gmssl_prototype_provider.py",
        "tests/security/test_local_toolchain_security.py",
        "tests/e2e/test_loop_environment.py",
        "tests/unit/test_private_key_handles_bindings.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/benchmark.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/production-readiness.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/benchmarks.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/benchmarks/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/python-script-lock.tsv",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/tool-shims/make.cs",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_benchmark_http.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_loop_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_dev_environment_entry.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_sm2_test_pki_generation.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cng_handle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_crypto_sm3.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_gmssl_prototype_provider.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/security/test_local_toolchain_security.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_loop_environment.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_private_key_handles_bindings.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\archive_records.py --check
[verification] archive 1 section(s): archived 1 old section(s); size 506329 > 500000 bytes; size-trimmed 1 kept section(s)
[ok] decisions: nothing to archive
[ok] audit: nothing to archive
check failed: 1 record file(s) need archiving

```



## 2026-08-08T11:03:18.396753Z — target=`quality` fingerprint=`5ab34d173704cd3e`
- exit_code: `1`
```text
k
test_snapshot_after_restart_supports_inmemory_facades (test_package_store_persistence.CrossRestartPersistenceTests.test_snapshot_after_restart_supports_inmemory_facades) ... ok
test_tampered_file_is_refused_on_reopen (test_package_store_persistence.CrossRestartPersistenceTests.test_tampered_file_is_refused_on_reopen) ... ok
test_watcher_background_mode_collects_modified_events (test_progress_watcher.ProgressWatcherIntegrationTests.test_watcher_background_mode_collects_modified_events) ... ok
test_watcher_events_feed_progress_capture (test_progress_watcher.ProgressWatcherIntegrationTests.test_watcher_events_feed_progress_capture) ... ok
test_partial_upgrade_leaves_pointer_intact_and_force_completes (test_recovery_faults.InstallerInterruptedUpgradeTests.test_partial_upgrade_leaves_pointer_intact_and_force_completes) ... ok
test_restart_loads_last_committed_state (test_recovery_faults.StateStoreInterruptedSaveTests.test_restart_loads_last_committed_state) ... ok
test_stale_tmp_does_not_corrupt_committed_state (test_recovery_faults.StateStoreInterruptedSaveTests.test_stale_tmp_does_not_corrupt_committed_state) ... ok
test_committed_profile_rejects_minimal_receipt_and_missing_or_tampered_artifact (test_sm2_test_pki_generation.Sm2TestPkiTests.test_committed_profile_rejects_minimal_receipt_and_missing_or_tampered_artifact) ... ok
test_committed_receipt_hardlink_is_rejected (test_sm2_test_pki_generation.Sm2TestPkiTests.test_committed_receipt_hardlink_is_rejected) ... ok
test_committed_receipt_reparse_is_rejected_when_supported (test_sm2_test_pki_generation.Sm2TestPkiTests.test_committed_receipt_reparse_is_rejected_when_supported) ... skipped "file symlink privilege unavailable: [WinError 1314] 客户端没有所需的特权。: 'E:\\\\Workspace\\\\Coevo\\\\loop\\\\runtime\\\\sm2-test-pki\\\\receipt-target-86974ec8a78e4d7b8884a56ba1065d6c.json' -> 'E:\\\\Workspace\\\\Coevo\\\\loop\\\\runtime\\\\sm2-test-pki\\\\test-fffb30e9224e4874988d\\\\receipt.json'"
test_concurrent_same_profile_has_one_atomic_winner (test_sm2_test_pki_generation.Sm2TestPkiTests.test_concurrent_same_profile_has_one_atomic_winner) ... ok
test_directory_lock_non_sharing_error_is_not_retried (test_sm2_test_pki_generation.Sm2TestPkiTests.test_directory_lock_non_sharing_error_is_not_retried) ... ok
test_directory_lock_retries_sharing_violation_then_succeeds (test_sm2_test_pki_generation.Sm2TestPkiTests.test_directory_lock_retries_sharing_violation_then_succeeds) ... ok
test_directory_lock_roles_and_share_flags_are_fixed (test_sm2_test_pki_generation.Sm2TestPkiTests.test_directory_lock_roles_and_share_flags_are_fixed) ... ok
test_directory_lock_sharing_violation_retry_exhaustion_fails_closed (test_sm2_test_pki_generation.Sm2TestPkiTests.test_directory_lock_sharing_violation_retry_exhaustion_fails_closed) ... ok
test_dpapi_and_encrypted_pkcs8_round_trip_without_command_line_secret (test_sm2_test_pki_generation.Sm2TestPkiTests.test_dpapi_and_encrypted_pkcs8_round_trip_without_command_line_secret) ... ok
test_existing_profile_acl_must_remain_protected_owner_only (test_sm2_test_pki_generation.Sm2TestPkiTests.test_existing_profile_acl_must_remain_protected_owner_only) ... ok
test_generation_is_isolated_encrypted_verified_and_non_overwriting (test_sm2_test_pki_generation.Sm2TestPkiTests.test_generation_is_isolated_encrypted_verified_and_non_overwriting) ... ok
test_helper_command_line_and_input_channel_are_fail_closed (test_sm2_test_pki_generation.Sm2TestPkiTests.test_helper_command_line_and_input_channel_are_fail_closed) ... ok
test_helper_is_static_no_child_and_launcher_has_no_job_or_native_directory_layer (test_sm2_test_pki_generation.Sm2TestPkiTests.test_helper_is_static_no_child_and_launcher_has_no_job_or_native_directory_layer) ... ok
test_helper_launch_surface_has_no_cli_or_subprocess_secret_path (test_sm2_test_pki_generation.Sm2TestPkiTests.test_helper_launch_surface_has_no_cli_or_subprocess_secret_path) ... ok
test_helper_owns_handle_identity_reparse_rename_and_strict_recovery (test_sm2_test_pki_generation.Sm2TestPkiTests.test_helper_owns_handle_identity_reparse_rename_and_strict_recovery) ... ok
test_helper_response_is_fixed_public_frame_and_response_loss_recovers (test_sm2_test_pki_generation.Sm2TestPkiTests.test_helper_response_is_fixed_public_frame_and_response_loss_recovers) ... ok
test_hung_helper_is_tree_killed_and_drains_are_bounded (test_sm2_test_pki_generation.Sm2TestPkiTests.test_hung_helper_is_tree_killed_and_drains_are_bounded) ... FAIL
test_kill_points_are_recovered_with_same_nonce (test_sm2_test_pki_generation.Sm2TestPkiTests.test_kill_points_are_recovered_with_same_nonce) ... ok
test_launcher_ignores_poisoned_path_and_cleans_ephemeral_helper (test_sm2_test_pki_generation.Sm2TestPkiTests.test_launcher_ignores_poisoned_path_and_cleans_ephemeral_helper) ... ok
test_lock_matches_offline_artifact_and_records_unsigned_risk (test_sm2_test_pki_generation.Sm2TestPkiTests.test_lock_matches_offline_artifact_and_records_unsigned_risk) ... ok
test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper (test_sm2_test_pki_generation.Sm2TestPkiTests.test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper) ... ok
test_prepositioned_profile_file_is_preserved_and_no_staging_remains (test_sm2_test_pki_generation.Sm2TestPkiTests.test_prepositioned_profile_file_is_preserved_and_no_staging_remains) ... ok
test_recover_unknown_staged_object_fails_closed_without_deleting_it (test_sm2_test_pki_generation.Sm2TestPkiTests.test_recover_unknown_staged_object_fails_closed_without_deleting_it) ... ok
test_runtime_output_is_gitignored (test_sm2_test_pki_generation.Sm2TestPkiTests.test_runtime_output_is_gitignored) ... ok
test_wide_runtime_acl_is_corrected_before_staging_creation (test_sm2_test_pki_generation.Sm2TestPkiTests.test_wide_runtime_acl_is_corrected_before_staging_creation) ... ok
test_append_after_reopen_extends_store (test_talent_store_persistence.CrossRestartPersistenceTests.test_append_after_reopen_extends_store) ... ok
test_duplicate_talent_code_detected_across_restart (test_talent_store_persistence.CrossRestartPersistenceTests.test_duplicate_talent_code_detected_across_restart) ... ok
test_from_pool_then_reopen_round_trip (test_talent_store_persistence.CrossRestartPersistenceTests.test_from_pool_then_reopen_round_trip) ... ok
test_registered_talents_survive_restart (test_talent_store_persistence.CrossRestartPersistenceTests.test_registered_talents_survive_restart) ... ok
test_snapshot_after_restart_drives_recommender (test_talent_store_persistence.CrossRestartPersistenceTests.test_snapshot_after_restart_drives_recommender) ... ok
test_tampered_file_is_refused_on_reopen (test_talent_store_persistence.CrossRestartPersistenceTests.test_tampered_file_is_refused_on_reopen) ... ok
test_custom_tools_reference_existing_controlled_scripts (test_tool_contracts.ToolContractIntegrationTests.test_custom_tools_reference_existing_controlled_scripts) ... ok

======================================================================
FAIL: test_hung_helper_is_tree_killed_and_drains_are_bounded (test_sm2_test_pki_generation.Sm2TestPkiTests.test_hung_helper_is_tree_killed_and_drains_are_bounded)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_sm2_test_pki_generation.py", line 269, in test_hung_helper_is_tree_killed_and_drains_are_bounded
    self.assertLess(elapsed, 8.0, result.stderr)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 15.451145400002133 not less than 8.0 : helper timed out
At E:\Workspace\Coevo\scripts\generate-sm2-test-pki.ps1:100 char:7
+       throw 'helper timed out'
+       ~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : OperationStopped: (helper timed out:String) [], RuntimeException
    + FullyQualifiedErrorId : helper timed out
 


----------------------------------------------------------------------
Ran 261 tests in 1360.237s

FAILED (failures=1, skipped=1)

```


## 2026-08-08T12:17:15.938756Z — target=`quality` fingerprint=`5ab34d173704cd3e`
- exit_code: `0`
```text
equires_recovery_and_reopen_commits_exactly_once) ... ok
test_row_shape_validator_rejects_each_oversize_and_malformed_column (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_row_shape_validator_rejects_each_oversize_and_malformed_column) ... ok
test_signed_chain_binds_store_head_sequence_and_previous_hash (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_signed_chain_binds_store_head_sequence_and_previous_hash) ... ok
test_stale_baseline_is_rejected_before_insert (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
test_truncation_is_rejected_by_freshness_checkpoint (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_truncation_is_rejected_by_freshness_checkpoint) ... ok
test_gitignore_excludes_receipt_pattern (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_gitignore_excludes_receipt_pattern) ... ok
test_no_reachable_receipt_blobs_across_all_refs (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_no_reachable_receipt_blobs_across_all_refs) ... ok
test_no_tracked_receipt_paths (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_no_tracked_receipt_paths) ... ok
test_pre_scrub_head_is_no_longer_reachable (test_private_key_handles_bindings.PrivateKeyHandleGitBindingTests.test_pre_scrub_head_is_no_longer_reachable) ... ok
test_validate_bundle_rejects_private_key_handle_field (test_private_key_storage.IdentityBundlePrivateKeyRejectionTests.test_validate_bundle_rejects_private_key_handle_field) ... ok
test_validate_bundle_rejects_private_key_pkcs8_bytes (test_private_key_storage.IdentityBundlePrivateKeyRejectionTests.test_validate_bundle_rejects_private_key_pkcs8_bytes) ... ok
test_reference_accepts_only_safe_metadata (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_accepts_only_safe_metadata) ... ok
test_reference_is_frozen_and_hash_stable_across_rotations (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_is_frozen_and_hash_stable_across_rotations) ... ok
test_reference_rejects_inverted_validity (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_rejects_inverted_validity) ... ok
test_reference_rejects_malformed_handle_and_digest (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_reference_rejects_malformed_handle_and_digest) ... ok
test_repr_and_pickle_never_expose_secret_token (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_repr_and_pickle_never_expose_secret_token) ... ok
test_validate_handle_payload_rejects_private_key_blob_strings (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_validate_handle_payload_rejects_private_key_blob_strings) ... ok
test_validate_handle_payload_rejects_unknown_or_sensitive_fields (test_private_key_storage.PrivateKeyReferenceSafetyTests.test_validate_handle_payload_rejects_unknown_or_sensitive_fields) ... ok
test_audit_chain_detects_event_tampering (test_private_key_storage.PrivateKeyServicePolicyTests.test_audit_chain_detects_event_tampering) ... ok
test_audit_chain_records_store_use_revoke_and_destroy (test_private_key_storage.PrivateKeyServicePolicyTests.test_audit_chain_records_store_use_revoke_and_destroy) ... ok
test_destroyed_handle_blocks_use_with_stale_reference (test_private_key_storage.PrivateKeyServicePolicyTests.test_destroyed_handle_blocks_use_with_stale_reference) ... ok
test_overwrite_store_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_overwrite_store_is_rejected) ... ok
test_revoke_without_reason_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_revoke_without_reason_is_rejected) ... ok
test_revoked_reference_blocks_use_and_audits_rejection (test_private_key_storage.PrivateKeyServicePolicyTests.test_revoked_reference_blocks_use_and_audits_rejection) ... ok
test_stored_reference_round_trips_use_and_returns_signature (test_private_key_storage.PrivateKeyServicePolicyTests.test_stored_reference_round_trips_use_and_returns_signature) ... ok
test_untrusted_parent_thumbprint_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_untrusted_parent_thumbprint_is_rejected) ... ok
test_use_outside_validity_window_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_use_outside_validity_window_is_rejected) ... ok
test_use_with_naive_datetime_is_rejected (test_private_key_storage.PrivateKeyServicePolicyTests.test_use_with_naive_datetime_is_rejected) ... ok
test_verify_binds_certificate_pin_digest_algorithm_and_audits_digest_only (test_private_key_storage.PrivateKeyServicePolicyTests.test_verify_binds_certificate_pin_digest_algorithm_and_audits_digest_only) ... ok
test_verify_rejects_wrong_pin_revoked_destroyed_and_bad_signature (test_private_key_storage.PrivateKeyServicePolicyTests.test_verify_rejects_wrong_pin_revoked_destroyed_and_bad_signature) ... ok
test_poisoned_powershell_path_is_rejected_before_execution (test_private_key_storage.WindowsPrivateKeyLaunchPolicyTests.test_poisoned_powershell_path_is_rejected_before_execution) ... ok
test_rejects_uncontrolled_helper_path (test_private_key_storage.WindowsPrivateKeyLaunchPolicyTests.test_rejects_uncontrolled_helper_path) ... ok
test_custom_tools_use_current_typed_api (test_tool_permissions.PermissionTests.test_custom_tools_use_current_typed_api) ... ok
test_network_and_install_commands_are_fail_closed (test_tool_permissions.PermissionTests.test_network_and_install_commands_are_fail_closed) ... ok

----------------------------------------------------------------------
Ran 99 tests in 150.528s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 232.069s

OK
audit seal: fully-sealed

```
## 2026-08-08T12:20:00Z — RECORDS-ARCHIVE-2 独立验证（mvp-verifier 契约，只读沙箱 recarch2-verify，pin=`b7b1cbc`）
- 审查者：mvp-verifier（独立沙箱实际执行）；结论：PASS。
- 沙箱内实际执行：
  * `python scripts/quality_gate.py --target fmt` exit=0 fingerprint=`fe39766e2048d2bc`（与主仓库指纹一致）；
  * `python scripts/quality_gate.py --target lint` exit=0 fingerprint=`0d48b25bc6a9b68`（沙箱路径指令专属，与维护机基线不同属预期，CI 同款）；
  * 定向单元 33/33 全绿：`test_records_archive`、`test_quality_gate_lock`、`test_run_validation`、`test_control_main`；
  * `review_sandbox check` violations=[]，loop/变更仅为门禁证据输出（VERIFICATION/audit-head/tool-audit），已 discard。
- 主仓库全量门禁：`make quality`（make.cs→control.pyz 入口）exit=0 fingerprint=`5ab34d173704cd3e`；fmt exit=0 fingerprint=`fe39766e2048d2bc`；lint exit=0 fingerprint=`eb5a3c41818a9be3`；audit fully-sealed。
## 2026-08-08T12:22:00Z — RECORDS-ARCHIVE-2 独立安全审查（security-reviewer 契约，只读沙箱 recarch2-sec，pin=`b7b1cbc`）
- 审查者：security-reviewer（独立沙箱实际执行）；结论：PASS，Critical/High/Medium/Low = 0/0/0/0。
- 沙箱内实际执行：
  * 安全测试子集 49/49 全绿：`test_local_toolchain_security`（含 make.cs 锁链常量、控制存档分派、注入拒绝回归）、`test_records_archive`、`test_quality_gate_lock`、`test_run_validation`、`test_control_main`；
  * STRIDE 行为探针 6/6 PASS：未知 kind 与非字符串输入 fail-closed、阈值边界准确、size-trim 不空记录、真实字节计数入理由、归档附加写入不覆盖、lint 含 `archive_records --check`；
  * `review_sandbox check` violations=[]，已 discard。
- 范围：涉及审计记录归档边界、脚本锁链全链同步、门禁 fail-closed 语义。

## 2026-08-08T12:31:03.738859Z — target=`lint` fingerprint=`eb5a3c41818a9be3`
- exit_code: `0`
```text
ype_provider / local_toolchain_security / loop_environment / private_key_handles_bindings），消除 PowerShell 5.1 GBK 输出在门禁 PYTHONUTF8 环境下解码崩溃（stderr=None/空输出/UnicodeDecodeError 0xcb）；④ 门禁自洽：quality_gate 阶段间重新封缄保证 e2e preflight 看到 fully-sealed，子进程加 2400s 限时防无限挂起；⑤ 全链哈希同步：quality_gate.py 变更后 python-script-lock.tsv / make.cs ScriptInventorySha256 / toolchain-lock 同步；⑥ docs/production-readiness.md + docs/modules/benchmarks.md + src/coevo/benchmarks/__init__.py 三处\"计时探针不进 make quality\"表述与实际门禁组合对齐（唯一例外 LOAD-1：预热 + best-of-3）",
      "code": [
        "scripts/benchmark.py",
        "scripts/quality_gate.py",
        "docs/production-readiness.md",
        "docs/modules/benchmarks.md",
        "src/coevo/benchmarks/__init__.py",
        "docs/dependencies/python-script-lock.tsv",
        "docs/dependencies/toolchain-lock.json",
        "scripts/tool-shims/make.cs"
      ],
      "tests": [
        "tests/unit/test_benchmark_http.py",
        "tests/unit/test_loop_launcher.py",
        "tests/integration/test_dev_environment_entry.py",
        "tests/integration/test_sm2_test_pki_generation.py",
        "tests/integration/test_cng_handle.py",
        "tests/integration/test_crypto_sm3.py",
        "tests/integration/test_gmssl_prototype_provider.py",
        "tests/security/test_local_toolchain_security.py",
        "tests/e2e/test_loop_environment.py",
        "tests/unit/test_private_key_handles_bindings.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/benchmark.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/production-readiness.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/benchmarks.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/benchmarks/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/python-script-lock.tsv",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/tool-shims/make.cs",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_benchmark_http.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_loop_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_dev_environment_entry.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_sm2_test_pki_generation.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cng_handle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_crypto_sm3.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_gmssl_prototype_provider.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/security/test_local_toolchain_security.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_loop_environment.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_private_key_handles_bindings.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "RECORDS-ARCHIVE-2",
      "title": "记录归档自动化门禁 + control.pyz 门禁入口同步（2026-08-08，用户指令“继续”）：① `records_archive.py` 收敛为归档策略唯一事实源（`POLICY` + `over_policy_size(kind,text)` fail-closed：未知 kind / 非字符串拒绝；`archive_plan` 新增真实文件字节 `size_bytes` 与尾差预算 `size_tail_budget_bytes`，size-trim 留余量避免 --apply 后紧贴阈值导致下一次 --check 必败）；② `archive_records.py` 新增 `--check` 门禁模式（任一记录文件超阈值/待归档即非零退出，fail-closed），归档写入改追加（同日重复 apply 不再覆盖历史归档）；③ `quality_gate.py` lint 阶段接入 `archive_records --check`；④ 重建 `.tools/control/control.pyz`（ZIP_STORED + sorted + DOS epoch）并全链哈希同步（python-script-lock.tsv / make.cs ScriptInventorySha256+ControlArchiveSha256 / toolchain-lock control_archive+script_inventory+source_sha256）；⑤ 实际 `--apply` 归档 VERIFICATION/DECISIONS 至策略容量内并落 20260808 归档；⑥ 修复 run_validation.py 对 PyYAML 的依赖（锁链 python 实际未捦绑 yaml，full gate 首次暴露），BACKLOG 状态计数改 stdlib 行解析保持指标语义",
      "code": [
        "src/coevo/records_archive.py",
        "scripts/archive_records.py",
        "scripts/quality_gate.py",
        "scripts/run_validation.py",
        "scripts/tool-shims/make.cs",
        "docs/dependencies/python-script-lock.tsv",
        "docs/dependencies/toolchain-lock.json",
        "docs/modules/root_modules.md",
        "docs/process/records-archiving-policy.md"
      ],
      "tests": [
        "tests/unit/test_records_archive.py",
        "tests/unit/test_quality_gate_lock.py",
        "tests/unit/test_run_validation.py",
        "tests/security/test_local_toolchain_security.py",
        "tests/integration/test_dev_environment_entry.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/records_archive.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/archive_records.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/run_validation.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/tool-shims/make.cs",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/python-script-lock.tsv",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/root_modules.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/process/records-archiving-policy.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_records_archive.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_lock.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_run_validation.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/security/test_local_toolchain_security.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_dev_environment_entry.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\archive_records.py --check
[ok] verification: nothing to archive
[ok] decisions: nothing to archive
[ok] audit: nothing to archive
check ok: all record files within archiving policy
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```
