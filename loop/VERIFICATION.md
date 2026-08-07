## 2026-08-04T01:04:15.420713Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
 "tests/unit/test_cockpit_http.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_production_support.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_protocol_sign_blocked.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_agent_package_atomic_import.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_state_persistence.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/security/test_identity_store_security.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_return_chain.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "LOAD-1",
      "title": "��ʻ�� HTTP ����/�ӳ�����̽�루2026-08-04���û�ָ�������������Ż�����`scripts/benchmark.py` ���� `_cockpit_http_probe`��������ʵ���� cockpit��16 worker �� 8 = 128 �� `GET /healthz`������ p95/p50/max ����������غɶ��������������ޣ�`max_concurrent_requests=16` Ĭ��ֵ����ÿ�����½����ӣ����Ϸ���� one-request-per-connection ������Ϊ����SLA p95��1.0s �� errors=0��`COCKPIT_HTTP_P95_LIMIT_SEC` ���������ο��ܹ���ͨҳ�� 3s��ʵ�� p95��0.52s ����һ����������`tests/unit/test_benchmark_http.py` 2 �������� ok / �ӳٱ߽�� result.limit����",
      "code": [
        "scripts/benchmark.py"
      ],
      "tests": [
        "tests/unit/test_benchmark_http.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/benchmark.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_benchmark_http.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-2",
      "title": "�̻����Ź�/��������ʽ Python ������·����2026-08-04���û�ָ�������������Ż������� `scripts/register-autostart.ps1` ���� `PinPython` ��������д `<install_root>\\python-path.txt`�������ƻ����񣬹�ˢ�³¾� pin����`Register` �ڴ����ƻ�����ǰ�̻��������Ľ���������ʽ `-PythonPath` �� PATH����дʧ�ܼ���ֹ���� `scripts/cockpit-watchdog.ps1` ���� `-PythonPath`������˳����ʽ���� �� sidecar �� PATH��sidecar ��/���·��/ָ��ȱʧ��������ʧ�ܹرգ�����Ĭ���ˣ����� `scripts/install_cockpit.py` ��װ/�����ɹ�ʱԭ��д�� `sys.executable`��ָ���л�ǰ��ʧ�ܼ���ֹ��װ������ �ĵ���ops-runbook ��2/��2.1 + known-limitations ��Ŀ���¡�",
      "code": [
        "scripts/register-autostart.ps1",
        "scripts/cockpit-watchdog.ps1",
        "scripts/install_cockpit.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py",
        "tests/unit/test_preflight_watchdog.py",
        "tests/integration/test_installer.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/register-autostart.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/install_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_installer.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "BACKUP-2",
      "title": "���������֤��2026-08-04���û�ָ�������������Ż�����`scripts/backup_state.py` ���� `--require-external`�������ݸ�λ�ڰ�װ���ڡ����밲װ��ͬ����`st_dev` �Ƚϣ�ʱʧ�ܹرգ���ֹ���̹���ͬʱ�ٵ������뱸�ݣ�manifest ���� `same_volume` �����ɶ��ֶι��Զ����˲飻���ݸ���Ŀ¼������д��Ŀ�겻�ɴ���ʱ�ɾ������������� traceback����`--require-external` �������� backup ������verify/restore �����ޣ��ĵ���ops-runbook ��4 ��ر���ʾ�� + known-limitations ������Ŀ���¡�",
      "code": [
        "scripts/backup_state.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/unit/test_backup_state.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/backup_state.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_backup_state.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-2",
      "title": "��Կɨ��ģʽ��չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� `pem_private_key` ���� `SM2 PRIVATE KEY`�����ܸ�ʽ��tests/ PEM �������岻�䣩���� `github_pat` ��չΪ���Ƽ��� `ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_`/`github_pat_`��fine-grained������ ���� `google_api_key`��`AIza`+35���� `npm_token`��`npm_`+36������ ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž��Զ����棨secret_scan ���裩��",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-3",
      "title": "����������ӱ������ʶȼ�أ�2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` ���� `backup` ��顪��ɨ�� `--backup-root`��Ĭ�� `<install-root>\\backups`����ȫ������ manifest��ȡ���� `created_at`������ �� `--max-backup-age-days`��Ĭ�� 7 �죩Ϊ ok�����ݸ�ȱʧ/����Ч manifest/����/δ��ʱ�����>1 �죩��Ϊ degraded���ָ���̬�澯������Ϸ��񣬲��� critical����CLI ���� `--backup-root` �� `--max-backup-age-days`��<1 �ܾ�����ֻ������ stdlib��docs/operations/ops-runbook.md ��1 ���� + ��ر��ݼ��ʾ����",
      "code": [
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
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

## 2026-08-08 — US-16-AC-5 增量门禁与安全审查记录（主仓库，豁免全量 quality）

- target=`test (定向)` exit_code=`0`
```text
python -m unittest tests.unit.test_framework_tools tests.unit.test_module_docs
  tests.unit.test_framework_capability tests.unit.test_framework_manifest_checker
  tests.unit.test_framework_validate_plan tests.unit.test_framework_plan_l18
  tests.unit.test_framework_lifecycle tests.unit.test_framework_policy
  tests.unit.test_framework_memory
Ran 111 tests; OK（AC-5.1..5.5 全部断言 + L17 文档守卫 + framework 相邻回归）
修复前沙箱内探针：timeout_sec=True / size_in_bytes_max=True 被接受（bool 是 int 子类）
修复后（commit 65dfb1e，type(...) is int）：两者均 REJECTED，111/111 仍全绿
```
- target=`fmt` exit_code=`0` fingerprint=`fe39766e2048d2bc`（2026-08-07T17:10Z）
- target=`lint` exit_code=`0` fingerprint=`252ad24e526f6728`（2026-08-07T17:10Z，audit fully-sealed）
- security-review（只读沙箱 `ac5-sec`，pin=`d2f4046`）：
  * review_sandbox check: ok, violations=[]（零违规，未修改任何受保护路径）
  * 沙箱内定向测试 13/13 OK（`-B` 无字节码落盘）
  * 结论：PASS，Critical/High 0；Low 1 已就地修复（bool-as-int，`65dfb1e`）
  * 沙箱已 check + discard
- 全量 `make quality` 按用户指示本轮豁免，留待后续回归；豁免见 DECISIONS。

## 2026-08-07T16:47:52.215398Z — target=`test+security-review (incremental)` fingerprint=`manual-us16ac3`
- exit_code: `0`
```text
US-16-AC-3（M1b，commit b42d00c）增量门禁与安全审查：

[1] 定向单元测试（主工作树）：
    python -m unittest tests.unit.test_framework_capability \
      tests.unit.test_framework_manifest_checker \
      tests.unit.test_framework_validate_plan \
      tests.unit.test_framework_plan_l18 \
      tests.unit.test_framework_lifecycle
    Ran 75 tests; OK（含 AC-3.1..AC-3.5 全部断言）

[2] 相邻回归（只读沙箱 us16ac3-sec，HEAD=b42d00c）：
    python -m unittest tests.unit.test_orchestrator \
      tests.unit.test_agent_wire_regression \
      tests.integration.test_orchestrator_real_facade_chain
    Ran 38 tests; OK（新增 KNOWLEDGE_INGEST 枚举成员未破坏编排器/wire/真实链路）
    python -m unittest tests.unit.test_module_docs  -> Ran 4 tests; OK（L17 文档守卫）

[3] 门禁：
    --target fmt exit=0 fingerprint=`fe39766e2048d2bc`（2026-08-07T16:42:14Z）
    --target lint exit=0 fingerprint=`252ad24e526f6728`（2026-08-07T16:42:23Z）
    audit seal: fully-sealed（前后均由 quality_gate 封存）

[4] 安全审查（security-reviewer 契约，只读沙箱内执行）：
    - 沙箱 review_sandbox check: ok, violations=[]（零违规；未修改任何受保护路径）
    - 能力闭集 fail-closed：未知/大小写变体/空串拒绝；19 条目 34 键无别名碰撞
    - CRYPTO_PROXY 仅允许 approved-product scope（manifest 层强制；mvp-prototype 拒绝）
    - 框架抽象 PLANNER..HUMAN_GATE 可注册且可用于 Plan AGENT 节点（AC-3.3）
    - 双向一致性：orphan/unmapped 均为空（AC-3.4）
    - 下游兼容：AgentManifest.capability 由枚举改为规范字符串，无 src 内消费方依赖旧枚举
    - 判定：PASS；Critical=0 High=0；Low=2（观察项：未映射 MVP 分支无直接单测仅由一致性守卫覆盖；
      枚举新增成员需在下次全量 quality 回归中复核全仓枚举假设）

治理偏差说明：子代理并发额度受限（agent thread limit reached），独立 security-reviewer 未能以子代理形式
派发；改由编排器在只读沙箱内按 security-reviewer 技能与只读契约实际执行（只读、不落盘、证据来自沙箱内命令），
并在 DECISIONS.md 留痕。全量 `make quality` 按用户指示本轮豁免，留待下次回归。

```


## 2026-08-04T01:16:05.002565Z — target=`quality` fingerprint=`e3a61c2f23c3031b`
- exit_code: `0`
```text
ge_receipt_repository.MergeReceiptRepositorySecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 66.620s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 13 tests in 142.351s

OK
audit seal: fully-sealed

```


## 2026-08-04T01:16:51.009044Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
equests=16` Ĭ��ֵ����ÿ�����½����ӣ����Ϸ���� one-request-per-connection ������Ϊ����SLA p95��1.0s �� errors=0��`COCKPIT_HTTP_P95_LIMIT_SEC` ���������ο��ܹ���ͨҳ�� 3s��ʵ�� p95��0.52s ����һ����������`tests/unit/test_benchmark_http.py` 2 �������� ok / �ӳٱ߽�� result.limit����",
      "code": [
        "scripts/benchmark.py"
      ],
      "tests": [
        "tests/unit/test_benchmark_http.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/benchmark.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_benchmark_http.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-2",
      "title": "�̻����Ź�/��������ʽ Python ������·����2026-08-04���û�ָ�������������Ż������� `scripts/register-autostart.ps1` ���� `PinPython` ��������д `<install_root>\\python-path.txt`�������ƻ����񣬹�ˢ�³¾� pin����`Register` �ڴ����ƻ�����ǰ�̻��������Ľ���������ʽ `-PythonPath` �� PATH����дʧ�ܼ���ֹ���� `scripts/cockpit-watchdog.ps1` ���� `-PythonPath`������˳����ʽ���� �� sidecar �� PATH��sidecar ��/���·��/ָ��ȱʧ��������ʧ�ܹرգ�����Ĭ���ˣ����� `scripts/install_cockpit.py` ��װ/�����ɹ�ʱԭ��д�� `sys.executable`��ָ���л�ǰ��ʧ�ܼ���ֹ��װ������ �ĵ���ops-runbook ��2/��2.1 + known-limitations ��Ŀ���¡�",
      "code": [
        "scripts/register-autostart.ps1",
        "scripts/cockpit-watchdog.ps1",
        "scripts/install_cockpit.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py",
        "tests/unit/test_preflight_watchdog.py",
        "tests/integration/test_installer.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/register-autostart.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/install_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_installer.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "BACKUP-2",
      "title": "���������֤��2026-08-04���û�ָ�������������Ż�����`scripts/backup_state.py` ���� `--require-external`�������ݸ�λ�ڰ�װ���ڡ����밲װ��ͬ����`st_dev` �Ƚϣ�ʱʧ�ܹرգ���ֹ���̹���ͬʱ�ٵ������뱸�ݣ�manifest ���� `same_volume` �����ɶ��ֶι��Զ����˲飻���ݸ���Ŀ¼������д��Ŀ�겻�ɴ���ʱ�ɾ������������� traceback����`--require-external` �������� backup ������verify/restore �����ޣ��ĵ���ops-runbook ��4 ��ر���ʾ�� + known-limitations ������Ŀ���¡�",
      "code": [
        "scripts/backup_state.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/unit/test_backup_state.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/backup_state.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_backup_state.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-2",
      "title": "��Կɨ��ģʽ��չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� `pem_private_key` ���� `SM2 PRIVATE KEY`�����ܸ�ʽ��tests/ PEM �������岻�䣩���� `github_pat` ��չΪ���Ƽ��� `ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_`/`github_pat_`��fine-grained������ ���� `google_api_key`��`AIza`+35���� `npm_token`��`npm_`+36������ ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž��Զ����棨secret_scan ���裩��",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-3",
      "title": "����������ӱ������ʶȼ�أ�2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` ���� `backup` ��顪��ɨ�� `--backup-root`��Ĭ�� `<install-root>\\backups`����ȫ������ manifest��ȡ���� `created_at`������ �� `--max-backup-age-days`��Ĭ�� 7 �죩Ϊ ok�����ݸ�ȱʧ/����Ч manifest/����/δ��ʱ�����>1 �죩��Ϊ degraded���ָ���̬�澯������Ϸ��񣬲��� critical����CLI ���� `--backup-root` �� `--max-backup-age-days`��<1 �ܾ�����ֻ������ stdlib��docs/operations/ops-runbook.md ��1 ���� + ��ر��ݼ��ʾ����",
      "code": [
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-4",
      "title": "ģ���ⷢ�����ɹ۲��ԣ�2026-08-04���û�ָ�������������Ż�����`scripts/run_cockpit.py` ���� `model_egress_warnings()`�������� provider �ǻػ���https���� `external_data_ok=true`����������뿪���������������� `COEVO_LLM_EXTERNAL_DATA_OK=1` ������ʱ����澯��`--preflight` ���ɣ��ⷢ����/�������� �� degraded exit 1���ػ� provider �� offline ��Ĭ�����ݲ��������󱨣���ÿ�������� `setup_logging` д `model egress posture` �澯��־���������Ʊ��� fail-closed ���䣻�ĵ���configuration-reference ������ + ops-runbook ��2.1 �ⷢ��̬�ڡ�",
      "code": [
        "scripts/run_cockpit.py",
        "docs/operations/configuration-reference.md",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/configuration-reference.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
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


## 2026-08-04T01:28:58.765259Z — target=`quality` fingerprint=`e3a61c2f23c3031b`
- exit_code: `0`
```text
ge_receipt_repository.MergeReceiptRepositorySecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 62.544s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 13 tests in 143.008s

OK
audit seal: fully-sealed

```


## 2026-08-04T01:29:46.172741Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
      "tests/unit/test_preflight_watchdog.py",
        "tests/integration/test_installer.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/register-autostart.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/install_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_installer.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "BACKUP-2",
      "title": "���������֤��2026-08-04���û�ָ�������������Ż�����`scripts/backup_state.py` ���� `--require-external`�������ݸ�λ�ڰ�װ���ڡ����밲װ��ͬ����`st_dev` �Ƚϣ�ʱʧ�ܹرգ���ֹ���̹���ͬʱ�ٵ������뱸�ݣ�manifest ���� `same_volume` �����ɶ��ֶι��Զ����˲飻���ݸ���Ŀ¼������д��Ŀ�겻�ɴ���ʱ�ɾ������������� traceback����`--require-external` �������� backup ������verify/restore �����ޣ��ĵ���ops-runbook ��4 ��ر���ʾ�� + known-limitations ������Ŀ���¡�",
      "code": [
        "scripts/backup_state.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/unit/test_backup_state.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/backup_state.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_backup_state.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-2",
      "title": "��Կɨ��ģʽ��չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� `pem_private_key` ���� `SM2 PRIVATE KEY`�����ܸ�ʽ��tests/ PEM �������岻�䣩���� `github_pat` ��չΪ���Ƽ��� `ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_`/`github_pat_`��fine-grained������ ���� `google_api_key`��`AIza`+35���� `npm_token`��`npm_`+36������ ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž��Զ����棨secret_scan ���裩��",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-3",
      "title": "����������ӱ������ʶȼ�أ�2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` ���� `backup` ��顪��ɨ�� `--backup-root`��Ĭ�� `<install-root>\\backups`����ȫ������ manifest��ȡ���� `created_at`������ �� `--max-backup-age-days`��Ĭ�� 7 �죩Ϊ ok�����ݸ�ȱʧ/����Ч manifest/����/δ��ʱ�����>1 �죩��Ϊ degraded���ָ���̬�澯������Ϸ��񣬲��� critical����CLI ���� `--backup-root` �� `--max-backup-age-days`��<1 �ܾ�����ֻ������ stdlib��docs/operations/ops-runbook.md ��1 ���� + ��ر��ݼ��ʾ����",
      "code": [
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-4",
      "title": "ģ���ⷢ�����ɹ۲��ԣ�2026-08-04���û�ָ�������������Ż�����`scripts/run_cockpit.py` ���� `model_egress_warnings()`�������� provider �ǻػ���https���� `external_data_ok=true`����������뿪���������������� `COEVO_LLM_EXTERNAL_DATA_OK=1` ������ʱ����澯��`--preflight` ���ɣ��ⷢ����/�������� �� degraded exit 1���ػ� provider �� offline ��Ĭ�����ݲ��������󱨣���ÿ�������� `setup_logging` д `model egress posture` �澯��־���������Ʊ��� fail-closed ���䣻�ĵ���configuration-reference ������ + ops-runbook ��2.1 �ⷢ��̬�ڡ�",
      "code": [
        "scripts/run_cockpit.py",
        "docs/operations/configuration-reference.md",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/configuration-reference.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-5",
      "title": "������ pin �����Լ�飨2026-08-04���û�ָ�������������Ż�����`scripts/install_cockpit.py --action check` ���� pin У�顪��`python-path.txt` ȱʧ/��/�Ǿ���·��/Ŀ�겻���ھ� check ʧ�ܣ�exit 1�������� `register-autostart.ps1 -Action PinPython` ָ�����ջ� OPS-2 �ɰ�װȱ�ڣ������Ź���Ĭ���� PATH����`scripts/health_check.py` ���� `pin` ��顪��ȱʧ/��Ч �� degraded����ز�ɼ��ԣ������� `build_report`���ĵ���ops-runbook ��1 ���� pin �� + install check ǿ��˵����known-limitations OPS-2 ��Ŀ���¡�",
      "code": [
        "scripts/install_cockpit.py",
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_installer.py",
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/install_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_installer.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
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


## 2026-08-04T01:41:22.153712Z — target=`quality` fingerprint=`e3a61c2f23c3031b`
- exit_code: `0`
```text
ge_receipt_repository.MergeReceiptRepositorySecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 65.921s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 13 tests in 148.773s

OK
audit seal: fully-sealed

```


## 2026-08-04T01:42:08.569408Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
6-08-04���û�ָ�������������Ż�����`scripts/backup_state.py` ���� `--require-external`�������ݸ�λ�ڰ�װ���ڡ����밲װ��ͬ����`st_dev` �Ƚϣ�ʱʧ�ܹرգ���ֹ���̹���ͬʱ�ٵ������뱸�ݣ�manifest ���� `same_volume` �����ɶ��ֶι��Զ����˲飻���ݸ���Ŀ¼������д��Ŀ�겻�ɴ���ʱ�ɾ������������� traceback����`--require-external` �������� backup ������verify/restore �����ޣ��ĵ���ops-runbook ��4 ��ر���ʾ�� + known-limitations ������Ŀ���¡�",
      "code": [
        "scripts/backup_state.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/unit/test_backup_state.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/backup_state.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_backup_state.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-2",
      "title": "��Կɨ��ģʽ��չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� `pem_private_key` ���� `SM2 PRIVATE KEY`�����ܸ�ʽ��tests/ PEM �������岻�䣩���� `github_pat` ��չΪ���Ƽ��� `ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_`/`github_pat_`��fine-grained������ ���� `google_api_key`��`AIza`+35���� `npm_token`��`npm_`+36������ ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž��Զ����棨secret_scan ���裩��",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-3",
      "title": "����������ӱ������ʶȼ�أ�2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` ���� `backup` ��顪��ɨ�� `--backup-root`��Ĭ�� `<install-root>\\backups`����ȫ������ manifest��ȡ���� `created_at`������ �� `--max-backup-age-days`��Ĭ�� 7 �죩Ϊ ok�����ݸ�ȱʧ/����Ч manifest/����/δ��ʱ�����>1 �죩��Ϊ degraded���ָ���̬�澯������Ϸ��񣬲��� critical����CLI ���� `--backup-root` �� `--max-backup-age-days`��<1 �ܾ�����ֻ������ stdlib��docs/operations/ops-runbook.md ��1 ���� + ��ر��ݼ��ʾ����",
      "code": [
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-4",
      "title": "ģ���ⷢ�����ɹ۲��ԣ�2026-08-04���û�ָ�������������Ż�����`scripts/run_cockpit.py` ���� `model_egress_warnings()`�������� provider �ǻػ���https���� `external_data_ok=true`����������뿪���������������� `COEVO_LLM_EXTERNAL_DATA_OK=1` ������ʱ����澯��`--preflight` ���ɣ��ⷢ����/�������� �� degraded exit 1���ػ� provider �� offline ��Ĭ�����ݲ��������󱨣���ÿ�������� `setup_logging` д `model egress posture` �澯��־���������Ʊ��� fail-closed ���䣻�ĵ���configuration-reference ������ + ops-runbook ��2.1 �ⷢ��̬�ڡ�",
      "code": [
        "scripts/run_cockpit.py",
        "docs/operations/configuration-reference.md",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/configuration-reference.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-5",
      "title": "������ pin �����Լ�飨2026-08-04���û�ָ�������������Ż�����`scripts/install_cockpit.py --action check` ���� pin У�顪��`python-path.txt` ȱʧ/��/�Ǿ���·��/Ŀ�겻���ھ� check ʧ�ܣ�exit 1�������� `register-autostart.ps1 -Action PinPython` ָ�����ջ� OPS-2 �ɰ�װȱ�ڣ������Ź���Ĭ���� PATH����`scripts/health_check.py` ���� `pin` ��顪��ȱʧ/��Ч �� degraded����ز�ɼ��ԣ������� `build_report`���ĵ���ops-runbook ��1 ���� pin �� + install check ǿ��˵����known-limitations OPS-2 ��Ŀ���¡�",
      "code": [
        "scripts/install_cockpit.py",
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_installer.py",
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/install_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_installer.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "METRICS-2",
      "title": "/healthz ̽�������2026-08-04���û�ָ�������������Ż�����`src/coevo/cockpit/server.py` ���� `_probe_count`������ `_request_lock` �̰߳�ȫ������`/healthz` ���̽���������������֤ `request_count` ����������METRICS-1 ���岻�䣩��`/api/health` ��Ӧ���� `probe_count` �ֶΣ���ά�����ֿ��Ź�/�������/��׼̽����������ʵʹ�ã��ĵ���ops-runbook ��1 �����ڶ˵�˵�� + known-limitations request_count ��Ŀ���¡�",
      "code": [
        "src/coevo/cockpit/server.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
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


## 2026-08-04T01:58:01.124432Z — target=`quality` fingerprint=`e3a61c2f23c3031b`
- exit_code: `1`
```text
not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

======================================================================
FAIL: test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\e2e\test_cockpit_offline_frontend.py", line 108, in test_local_assets_load_and_have_no_external_urls
    self.assertNotIn("http://", text)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
AssertionError: 'http://' unexpectedly found in '(function () {\r\n  "use strict";\r\n\r\n  var token = new URLSearchParams(location.search).get("token")\r\n    || sessionStorage.getItem("cockpit_token")\r\n    || "";\r\n  if (token) {\r\n    sessionStorage.setItem("cockpit_token", token);\r\n    if (location.search) {\r\n      history.replaceState(null, "", location.pathname);\r\n    }\r\n  }\r\n\r\n  function api(path, options) {\r\n    var headers = { "X-Cockpit-Token": token };\r\n    var init = { headers: headers };\r\n    if (options && options.body) {\r\n      init.method = "POST";\r\n      init.headers["Content-Type"] = "application/json";\r\n      init.headers["X-Requested-With"] = "coevo-cockpit";\r\n      init.body = JSON.stringify(options.body);\r\n    }\r\n    return fetch(path, init).then(function (response) {\r\n      return response.json().then(function (data) {\r\n        return { code: response.status, data: data };\r\n      });\r\n    });\r\n  }\r\n\r\n  function setStatus(text, isError) {\r\n    var status = document.getElementById("status");\r\n    status.textContent = text;\r\n    status.classList.toggle("error", !!isError);\r\n  }\r\n\r\n  function el(tag, text) {\r\n    var node = document.createElement(tag);\r\n    if (text !== undefined && text !== null) {\r\n      node.textContent = String(text);\r\n    }\r\n    return node;\r\n  }\r\n\r\n  function showDetail(title) {\r\n    document.getElementById("detail-title").textContent = title;\r\n    document.getElementById("detail").hidden = false;\r\n  }\r\n\r\n  function renderRoles(roleView) {\r\n    var container = document.getElementById("roles");\r\n    container.textContent = "";\r\n    container.appendChild(el("h3", "Roles"));\r\n    var list = el("ul");\r\n    var role = el("li", roleView.data.payload.display_name + " (" + roleView.data.payload.role_id + ")");\r\n    role.appendChild(el("span", " - " + roleView.data.payload.task_count + " tasks"));\r\n    list.appendChild(role);\r\n    container.appendChild(list);\r\n  }\r\n\r\n  function renderTasks(roleView) {\r\n    var list = document.getElementById("tasks");\r\n    list.textContent = "";\r\n    (roleView.data.payload.tasks || []).forEach(function (task) {\r\n      var item = el("li", task.title + " [" + task.status + "] due " + task.due_at);\r\n      list.appendChild(item);\r\n    });\r\n  }\r\n\r\n  function renderMilestones(roleView) {\r\n    var list = document.getElementById("milestones");\r\n    list.textContent = "";\r\n    (roleView.data.payload.milestones || []).forEach(function (milestone) {\r\n      var item = el("li", milestone.title + (milestone.completed ? " (done)" : " (open)"));\r\n      list.appendChild(item);\r\n    });\r\n  }\r\n\r\n  function renderArtifacts(roleView) {\r\n    var list = document.getElementById("artifacts");\r\n    list.textContent = "";\r\n    (roleView.data.payload.artifacts || []).forEach(function (artifact) {\r\n      var item = el("li", artifact.path);\r\n      var button = el("button", "Open in WPS");\r\n      button.addEventListener("click", function () {\r\n        api("/api/wps_open", {\r\n          body: { project_id: roleView.data.payload.project_id, artifact_path: artifact.path, confirm: true },\r\n        }).then(function (result) {\r\n          setStatus(result.data.task || "WPS request accepted", result.code !== 200);\r\n        });\r\n      });\r\n      item.appendChild(button);\r\n      list.appendChild(item);\r\n    });\r\n  }\r\n\r\n  function loadRole(projectId, roleId) {\r\n    return api("/api/role_view?project_id=" + encodeURIComponent(projectId)\r\n      + "&role_id=" + encodeURIComponent(roleId)).then(function (result) {\r\n      if (result.code !== 200) {\r\n        throw new Error(result.data.error || "role view failed");\r\n      }\r\n      return result;\r\n    });\r\n  }\r\n\r\n  function openProject(projectId, displayName) {\r\n    showDetail(displayName + " (" + projectId + ")");\r\n    document.getElementById("roles").textContent = "Loading roles?";\r\n    return api("/api/list_roles?project_id=" + encodeURIComponent(projectId)).then(function (result) {\r\n      if (result.code !== 200) {\r\n        throw new Error(result.data.error || "roles failed");\r\n      }\r\n      var roles = result.data.payload.roles || [];\r\n      if (roles.length === 0) {\r\n        document.getElementById("roles").textContent = "No roles.";\r\n        return;\r\n      }\r\n      var first = roles[0];\r\n      return loadRole(projectId, first).then(function (roleView) {\r\n        renderRoles(roleView);\r\n        renderTasks(roleView);\r\n        renderMilestones(roleView);\r\n        renderArtifacts(roleView);\r\n      });\r\n    }).catch(function (err) {\r\n      setStatus(err.message, true);\r\n    });\r\n  }\r\n\r\n  function loadProjects() {\r\n    var list = document.getElementById("project-list");\r\n    list.textContent = "";\r\n    setStatus("Loading projects?");\r\n    return api("/api/list_projects").then(function (result) {\r\n      if (result.code !== 200) {\r\n        throw new Error(result.data.error || "list failed");\r\n      }\r\n      setStatus("Connected.");\r\n      var projects = result.data.payload.projects || [];\r\n      if (projects.length === 0) {\r\n        list.appendChild(el("li", "(no projects)"));\r\n        return;\r\n      }\r\n      projects.forEach(function (projectId) {\r\n        var item = el("li", projectId);\r\n        item.classList.add("project");\r\n        item.addEventListener("click", function () {\r\n          openProject(projectId, projectId);\r\n        });\r\n        list.appendChild(item);\r\n      });\r\n    }).catch(function (err) {\r\n      setStatus(err.message, true);\r\n    });\r\n  }\r\n\r\n  if (!token) {\n    setStatus(\n      "No session token. Start the cockpit with --print-token and open " +\n      "the printed URL (http://127.0.0.1:12701/?token=...).",\n      true\n    );\n    return;\n  }\n  loadProjects();\r\n})();\r\n'

----------------------------------------------------------------------
Ran 14 tests in 141.430s

FAILED (failures=1)

```


## 2026-08-04T02:07:51.147788Z — target=`quality` fingerprint=`e3a61c2f23c3031b`
- exit_code: `0`
```text
ejected_by_freshness_checkpoint (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_truncation_is_rejected_by_freshness_checkpoint) ... ok
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
Ran 97 tests in 67.617s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 147.767s

OK
audit seal: fully-sealed

```


## 2026-08-04T02:08:44.224831Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
s": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-3",
      "title": "����������ӱ������ʶȼ�أ�2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` ���� `backup` ��顪��ɨ�� `--backup-root`��Ĭ�� `<install-root>\\backups`����ȫ������ manifest��ȡ���� `created_at`������ �� `--max-backup-age-days`��Ĭ�� 7 �죩Ϊ ok�����ݸ�ȱʧ/����Ч manifest/����/δ��ʱ�����>1 �죩��Ϊ degraded���ָ���̬�澯������Ϸ��񣬲��� critical����CLI ���� `--backup-root` �� `--max-backup-age-days`��<1 �ܾ�����ֻ������ stdlib��docs/operations/ops-runbook.md ��1 ���� + ��ر��ݼ��ʾ����",
      "code": [
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-4",
      "title": "ģ���ⷢ�����ɹ۲��ԣ�2026-08-04���û�ָ�������������Ż�����`scripts/run_cockpit.py` ���� `model_egress_warnings()`�������� provider �ǻػ���https���� `external_data_ok=true`����������뿪���������������� `COEVO_LLM_EXTERNAL_DATA_OK=1` ������ʱ����澯��`--preflight` ���ɣ��ⷢ����/�������� �� degraded exit 1���ػ� provider �� offline ��Ĭ�����ݲ��������󱨣���ÿ�������� `setup_logging` д `model egress posture` �澯��־���������Ʊ��� fail-closed ���䣻�ĵ���configuration-reference ������ + ops-runbook ��2.1 �ⷢ��̬�ڡ�",
      "code": [
        "scripts/run_cockpit.py",
        "docs/operations/configuration-reference.md",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/configuration-reference.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-5",
      "title": "������ pin �����Լ�飨2026-08-04���û�ָ�������������Ż�����`scripts/install_cockpit.py --action check` ���� pin У�顪��`python-path.txt` ȱʧ/��/�Ǿ���·��/Ŀ�겻���ھ� check ʧ�ܣ�exit 1�������� `register-autostart.ps1 -Action PinPython` ָ�����ջ� OPS-2 �ɰ�װȱ�ڣ������Ź���Ĭ���� PATH����`scripts/health_check.py` ���� `pin` ��顪��ȱʧ/��Ч �� degraded����ز�ɼ��ԣ������� `build_report`���ĵ���ops-runbook ��1 ���� pin �� + install check ǿ��˵����known-limitations OPS-2 ��Ŀ���¡�",
      "code": [
        "scripts/install_cockpit.py",
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_installer.py",
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/install_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_installer.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "METRICS-2",
      "title": "/healthz ̽�������2026-08-04���û�ָ�������������Ż�����`src/coevo/cockpit/server.py` ���� `_probe_count`������ `_request_lock` �̰߳�ȫ������`/healthz` ���̽���������������֤ `request_count` ����������METRICS-1 ���岻�䣩��`/api/health` ��Ӧ���� `probe_count` �ֶΣ���ά�����ֿ��Ź�/�������/��׼̽����������ʵʹ�ã��ĵ���ops-runbook ��1 �����ڶ˵�˵�� + known-limitations request_count ��Ŀ���¡�",
      "code": [
        "src/coevo/cockpit/server.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "REVIEW-FIX-2",
      "title": "�������������޸���2026-08-04���û�ָ�������������Ż������� `scripts/run_cockpit.py` ���� `--print-token`���������� `session_manager.create()` ǩ��һ�λỰ���ƴ�ӡ�� stdout��flush ��ʱ�ɼ���������־��ܡ������̣�����˽��� SHA-256 ժҪ�����ջ���������\"��֤�ӿ�������ǩ��·��\"��ȱ�ڣ�ops-runbook ��2.2 ����ʽ����˵����`static/app.js` ��������ʾָ�� `--print-token`���� URL �����������������ʲ������������������� `src/coevo/cockpit/server.py` �������� 503 �ɹ۲⡪������ `rejected_count`���̰߳�ȫ����¶�� `/api/health`��`_reject_busy` д�н� `busy_rejected` ������־�У��� client_host/reason�������������ݣ���",
      "code": [
        "scripts/run_cockpit.py",
        "src/coevo/cockpit/server.py",
        "src/coevo/cockpit/static/app.js",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/e2e/test_cockpit_launcher.py",
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/static/app.js",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
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


## 2026-08-04T02:19:42.754055Z — target=`quality` fingerprint=`e3a61c2f23c3031b`
- exit_code: `0`
```text
ejected_by_freshness_checkpoint (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_truncation_is_rejected_by_freshness_checkpoint) ... ok
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
Ran 97 tests in 68.916s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 150.025s

OK
audit seal: fully-sealed

```


## 2026-08-04T02:20:29.653156Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `1`
```text
unbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-4",
      "title": "ģ���ⷢ�����ɹ۲��ԣ�2026-08-04���û�ָ�������������Ż�����`scripts/run_cockpit.py` ���� `model_egress_warnings()`�������� provider �ǻػ���https���� `external_data_ok=true`����������뿪���������������� `COEVO_LLM_EXTERNAL_DATA_OK=1` ������ʱ����澯��`--preflight` ���ɣ��ⷢ����/�������� �� degraded exit 1���ػ� provider �� offline ��Ĭ�����ݲ��������󱨣���ÿ�������� `setup_logging` д `model egress posture` �澯��־���������Ʊ��� fail-closed ���䣻�ĵ���configuration-reference ������ + ops-runbook ��2.1 �ⷢ��̬�ڡ�",
      "code": [
        "scripts/run_cockpit.py",
        "docs/operations/configuration-reference.md",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/configuration-reference.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-5",
      "title": "������ pin �����Լ�飨2026-08-04���û�ָ�������������Ż�����`scripts/install_cockpit.py --action check` ���� pin У�顪��`python-path.txt` ȱʧ/��/�Ǿ���·��/Ŀ�겻���ھ� check ʧ�ܣ�exit 1�������� `register-autostart.ps1 -Action PinPython` ָ�����ջ� OPS-2 �ɰ�װȱ�ڣ������Ź���Ĭ���� PATH����`scripts/health_check.py` ���� `pin` ��顪��ȱʧ/��Ч �� degraded����ز�ɼ��ԣ������� `build_report`���ĵ���ops-runbook ��1 ���� pin �� + install check ǿ��˵����known-limitations OPS-2 ��Ŀ���¡�",
      "code": [
        "scripts/install_cockpit.py",
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_installer.py",
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/install_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_installer.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "METRICS-2",
      "title": "/healthz ̽�������2026-08-04���û�ָ�������������Ż�����`src/coevo/cockpit/server.py` ���� `_probe_count`������ `_request_lock` �̰߳�ȫ������`/healthz` ���̽���������������֤ `request_count` ����������METRICS-1 ���岻�䣩��`/api/health` ��Ӧ���� `probe_count` �ֶΣ���ά�����ֿ��Ź�/�������/��׼̽����������ʵʹ�ã��ĵ���ops-runbook ��1 �����ڶ˵�˵�� + known-limitations request_count ��Ŀ���¡�",
      "code": [
        "src/coevo/cockpit/server.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "REVIEW-FIX-2",
      "title": "�������������޸���2026-08-04���û�ָ�������������Ż������� `scripts/run_cockpit.py` ���� `--print-token`���������� `session_manager.create()` ǩ��һ�λỰ���ƴ�ӡ�� stdout��flush ��ʱ�ɼ���������־��ܡ������̣�����˽��� SHA-256 ժҪ�����ջ���������\"��֤�ӿ�������ǩ��·��\"��ȱ�ڣ�ops-runbook ��2.2 ����ʽ����˵����`static/app.js` ��������ʾָ�� `--print-token`���� URL �����������������ʲ������������������� `src/coevo/cockpit/server.py` �������� 503 �ɹ۲⡪������ `rejected_count`���̰߳�ȫ����¶�� `/api/health`��`_reject_busy` д�н� `busy_rejected` ������־�У��� client_host/reason�������������ݣ���",
      "code": [
        "scripts/run_cockpit.py",
        "src/coevo/cockpit/server.py",
        "src/coevo/cockpit/static/app.js",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/e2e/test_cockpit_launcher.py",
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/static/app.js",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-3",
      "title": "��Կɨ��ģʽ����չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� ���� `stripe_key`��`sk_live_`/`sk_test_`/`rk_live_`+16+��Stripe ��ʵ/����/������Կ������ ���� `sendgrid_key`��`SG.<22>.<20>`������ ���� `pgp_private_key`��`PGP PRIVATE KEY BLOCK`������ tests/ PEM �������壩���� ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž� secret_scan �����Զ����档",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
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
SECRET pgp_private_key: loop/DECISIONS.md:4091 (-----BEGIN PGP PRIVATE KEY BLOCK-----)

```


## 2026-08-04T02:20:54.585980Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
ealth_check.py",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-4",
      "title": "ģ���ⷢ�����ɹ۲��ԣ�2026-08-04���û�ָ�������������Ż�����`scripts/run_cockpit.py` ���� `model_egress_warnings()`�������� provider �ǻػ���https���� `external_data_ok=true`����������뿪���������������� `COEVO_LLM_EXTERNAL_DATA_OK=1` ������ʱ����澯��`--preflight` ���ɣ��ⷢ����/�������� �� degraded exit 1���ػ� provider �� offline ��Ĭ�����ݲ��������󱨣���ÿ�������� `setup_logging` д `model egress posture` �澯��־���������Ʊ��� fail-closed ���䣻�ĵ���configuration-reference ������ + ops-runbook ��2.1 �ⷢ��̬�ڡ�",
      "code": [
        "scripts/run_cockpit.py",
        "docs/operations/configuration-reference.md",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/configuration-reference.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-5",
      "title": "������ pin �����Լ�飨2026-08-04���û�ָ�������������Ż�����`scripts/install_cockpit.py --action check` ���� pin У�顪��`python-path.txt` ȱʧ/��/�Ǿ���·��/Ŀ�겻���ھ� check ʧ�ܣ�exit 1�������� `register-autostart.ps1 -Action PinPython` ָ�����ջ� OPS-2 �ɰ�װȱ�ڣ������Ź���Ĭ���� PATH����`scripts/health_check.py` ���� `pin` ��顪��ȱʧ/��Ч �� degraded����ز�ɼ��ԣ������� `build_report`���ĵ���ops-runbook ��1 ���� pin �� + install check ǿ��˵����known-limitations OPS-2 ��Ŀ���¡�",
      "code": [
        "scripts/install_cockpit.py",
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_installer.py",
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/install_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_installer.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "METRICS-2",
      "title": "/healthz ̽�������2026-08-04���û�ָ�������������Ż�����`src/coevo/cockpit/server.py` ���� `_probe_count`������ `_request_lock` �̰߳�ȫ������`/healthz` ���̽���������������֤ `request_count` ����������METRICS-1 ���岻�䣩��`/api/health` ��Ӧ���� `probe_count` �ֶΣ���ά�����ֿ��Ź�/�������/��׼̽����������ʵʹ�ã��ĵ���ops-runbook ��1 �����ڶ˵�˵�� + known-limitations request_count ��Ŀ���¡�",
      "code": [
        "src/coevo/cockpit/server.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "REVIEW-FIX-2",
      "title": "�������������޸���2026-08-04���û�ָ�������������Ż������� `scripts/run_cockpit.py` ���� `--print-token`���������� `session_manager.create()` ǩ��һ�λỰ���ƴ�ӡ�� stdout��flush ��ʱ�ɼ���������־��ܡ������̣�����˽��� SHA-256 ժҪ�����ջ���������\"��֤�ӿ�������ǩ��·��\"��ȱ�ڣ�ops-runbook ��2.2 ����ʽ����˵����`static/app.js` ��������ʾָ�� `--print-token`���� URL �����������������ʲ������������������� `src/coevo/cockpit/server.py` �������� 503 �ɹ۲⡪������ `rejected_count`���̰߳�ȫ����¶�� `/api/health`��`_reject_busy` д�н� `busy_rejected` ������־�У��� client_host/reason�������������ݣ���",
      "code": [
        "scripts/run_cockpit.py",
        "src/coevo/cockpit/server.py",
        "src/coevo/cockpit/static/app.js",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/e2e/test_cockpit_launcher.py",
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/static/app.js",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-3",
      "title": "��Կɨ��ģʽ����չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� ���� `stripe_key`��`sk_live_`/`sk_test_`/`rk_live_`+16+��Stripe ��ʵ/����/������Կ������ ���� `sendgrid_key`��`SG.<22>.<20>`������ ���� `pgp_private_key`��`PGP PRIVATE KEY BLOCK`������ tests/ PEM �������壩���� ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž� secret_scan �����Զ����档",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
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


## 2026-08-04T02:32:35.844945Z — target=`quality` fingerprint=`e3a61c2f23c3031b`
- exit_code: `0`
```text
ejected_by_freshness_checkpoint (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_truncation_is_rejected_by_freshness_checkpoint) ... ok
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
Ran 97 tests in 66.793s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 141.450s

OK
audit seal: fully-sealed

```


## 2026-08-04T02:33:39.870284Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/configuration-reference.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-5",
      "title": "������ pin �����Լ�飨2026-08-04���û�ָ�������������Ż�����`scripts/install_cockpit.py --action check` ���� pin У�顪��`python-path.txt` ȱʧ/��/�Ǿ���·��/Ŀ�겻���ھ� check ʧ�ܣ�exit 1�������� `register-autostart.ps1 -Action PinPython` ָ�����ջ� OPS-2 �ɰ�װȱ�ڣ������Ź���Ĭ���� PATH����`scripts/health_check.py` ���� `pin` ��顪��ȱʧ/��Ч �� degraded����ز�ɼ��ԣ������� `build_report`���ĵ���ops-runbook ��1 ���� pin �� + install check ǿ��˵����known-limitations OPS-2 ��Ŀ���¡�",
      "code": [
        "scripts/install_cockpit.py",
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_installer.py",
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/install_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_installer.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "METRICS-2",
      "title": "/healthz ̽�������2026-08-04���û�ָ�������������Ż�����`src/coevo/cockpit/server.py` ���� `_probe_count`������ `_request_lock` �̰߳�ȫ������`/healthz` ���̽���������������֤ `request_count` ����������METRICS-1 ���岻�䣩��`/api/health` ��Ӧ���� `probe_count` �ֶΣ���ά�����ֿ��Ź�/�������/��׼̽����������ʵʹ�ã��ĵ���ops-runbook ��1 �����ڶ˵�˵�� + known-limitations request_count ��Ŀ���¡�",
      "code": [
        "src/coevo/cockpit/server.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "REVIEW-FIX-2",
      "title": "�������������޸���2026-08-04���û�ָ�������������Ż������� `scripts/run_cockpit.py` ���� `--print-token`���������� `session_manager.create()` ǩ��һ�λỰ���ƴ�ӡ�� stdout��flush ��ʱ�ɼ���������־��ܡ������̣�����˽��� SHA-256 ժҪ�����ջ���������\"��֤�ӿ�������ǩ��·��\"��ȱ�ڣ�ops-runbook ��2.2 ����ʽ����˵����`static/app.js` ��������ʾָ�� `--print-token`���� URL �����������������ʲ������������������� `src/coevo/cockpit/server.py` �������� 503 �ɹ۲⡪������ `rejected_count`���̰߳�ȫ����¶�� `/api/health`��`_reject_busy` д�н� `busy_rejected` ������־�У��� client_host/reason�������������ݣ���",
      "code": [
        "scripts/run_cockpit.py",
        "src/coevo/cockpit/server.py",
        "src/coevo/cockpit/static/app.js",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/e2e/test_cockpit_launcher.py",
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/static/app.js",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-3",
      "title": "��Կɨ��ģʽ����չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� ���� `stripe_key`��`sk_live_`/`sk_test_`/`rk_live_`+16+��Stripe ��ʵ/����/������Կ������ ���� `sendgrid_key`��`SG.<22>.<20>`������ ���� `pgp_private_key`��`PGP PRIVATE KEY BLOCK`������ tests/ PEM �������壩���� ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž� secret_scan �����Զ����档",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "AVAIL-2",
      "title": "����̽����Ӧ����У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` `check_cockpit`����`/healthz` �� HTTP 200 ��У����Ӧ�� `service=coevo-cockpit` �� `status=ok`����ֹ�˿ڱ���������ռ��ʱ���н��������ǽ��������ɴ�/�� 200/�������/�����壩ͳһ degraded��������ǰ�� 200 �� critical ���ĵ�����Ĳ�һ�£�`scripts/cockpit-watchdog.ps1` `Test-CockpitHealth` ͬ��У����Ӧ�����ݣ��ĵ���ops-runbook ��1 cockpit �� + ��2.1 �����ж�˵����",
      "code": [
        "scripts/health_check.py",
        "scripts/cockpit-watchdog.ps1",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py",
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
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


## 2026-08-04T02:45:13.187921Z — target=`quality` fingerprint=`e3a61c2f23c3031b`
- exit_code: `0`
```text
ejected_by_freshness_checkpoint (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_truncation_is_rejected_by_freshness_checkpoint) ... ok
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
Ran 97 tests in 68.271s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 139.975s

OK
audit seal: fully-sealed

```


## 2026-08-04T02:46:06.856794Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
,
      "code": [
        "scripts/install_cockpit.py",
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_installer.py",
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/install_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_installer.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "METRICS-2",
      "title": "/healthz ̽�������2026-08-04���û�ָ�������������Ż�����`src/coevo/cockpit/server.py` ���� `_probe_count`������ `_request_lock` �̰߳�ȫ������`/healthz` ���̽���������������֤ `request_count` ����������METRICS-1 ���岻�䣩��`/api/health` ��Ӧ���� `probe_count` �ֶΣ���ά�����ֿ��Ź�/�������/��׼̽����������ʵʹ�ã��ĵ���ops-runbook ��1 �����ڶ˵�˵�� + known-limitations request_count ��Ŀ���¡�",
      "code": [
        "src/coevo/cockpit/server.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "REVIEW-FIX-2",
      "title": "�������������޸���2026-08-04���û�ָ�������������Ż������� `scripts/run_cockpit.py` ���� `--print-token`���������� `session_manager.create()` ǩ��һ�λỰ���ƴ�ӡ�� stdout��flush ��ʱ�ɼ���������־��ܡ������̣�����˽��� SHA-256 ժҪ�����ջ���������\"��֤�ӿ�������ǩ��·��\"��ȱ�ڣ�ops-runbook ��2.2 ����ʽ����˵����`static/app.js` ��������ʾָ�� `--print-token`���� URL �����������������ʲ������������������� `src/coevo/cockpit/server.py` �������� 503 �ɹ۲⡪������ `rejected_count`���̰߳�ȫ����¶�� `/api/health`��`_reject_busy` д�н� `busy_rejected` ������־�У��� client_host/reason�������������ݣ���",
      "code": [
        "scripts/run_cockpit.py",
        "src/coevo/cockpit/server.py",
        "src/coevo/cockpit/static/app.js",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/e2e/test_cockpit_launcher.py",
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/static/app.js",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-3",
      "title": "��Կɨ��ģʽ����չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� ���� `stripe_key`��`sk_live_`/`sk_test_`/`rk_live_`+16+��Stripe ��ʵ/����/������Կ������ ���� `sendgrid_key`��`SG.<22>.<20>`������ ���� `pgp_private_key`��`PGP PRIVATE KEY BLOCK`������ tests/ PEM �������壩���� ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž� secret_scan �����Զ����档",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "AVAIL-2",
      "title": "����̽����Ӧ����У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` `check_cockpit`����`/healthz` �� HTTP 200 ��У����Ӧ�� `service=coevo-cockpit` �� `status=ok`����ֹ�˿ڱ���������ռ��ʱ���н��������ǽ��������ɴ�/�� 200/�������/�����壩ͳһ degraded��������ǰ�� 200 �� critical ���ĵ�����Ĳ�һ�£�`scripts/cockpit-watchdog.ps1` `Test-CockpitHealth` ͬ��У����Ӧ�����ݣ��ĵ���ops-runbook ��1 cockpit �� + ��2.1 �����ж�˵����",
      "code": [
        "scripts/health_check.py",
        "scripts/cockpit-watchdog.ps1",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py",
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-6",
      "title": "������鱸��������У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` ���� `--verify-backups`���������±���ִ�� `backup_state.py verify`�������Թ�ϣУ�飻�ӽ��� 120s ��ʱ fail-closed������ȱʧ/ʧ��/��ʱ �� degraded�����ɹ�ʱ detail �� `integrity=ok`��У��������ʶ� ok ʱִ�У���ѡ���н�ɱ����ջ� OPS-3 ��\"������У�����ֶ�\"�߽磩���ĵ���ops-runbook ��1 backup �� + ʾ����",
      "code": [
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
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


## 2026-08-04T02:58:26.866875Z — target=`quality` fingerprint=`e3a61c2f23c3031b`
- exit_code: `0`
```text
ejected_by_freshness_checkpoint (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_truncation_is_rejected_by_freshness_checkpoint) ... ok
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
Ran 97 tests in 66.145s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 141.111s

OK
audit seal: fully-sealed

```


## 2026-08-04T02:59:29.870217Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
er.py` ���� `_probe_count`������ `_request_lock` �̰߳�ȫ������`/healthz` ���̽���������������֤ `request_count` ����������METRICS-1 ���岻�䣩��`/api/health` ��Ӧ���� `probe_count` �ֶΣ���ά�����ֿ��Ź�/�������/��׼̽����������ʵʹ�ã��ĵ���ops-runbook ��1 �����ڶ˵�˵�� + known-limitations request_count ��Ŀ���¡�",
      "code": [
        "src/coevo/cockpit/server.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "REVIEW-FIX-2",
      "title": "�������������޸���2026-08-04���û�ָ�������������Ż������� `scripts/run_cockpit.py` ���� `--print-token`���������� `session_manager.create()` ǩ��һ�λỰ���ƴ�ӡ�� stdout��flush ��ʱ�ɼ���������־��ܡ������̣�����˽��� SHA-256 ժҪ�����ջ���������\"��֤�ӿ�������ǩ��·��\"��ȱ�ڣ�ops-runbook ��2.2 ����ʽ����˵����`static/app.js` ��������ʾָ�� `--print-token`���� URL �����������������ʲ������������������� `src/coevo/cockpit/server.py` �������� 503 �ɹ۲⡪������ `rejected_count`���̰߳�ȫ����¶�� `/api/health`��`_reject_busy` д�н� `busy_rejected` ������־�У��� client_host/reason�������������ݣ���",
      "code": [
        "scripts/run_cockpit.py",
        "src/coevo/cockpit/server.py",
        "src/coevo/cockpit/static/app.js",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/e2e/test_cockpit_launcher.py",
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/static/app.js",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-3",
      "title": "��Կɨ��ģʽ����չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� ���� `stripe_key`��`sk_live_`/`sk_test_`/`rk_live_`+16+��Stripe ��ʵ/����/������Կ������ ���� `sendgrid_key`��`SG.<22>.<20>`������ ���� `pgp_private_key`��`PGP PRIVATE KEY BLOCK`������ tests/ PEM �������壩���� ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž� secret_scan �����Զ����档",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "AVAIL-2",
      "title": "����̽����Ӧ����У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` `check_cockpit`����`/healthz` �� HTTP 200 ��У����Ӧ�� `service=coevo-cockpit` �� `status=ok`����ֹ�˿ڱ���������ռ��ʱ���н��������ǽ��������ɴ�/�� 200/�������/�����壩ͳһ degraded��������ǰ�� 200 �� critical ���ĵ�����Ĳ�һ�£�`scripts/cockpit-watchdog.ps1` `Test-CockpitHealth` ͬ��У����Ӧ�����ݣ��ĵ���ops-runbook ��1 cockpit �� + ��2.1 �����ж�˵����",
      "code": [
        "scripts/health_check.py",
        "scripts/cockpit-watchdog.ps1",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py",
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-6",
      "title": "������鱸��������У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` ���� `--verify-backups`���������±���ִ�� `backup_state.py verify`�������Թ�ϣУ�飻�ӽ��� 120s ��ʱ fail-closed������ȱʧ/ʧ��/��ʱ �� degraded�����ɹ�ʱ detail �� `integrity=ok`��У��������ʶ� ok ʱִ�У���ѡ���н�ɱ����ջ� OPS-3 ��\"������У�����ֶ�\"�߽磩���ĵ���ops-runbook ��1 backup �� + ʾ����",
      "code": [
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "AVAIL-3",
      "title": "���Ź�����Ԥ�㣨2026-08-04���û�ָ�������������Ż��������� `scripts/restart-budget.ps1`���������� `Test-RestartBudget`���������������� `< MaxRestarts` �����������ɱ����Ź� dot-source��Ҳ�ɶ������й����ԣ�`scripts/cockpit-watchdog.ps1` ���� `-MaxRestarts`��Ĭ�� 5���� `-RestartWindowSeconds`��Ĭ�� 3600��������ǰ�ж�Ԥ�㣬�ľ�ʱ������ѯ��ֹͣ��������ӡ manual intervention required�����ڹ�����ָ������ĵ���ops-runbook ��2.1 ����Ԥ��˵����",
      "code": [
        "scripts/restart-budget.ps1",
        "scripts/cockpit-watchdog.ps1",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/restart-budget.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
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


## 2026-08-04T09:54:31.038826Z — target=`fmt` fingerprint=`e225df61158f8ccf`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ C:\Users\liq08\AppData\Local\Temp\coevo-ci-restore-smoke-1baf824e1ca147028af950d923f27595\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```


## 2026-08-04T09:54:45.105877Z — target=`lint` fingerprint=`4e9985cfc154f025`
- exit_code: `0`
```text
n-limitations request_count ��Ŀ���¡�",
      "code": [
        "src/coevo/cockpit/server.py",
        "docs/operations/ops-runbook.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "REVIEW-FIX-2",
      "title": "�������������޸���2026-08-04���û�ָ�������������Ż������� `scripts/run_cockpit.py` ���� `--print-token`���������� `session_manager.create()` ǩ��һ�λỰ���ƴ�ӡ�� stdout��flush ��ʱ�ɼ���������־��ܡ������̣�����˽��� SHA-256 ժҪ�����ջ���������\"��֤�ӿ�������ǩ��·��\"��ȱ�ڣ�ops-runbook ��2.2 ����ʽ����˵����`static/app.js` ��������ʾָ�� `--print-token`���� URL �����������������ʲ������������������� `src/coevo/cockpit/server.py` �������� 503 �ɹ۲⡪������ `rejected_count`���̰߳�ȫ����¶�� `/api/health`��`_reject_busy` д�н� `busy_rejected` ������־�У��� client_host/reason�������������ݣ���",
      "code": [
        "scripts/run_cockpit.py",
        "src/coevo/cockpit/server.py",
        "src/coevo/cockpit/static/app.js",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/e2e/test_cockpit_launcher.py",
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/static/app.js",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-3",
      "title": "��Կɨ��ģʽ����չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� ���� `stripe_key`��`sk_live_`/`sk_test_`/`rk_live_`+16+��Stripe ��ʵ/����/������Կ������ ���� `sendgrid_key`��`SG.<22>.<20>`������ ���� `pgp_private_key`��`PGP PRIVATE KEY BLOCK`������ tests/ PEM �������壩���� ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž� secret_scan �����Զ����档",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "AVAIL-2",
      "title": "����̽����Ӧ����У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` `check_cockpit`����`/healthz` �� HTTP 200 ��У����Ӧ�� `service=coevo-cockpit` �� `status=ok`����ֹ�˿ڱ���������ռ��ʱ���н��������ǽ��������ɴ�/�� 200/�������/�����壩ͳһ degraded��������ǰ�� 200 �� critical ���ĵ�����Ĳ�һ�£�`scripts/cockpit-watchdog.ps1` `Test-CockpitHealth` ͬ��У����Ӧ�����ݣ��ĵ���ops-runbook ��1 cockpit �� + ��2.1 �����ж�˵����",
      "code": [
        "scripts/health_check.py",
        "scripts/cockpit-watchdog.ps1",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py",
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-6",
      "title": "������鱸��������У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` ���� `--verify-backups`���������±���ִ�� `backup_state.py verify`�������Թ�ϣУ�飻�ӽ��� 120s ��ʱ fail-closed������ȱʧ/ʧ��/��ʱ �� degraded�����ɹ�ʱ detail �� `integrity=ok`��У��������ʶ� ok ʱִ�У���ѡ���н�ɱ����ջ� OPS-3 ��\"������У�����ֶ�\"�߽磩���ĵ���ops-runbook ��1 backup �� + ʾ����",
      "code": [
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "AVAIL-3",
      "title": "���Ź�����Ԥ�㣨2026-08-04���û�ָ�������������Ż��������� `scripts/restart-budget.ps1`���������� `Test-RestartBudget`���������������� `< MaxRestarts` �����������ɱ����Ź� dot-source��Ҳ�ɶ������й����ԣ�`scripts/cockpit-watchdog.ps1` ���� `-MaxRestarts`��Ĭ�� 5���� `-RestartWindowSeconds`��Ĭ�� 3600��������ǰ�ж�Ԥ�㣬�ľ�ʱ������ѯ��ֹͣ��������ӡ manual intervention required�����ڹ�����ָ������ĵ���ops-runbook ��2.1 ����Ԥ��˵����",
      "code": [
        "scripts/restart-budget.ps1",
        "scripts/cockpit-watchdog.ps1",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/restart-budget.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    }
  ]
}
$ C:\Users\liq08\AppData\Local\Temp\coevo-ci-restore-smoke-1baf824e1ca147028af950d923f27595\python\3.14.3\python.exe C:\Users\liq08\AppData\Local\Temp\coevo-ci-restore-smoke-1baf824e1ca147028af950d923f27595\control\control.pyz audit_log verify
{"ok": true, "errors": []}
$ C:\Users\liq08\AppData\Local\Temp\coevo-ci-restore-smoke-1baf824e1ca147028af950d923f27595\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\audit_seal.py verify --allow-tail
{"ok": true, "status": "fully-sealed"}
$ C:\Users\liq08\AppData\Local\Temp\coevo-ci-restore-smoke-1baf824e1ca147028af950d923f27595\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\secret_scan.py
secret scan ok
audit seal: fully-sealed

```


## 2026-08-04T10:06:24.893884Z — target=`quality` fingerprint=`e3a61c2f23c3031b`
- exit_code: `0`
```text
ejected_by_freshness_checkpoint (test_merge_receipt_repository.MergeReceiptRepositorySecurityTests.test_truncation_is_rejected_by_freshness_checkpoint) ... ok
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
Ran 97 tests in 71.979s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
E:\Workspace\Coevo\.tools\python\3.14.3\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... E:\Workspace\Coevo\.tools\python\3.14.3\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 153.032s

OK
audit seal: fully-sealed

```


## 2026-08-04T10:07:15.815633Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
health`��`_reject_busy` д�н� `busy_rejected` ������־�У��� client_host/reason�������������ݣ���",
      "code": [
        "scripts/run_cockpit.py",
        "src/coevo/cockpit/server.py",
        "src/coevo/cockpit/static/app.js",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/e2e/test_cockpit_launcher.py",
        "tests/integration/test_cockpit_http_server.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/run_cockpit.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/cockpit/static/app.js",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-3",
      "title": "��Կɨ��ģʽ����չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� ���� `stripe_key`��`sk_live_`/`sk_test_`/`rk_live_`+16+��Stripe ��ʵ/����/������Կ������ ���� `sendgrid_key`��`SG.<22>.<20>`������ ���� `pgp_private_key`��`PGP PRIVATE KEY BLOCK`������ tests/ PEM �������壩���� ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž� secret_scan �����Զ����档",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "AVAIL-2",
      "title": "����̽����Ӧ����У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` `check_cockpit`����`/healthz` �� HTTP 200 ��У����Ӧ�� `service=coevo-cockpit` �� `status=ok`����ֹ�˿ڱ���������ռ��ʱ���н��������ǽ��������ɴ�/�� 200/�������/�����壩ͳһ degraded��������ǰ�� 200 �� critical ���ĵ�����Ĳ�һ�£�`scripts/cockpit-watchdog.ps1` `Test-CockpitHealth` ͬ��У����Ӧ�����ݣ��ĵ���ops-runbook ��1 cockpit �� + ��2.1 �����ж�˵����",
      "code": [
        "scripts/health_check.py",
        "scripts/cockpit-watchdog.ps1",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py",
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-6",
      "title": "������鱸��������У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` ���� `--verify-backups`���������±���ִ�� `backup_state.py verify`�������Թ�ϣУ�飻�ӽ��� 120s ��ʱ fail-closed������ȱʧ/ʧ��/��ʱ �� degraded�����ɹ�ʱ detail �� `integrity=ok`��У��������ʶ� ok ʱִ�У���ѡ���н�ɱ����ջ� OPS-3 ��\"������У�����ֶ�\"�߽磩���ĵ���ops-runbook ��1 backup �� + ʾ����",
      "code": [
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "AVAIL-3",
      "title": "���Ź�����Ԥ�㣨2026-08-04���û�ָ�������������Ż��������� `scripts/restart-budget.ps1`���������� `Test-RestartBudget`���������������� `< MaxRestarts` �����������ɱ����Ź� dot-source��Ҳ�ɶ������й����ԣ�`scripts/cockpit-watchdog.ps1` ���� `-MaxRestarts`��Ĭ�� 5���� `-RestartWindowSeconds`��Ĭ�� 3600��������ǰ�ж�Ԥ�㣬�ľ�ʱ������ѯ��ֹͣ��������ӡ manual intervention required�����ڹ�����ָ������ĵ���ops-runbook ��2.1 ����Ԥ��˵����",
      "code": [
        "scripts/restart-budget.ps1",
        "scripts/cockpit-watchdog.ps1",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/restart-budget.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "CI-2",
      "title": "��������Ʒ�������ϣ���2026-08-04���û�ָ�push �� github ������������� `scripts/ci-build-toolchain.py`�����ɸ��ֹ������߹����� zip��python ��������ʱ+���ļ�/node/gmssl/control����Ϊ `.tools/`���������С�� SHA-256��fail-closed��ȱ��Ŀ/����Ѵ��ھܾ�����`docs/dependencies/ci-artifact.json` ���� version=1.0.0/url=Release ģʽ/sha256=81dd3e7d����80.08 MB��4934 �ļ�������ʵ��Ʒ�� `ci-restore-toolchain.ps1 -LocalPath` �ָ��ɹ����ָ����� python �� fmt/lint �� exit 0��ָ�� e225df61/4e9985cf��CI ����ָ����ά������ͬ��Ԥ�ڣ����ĵ���ci-artifact-hosting.md ״̬/�������known-limitations CI �и��£�ʣ�༤��裺�����ߴ��� `toolchain-1.0.0` Release �ϴ���Ʒ��",
      "code": [
        "scripts/ci-build-toolchain.py",
        "docs/dependencies/ci-artifact.json",
        "docs/operations/ci-artifact-hosting.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/unit/test_ci_restore.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/ci-build-toolchain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/ci-artifact.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ci-artifact-hosting.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ci_restore.py",
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


## 2026-08-04T10:33:19.048557Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text

          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-3",
      "title": "��Կɨ��ģʽ����չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� ���� `stripe_key`��`sk_live_`/`sk_test_`/`rk_live_`+16+��Stripe ��ʵ/����/������Կ������ ���� `sendgrid_key`��`SG.<22>.<20>`������ ���� `pgp_private_key`��`PGP PRIVATE KEY BLOCK`������ tests/ PEM �������壩���� ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž� secret_scan �����Զ����档",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "AVAIL-2",
      "title": "����̽����Ӧ����У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` `check_cockpit`����`/healthz` �� HTTP 200 ��У����Ӧ�� `service=coevo-cockpit` �� `status=ok`����ֹ�˿ڱ���������ռ��ʱ���н��������ǽ��������ɴ�/�� 200/�������/�����壩ͳһ degraded��������ǰ�� 200 �� critical ���ĵ�����Ĳ�һ�£�`scripts/cockpit-watchdog.ps1` `Test-CockpitHealth` ͬ��У����Ӧ�����ݣ��ĵ���ops-runbook ��1 cockpit �� + ��2.1 �����ж�˵����",
      "code": [
        "scripts/health_check.py",
        "scripts/cockpit-watchdog.ps1",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py",
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-6",
      "title": "������鱸��������У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` ���� `--verify-backups`���������±���ִ�� `backup_state.py verify`�������Թ�ϣУ�飻�ӽ��� 120s ��ʱ fail-closed������ȱʧ/ʧ��/��ʱ �� degraded�����ɹ�ʱ detail �� `integrity=ok`��У��������ʶ� ok ʱִ�У���ѡ���н�ɱ����ջ� OPS-3 ��\"������У�����ֶ�\"�߽磩���ĵ���ops-runbook ��1 backup �� + ʾ����",
      "code": [
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "AVAIL-3",
      "title": "���Ź�����Ԥ�㣨2026-08-04���û�ָ�������������Ż��������� `scripts/restart-budget.ps1`���������� `Test-RestartBudget`���������������� `< MaxRestarts` �����������ɱ����Ź� dot-source��Ҳ�ɶ������й����ԣ�`scripts/cockpit-watchdog.ps1` ���� `-MaxRestarts`��Ĭ�� 5���� `-RestartWindowSeconds`��Ĭ�� 3600��������ǰ�ж�Ԥ�㣬�ľ�ʱ������ѯ��ֹͣ��������ӡ manual intervention required�����ڹ�����ָ������ĵ���ops-runbook ��2.1 ����Ԥ��˵����",
      "code": [
        "scripts/restart-budget.ps1",
        "scripts/cockpit-watchdog.ps1",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/restart-budget.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "CI-2",
      "title": "��������Ʒ�������ϣ���2026-08-04���û�ָ�push �� github ������������� `scripts/ci-build-toolchain.py`�����ɸ��ֹ������߹����� zip��python ��������ʱ+���ļ�/node/gmssl/control����Ϊ `.tools/`���������С�� SHA-256��fail-closed��ȱ��Ŀ/����Ѵ��ھܾ�����`docs/dependencies/ci-artifact.json` ���� version=1.0.0/url=Release ģʽ/sha256=81dd3e7d����80.08 MB��4934 �ļ�������ʵ��Ʒ�� `ci-restore-toolchain.ps1 -LocalPath` �ָ��ɹ����ָ����� python �� fmt/lint �� exit 0��ָ�� e225df61/4e9985cf��CI ����ָ����ά������ͬ��Ԥ�ڣ����ĵ���ci-artifact-hosting.md ״̬/�������known-limitations CI �и��£�ʣ�༤��裺�����ߴ��� `toolchain-1.0.0` Release �ϴ���Ʒ��",
      "code": [
        "scripts/ci-build-toolchain.py",
        "docs/dependencies/ci-artifact.json",
        "docs/operations/ci-artifact-hosting.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/unit/test_ci_restore.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/ci-build-toolchain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/ci-artifact.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ci-artifact-hosting.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ci_restore.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "RECORDS-2",
      "title": "BACKLOG ״̬������2026-08-04���û�ָ�������������Ż�����`loop/BACKLOG.yaml` 19 ��������� `ready �� done`���ָ�����״̬����������`ready` ������δ��ʼ��������� STATE/matrix ��ì�ܡ���release_check �� backlog �����\"19 ready item(s) explicitly deferred\"��Ϊ\"all items done\"�������ع���ԣ�BACKLOG �� done �����ǡΪ STATE `current_item`����Դһ���Բ���������",
      "code": [
        "loop/BACKLOG.yaml",
        "tests/unit/test_release_check.py"
      ],
      "tests": [
        "tests/unit/test_release_check.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "loop/BACKLOG.yaml",
          "exists": true
        },
        {
          "kind": "code",
          "path": "tests/unit/test_release_check.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_release_check.py",
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


## 2026-08-04T15:01:46.261263Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 60.991s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 138.748s

OK
audit seal: fully-sealed

```


## 2026-08-04T15:23:25.226532Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 51.197s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 139.627s

OK
audit seal: fully-sealed

```


## 2026-08-04T16:22:30.218132Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 52.398s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 139.523s

OK
audit seal: fully-sealed

```


## 2026-08-04T16:43:53.166046Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 52.589s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 138.704s

OK
audit seal: fully-sealed

```


## 2026-08-04T16:57:41.922724Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 54.718s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 140.328s

OK
audit seal: fully-sealed

```


## 2026-08-04T17:11:08.171762Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 52.718s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 141.614s

OK
audit seal: fully-sealed

```


## 2026-08-04T17:26:36.733130Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 59.841s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 145.860s

OK
audit seal: fully-sealed

```


## 2026-08-04T17:36:20.762986Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 50.904s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 138.515s

OK
audit seal: fully-sealed

```


## 2026-08-04T17:47:40.425019Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 52.541s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 138.790s

OK
audit seal: fully-sealed

```


## 2026-08-04T18:07:52.870736Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 52.480s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 138.819s

OK
audit seal: fully-sealed

```


## 2026-08-05T10:32:32.291318Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
ecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 157.709s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 182.221s

OK
audit seal: fully-sealed

```


## 2026-08-05T10:48:19.287524Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 72.604s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 174.954s

OK
audit seal: fully-sealed

```


## 2026-08-05T11:02:06.108597Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 78.935s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 190.257s

OK
audit seal: fully-sealed

```


## 2026-08-05T11:22:38.838510Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 88.121s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 194.388s

OK
audit seal: fully-sealed

```


## 2026-08-05T11:35:46.847681Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 71.985s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 165.449s

OK
audit seal: fully-sealed

```


## 2026-08-05T11:49:36.127203Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 71.645s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 160.309s

OK
audit seal: fully-sealed

```


## 2026-08-05T12:07:39.052209Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 75.908s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 166.443s

OK
audit seal: fully-sealed

```


## 2026-08-05T16:21:14.295172Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 79.569s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 175.899s

OK
audit seal: fully-sealed

```


## 2026-08-05T16:33:24.943346Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 63.777s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 159.268s

OK
audit seal: fully-sealed

```


## 2026-08-05T16:45:29.805273Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 68.220s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 158.698s

OK
audit seal: fully-sealed

```


## 2026-08-05T16:58:25.789901Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 69.215s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 165.733s

OK
audit seal: fully-sealed

```


## 2026-08-05T17:10:27.640996Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 67.951s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 166.054s

OK
audit seal: fully-sealed

```


## 2026-08-05T17:25:34.363660Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 72.218s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 165.591s

OK
audit seal: fully-sealed

```


## 2026-08-05T17:37:52.676158Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 65.627s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 165.286s

OK
audit seal: fully-sealed

```


## 2026-08-05T17:49:30.460071Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 66.052s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 157.890s

OK
audit seal: fully-sealed

```


## 2026-08-05T18:02:11.218268Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 64.914s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 155.199s

OK
audit seal: fully-sealed

```


## 2026-08-05T18:12:04.276078Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `1`
```text
^^^^^^^^^^
AssertionError: 0 != 1 : helper failed: GMH-E-MAGIC
At E:\Workspace\Coevo\scripts\generate-sm2-test-pki.ps1:106 char:7
+       throw ('helper failed: ' + $diagnostic.Trim())
+       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : OperationStopped: (helper failed: GMH-E-MAGIC:String) [], RuntimeException
    + FullyQualifiedErrorId : helper failed: GMH-E-MAGIC
 


======================================================================
FAIL: test_generation_is_isolated_encrypted_verified_and_non_overwriting (test_sm2_test_pki_generation.Sm2TestPkiTests.test_generation_is_isolated_encrypted_verified_and_non_overwriting)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_sm2_test_pki_generation.py", line 129, in test_generation_is_isolated_encrypted_verified_and_non_overwriting
    self.assertEqual(0, result.returncode, result.stderr)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : helper failed: GMH-E-MAGIC
At E:\Workspace\Coevo\scripts\generate-sm2-test-pki.ps1:106 char:7
+       throw ('helper failed: ' + $diagnostic.Trim())
+       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : OperationStopped: (helper failed: GMH-E-MAGIC:String) [], RuntimeException
    + FullyQualifiedErrorId : helper failed: GMH-E-MAGIC
 


======================================================================
FAIL: test_helper_response_is_fixed_public_frame_and_response_loss_recovers (test_sm2_test_pki_generation.Sm2TestPkiTests.test_helper_response_is_fixed_public_frame_and_response_loss_recovers)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_sm2_test_pki_generation.py", line 433, in test_helper_response_is_fixed_public_frame_and_response_loss_recovers
    self.assertEqual(0, lost.returncode, lost.stderr)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : helper failed: GMH-E-MAGIC
At E:\Workspace\Coevo\scripts\generate-sm2-test-pki.ps1:106 char:7
+       throw ('helper failed: ' + $diagnostic.Trim())
+       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : OperationStopped: (helper failed: GMH-E-MAGIC:String) [], RuntimeException
    + FullyQualifiedErrorId : helper failed: GMH-E-MAGIC
 


======================================================================
FAIL: test_hung_helper_is_tree_killed_and_drains_are_bounded (test_sm2_test_pki_generation.Sm2TestPkiTests.test_hung_helper_is_tree_killed_and_drains_are_bounded)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_sm2_test_pki_generation.py", line 270, in test_hung_helper_is_tree_killed_and_drains_are_bounded
    self.assertIn("helper timed out", result.stderr)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'helper timed out' not found in "helper failed: GMH-E-MAGIC\nAt E:\\Workspace\\Coevo\\scripts\\generate-sm2-test-pki.ps1:106 char:7\n+       throw ('helper failed: ' + $diagnostic.Trim())\n+       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n    + CategoryInfo          : OperationStopped: (helper failed: GMH-E-MAGIC:String) [], RuntimeException\n    + FullyQualifiedErrorId : helper failed: GMH-E-MAGIC\n \n"

======================================================================
FAIL: test_kill_points_are_recovered_with_same_nonce (test_sm2_test_pki_generation.Sm2TestPkiTests.test_kill_points_are_recovered_with_same_nonce) (point='after-rename')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_sm2_test_pki_generation.py", line 476, in test_kill_points_are_recovered_with_same_nonce
    self.assertEqual(0, result.returncode, result.stderr)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : helper failed: GMH-E-MAGIC
At E:\Workspace\Coevo\scripts\generate-sm2-test-pki.ps1:106 char:7
+       throw ('helper failed: ' + $diagnostic.Trim())
+       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : OperationStopped: (helper failed: GMH-E-MAGIC:String) [], RuntimeException
    + FullyQualifiedErrorId : helper failed: GMH-E-MAGIC
 


======================================================================
FAIL: test_launcher_ignores_poisoned_path_and_cleans_ephemeral_helper (test_sm2_test_pki_generation.Sm2TestPkiTests.test_launcher_ignores_poisoned_path_and_cleans_ephemeral_helper)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_sm2_test_pki_generation.py", line 496, in test_launcher_ignores_poisoned_path_and_cleans_ephemeral_helper
    self.assertEqual(0, result.returncode, result.stderr)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : helper failed: GMH-E-MAGIC
At E:\Workspace\Coevo\scripts\generate-sm2-test-pki.ps1:106 char:7
+       throw ('helper failed: ' + $diagnostic.Trim())
+       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : OperationStopped: (helper failed: GMH-E-MAGIC:String) [], RuntimeException
    + FullyQualifiedErrorId : helper failed: GMH-E-MAGIC
 


======================================================================
FAIL: test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper (test_sm2_test_pki_generation.Sm2TestPkiTests.test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_sm2_test_pki_generation.py", line 306, in test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper
    self.assertRegex(result.stderr, r"GMH-E-DIRECTORY-LOCK-[A-Z-]+-WIN32-32-ATTEMPT-4|Unable to lock file|Unable to lock tool directory")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Regex didn't match: 'GMH-E-DIRECTORY-LOCK-[A-Z-]+-WIN32-32-ATTEMPT-4|Unable to lock file|Unable to lock tool directory' not found in "helper failed: GMH-E-MAGIC\nAt E:\\Workspace\\Coevo\\scripts\\generate-sm2-test-pki.ps1:106 char:7\n+       throw ('helper failed: ' + $diagnostic.Trim())\n+       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n    + CategoryInfo          : OperationStopped: (helper failed: GMH-E-MAGIC:String) [], RuntimeException\n    + FullyQualifiedErrorId : helper failed: GMH-E-MAGIC\n \n"

======================================================================
FAIL: test_wide_runtime_acl_is_corrected_before_staging_creation (test_sm2_test_pki_generation.Sm2TestPkiTests.test_wide_runtime_acl_is_corrected_before_staging_creation)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\integration\test_sm2_test_pki_generation.py", line 335, in test_wide_runtime_acl_is_corrected_before_staging_creation
    self.assertEqual(0, result.returncode, result.stderr)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : helper failed: GMH-E-MAGIC
At E:\Workspace\Coevo\scripts\generate-sm2-test-pki.ps1:106 char:7
+       throw ('helper failed: ' + $diagnostic.Trim())
+       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : OperationStopped: (helper failed: GMH-E-MAGIC:String) [], RuntimeException
    + FullyQualifiedErrorId : helper failed: GMH-E-MAGIC
 


----------------------------------------------------------------------
Ran 249 tests in 191.154s

FAILED (failures=15, errors=3)

```


## 2026-08-05T18:29:17.437201Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 66.594s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 158.609s

OK
audit seal: fully-sealed

```


## 2026-08-05T18:41:46.531182Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 67.058s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 164.751s

OK
audit seal: fully-sealed

```


## 2026-08-05T18:54:17.237987Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 68.419s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 158.868s

OK
audit seal: fully-sealed

```


## 2026-08-05T19:07:30.901806Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 65.615s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 160.128s

OK
audit seal: fully-sealed

```


## 2026-08-05T19:20:55.518153Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 68.216s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 156.368s

OK
audit seal: fully-sealed

```


## 2026-08-05T19:34:24.578634Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 68.808s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 162.612s

OK
audit seal: fully-sealed

```


## 2026-08-05T23:40:57.967626Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 66.100s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 152.642s

OK
audit seal: fully-sealed

```


## 2026-08-06T00:15:33.760312Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
SecurityTests.test_stale_baseline_is_rejected_before_insert) ... ok
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
Ran 97 tests in 53.723s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
test_launcher_serves_healthz_and_stops_gracefully (test_cockpit_launcher.CockpitLauncherE2ETest.test_launcher_serves_healthz_and_stops_gracefully) ... C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Python314\Lib\unittest\case.py:615: ResourceWarning: unclosed file <_io.TextIOWrapper name=3 encoding='cp936'>
  result = method()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok
test_preflight_exits_zero_on_healthy_repo (test_cockpit_launcher.CockpitLauncherE2ETest.test_preflight_exits_zero_on_healthy_repo) ... ok
test_print_token_issues_usable_session (test_cockpit_launcher.CockpitLauncherE2ETest.test_print_token_issues_usable_session) ... ok
test_api_endpoints_drive_the_ui (test_cockpit_offline_frontend.OfflineFrontendTests.test_api_endpoints_drive_the_ui) ... ok
test_index_serves_local_page_with_csp (test_cockpit_offline_frontend.OfflineFrontendTests.test_index_serves_local_page_with_csp) ... ok
test_local_assets_load_and_have_no_external_urls (test_cockpit_offline_frontend.OfflineFrontendTests.test_local_assets_load_and_have_no_external_urls) ... ok
test_unknown_asset_is_not_served (test_cockpit_offline_frontend.OfflineFrontendTests.test_unknown_asset_is_not_served) ... C:\Python314\Lib\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'Not Found'>
  _warnings.warn(self.warn_message, ResourceWarning)
ok
test_cli_smoke_run_exits_zero (test_demo_runner.DemoRunnerTests.test_cli_smoke_run_exits_zero) ... ok
test_pipeline_completes_with_real_package_and_persistence (test_demo_runner.DemoRunnerTests.test_pipeline_completes_with_real_package_and_persistence) ... ok
test_pipeline_with_cockpit_server_serves_and_stops (test_demo_runner.DemoRunnerTests.test_pipeline_with_cockpit_server_serves_and_stops) ... ok
test_windows_certificate_parser_and_generation_markers_work_end_to_end (test_identity_dev_environment.IdentityDevelopmentEnvironmentTests.test_windows_certificate_parser_and_generation_markers_work_end_to_end) ... ok
test_strict_environment_validator_passes (test_loop_environment.LoopEnvironmentE2ETest.test_strict_environment_validator_passes) ... ok
test_validator_runs_with_standard_library_only (test_offline_baseline.OfflineBaselineTests.test_validator_runs_with_standard_library_only) ... ok
test_real_encrypted_report_drives_merge_risk_brief_knowledge (test_return_chain.ReturnChainE2ETest.test_real_encrypted_report_drives_merge_risk_brief_knowledge) ... ok

----------------------------------------------------------------------
Ran 14 tests in 151.126s

OK
audit seal: fully-sealed

```


## 2026-08-06T13:48:37.769307Z — target=`quality` fingerprint=`759566939f0be77b`
- exit_code: `1`
```text
/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "SECSCAN-3",
      "title": "��Կɨ��ģʽ����չ��2026-08-04���û�ָ�������������Ż�����`scripts/secret_scan.py` �� ���� `stripe_key`��`sk_live_`/`sk_test_`/`rk_live_`+16+��Stripe ��ʵ/����/������Կ������ ���� `sendgrid_key`��`SG.<22>.<20>`������ ���� `pgp_private_key`��`PGP PRIVATE KEY BLOCK`������ tests/ PEM �������壩���� ȫ�������Ÿ�ʽ��������ȫ·�����أ��� tests/����lint �Ž� secret_scan �����Զ����档",
      "code": [
        "scripts/secret_scan.py"
      ],
      "tests": [
        "tests/unit/test_secret_scan.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "AVAIL-2",
      "title": "����̽����Ӧ����У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` `check_cockpit`����`/healthz` �� HTTP 200 ��У����Ӧ�� `service=coevo-cockpit` �� `status=ok`����ֹ�˿ڱ���������ռ��ʱ���н��������ǽ��������ɴ�/�� 200/�������/�����壩ͳһ degraded��������ǰ�� 200 �� critical ���ĵ�����Ĳ�һ�£�`scripts/cockpit-watchdog.ps1` `Test-CockpitHealth` ͬ��У����Ӧ�����ݣ��ĵ���ops-runbook ��1 cockpit �� + ��2.1 �����ж�˵����",
      "code": [
        "scripts/health_check.py",
        "scripts/cockpit-watchdog.ps1",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py",
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPS-6",
      "title": "������鱸��������У�飨2026-08-04���û�ָ�������������Ż�����`scripts/health_check.py` ���� `--verify-backups`���������±���ִ�� `backup_state.py verify`�������Թ�ϣУ�飻�ӽ��� 120s ��ʱ fail-closed������ȱʧ/ʧ��/��ʱ �� degraded�����ɹ�ʱ detail �� `integrity=ok`��У��������ʶ� ok ʱִ�У���ѡ���н�ɱ����ջ� OPS-3 ��\"������У�����ֶ�\"�߽磩���ĵ���ops-runbook ��1 backup �� + ʾ����",
      "code": [
        "scripts/health_check.py",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "AVAIL-3",
      "title": "���Ź�����Ԥ�㣨2026-08-04���û�ָ�������������Ż��������� `scripts/restart-budget.ps1`���������� `Test-RestartBudget`���������������� `< MaxRestarts` �����������ɱ����Ź� dot-source��Ҳ�ɶ������й����ԣ�`scripts/cockpit-watchdog.ps1` ���� `-MaxRestarts`��Ĭ�� 5���� `-RestartWindowSeconds`��Ĭ�� 3600��������ǰ�ж�Ԥ�㣬�ľ�ʱ������ѯ��ֹͣ��������ӡ manual intervention required�����ڹ�����ָ������ĵ���ops-runbook ��2.1 ����Ԥ��˵����",
      "code": [
        "scripts/restart-budget.ps1",
        "scripts/cockpit-watchdog.ps1",
        "docs/operations/ops-runbook.md"
      ],
      "tests": [
        "tests/unit/test_preflight_watchdog.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/restart-budget.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/cockpit-watchdog.ps1",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ops-runbook.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_preflight_watchdog.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "CI-2",
      "title": "��������Ʒ�������ϣ���2026-08-04���û�ָ�push �� github ������������� `scripts/ci-build-toolchain.py`�����ɸ��ֹ������߹����� zip��python ��������ʱ+���ļ�/node/gmssl/control����Ϊ `.tools/`���������С�� SHA-256��fail-closed��ȱ��Ŀ/����Ѵ��ھܾ�����`docs/dependencies/ci-artifact.json` ���� version=1.0.0/url=Release ģʽ/sha256=81dd3e7d����80.08 MB��4934 �ļ�������ʵ��Ʒ�� `ci-restore-toolchain.ps1 -LocalPath` �ָ��ɹ����ָ����� python �� fmt/lint �� exit 0��ָ�� e225df61/4e9985cf��CI ����ָ����ά������ͬ��Ԥ�ڣ����ĵ���ci-artifact-hosting.md ״̬/�������known-limitations CI �и��£�ʣ�༤��裺�����ߴ��� `toolchain-1.0.0` Release �ϴ���Ʒ��",
      "code": [
        "scripts/ci-build-toolchain.py",
        "docs/dependencies/ci-artifact.json",
        "docs/operations/ci-artifact-hosting.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/unit/test_ci_restore.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/ci-build-toolchain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/ci-artifact.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ci-artifact-hosting.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ci_restore.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "RECORDS-2",
      "title": "BACKLOG ״̬������2026-08-04���û�ָ�������������Ż�����`loop/BACKLOG.yaml` 19 ��������� `ready �� done`���ָ�����״̬����������`ready` ������δ��ʼ��������� STATE/matrix ��ì�ܡ���release_check �� backlog �����\"19 ready item(s) explicitly deferred\"��Ϊ\"all items done\"�������ع���ԣ�BACKLOG �� done �����ǡΪ STATE `current_item`����Դһ���Բ���������",
      "code": [
        "loop/BACKLOG.yaml",
        "tests/unit/test_release_check.py"
      ],
      "tests": [
        "tests/unit/test_release_check.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "loop/BACKLOG.yaml",
          "exists": true
        },
        {
          "kind": "code",
          "path": "tests/unit/test_release_check.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_release_check.py",
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
SECRET pgp_private_key: loop/VERIFICATION.md:1795 (-----BEGIN PGP PRIVATE KEY BLOCK-----)

```

## 2026-08-06T14:20:44.695739Z — target=`fmt` fingerprint=`8d456a2ce09245c7`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ C:\Python314\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```

## 2026-08-06T14:36:30.963647Z — target=`quality` fingerprint=`759566939f0be77b`
- exit_code: `0`
```text
Tests.test_promote_failure_requires_recovery_and_reopen_commits_exactly_once) ... ok
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
Ran 97 tests in 57.113s

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
Ran 14 tests in 153.278s

OK
audit seal: fully-sealed

```

## 2026-08-06T15:54:39.426799Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `10`
```text
����������� `scripts/ci-build-toolchain.py`�����ɸ��ֹ������߹����� zip��python ��������ʱ+���ļ�/node/gmssl/control����Ϊ `.tools/`���������С�� SHA-256��fail-closed��ȱ��Ŀ/����Ѵ��ھܾ�����`docs/dependencies/ci-artifact.json` ���� version=1.0.0/url=Release ģʽ/sha256=81dd3e7d����80.08 MB��4934 �ļ�������ʵ��Ʒ�� `ci-restore-toolchain.ps1 -LocalPath` �ָ��ɹ����ָ����� python �� fmt/lint �� exit 0��ָ�� e225df61/4e9985cf��CI ����ָ����ά������ͬ��Ԥ�ڣ����ĵ���ci-artifact-hosting.md ״̬/�������known-limitations CI �и��£�ʣ�༤��裺�����ߴ��� `toolchain-1.0.0` Release �ϴ���Ʒ��",
      "code": [
        "scripts/ci-build-toolchain.py",
        "docs/dependencies/ci-artifact.json",
        "docs/operations/ci-artifact-hosting.md",
        "docs/operations/known-limitations.md"
      ],
      "tests": [
        "tests/unit/test_ci_restore.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/ci-build-toolchain.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/ci-artifact.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/ci-artifact-hosting.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ci_restore.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "RECORDS-2",
      "title": "BACKLOG ״̬������2026-08-04���û�ָ�������������Ż�����`loop/BACKLOG.yaml` 19 ��������� `ready �� done`���ָ�����״̬����������`ready` ������δ��ʼ��������� STATE/matrix ��ì�ܡ���release_check �� backlog �����\"19 ready item(s) explicitly deferred\"��Ϊ\"all items done\"�������ع���ԣ�BACKLOG �� done �����ǡΪ STATE `current_item`����Դһ���Բ���������",
      "code": [
        "loop/BACKLOG.yaml",
        "tests/unit/test_release_check.py"
      ],
      "tests": [
        "tests/unit/test_release_check.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "loop/BACKLOG.yaml",
          "exists": true
        },
        {
          "kind": "code",
          "path": "tests/unit/test_release_check.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_release_check.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "REVIEW-FIX-3",
      "title": "������������޸���2026-08-06���û�ָ���������������޸����Ż������� H-1 ��ʵ��������`SingleInstanceLock` ����ˢ�£�Ĭ�� 60s `os.utime`��+ `_recover_stale` ˫�ж���mtime �����Ҽ�¼ pid ���ٴ��Žӹܣ���Windows ���̽�� `OpenProcess`+`GetExitCodeProcess(STILL_ACTIVE)` ����ʽ���� 64 λ HANDLE restype�������߳��� start/stop ��ͣ���� M-1 e2e ResourceWarning����launcher �ر��ӽ��� stdout/stderr��offline_frontend/integration �� HTTPError `finally close`��e2e ��־ ResourceWarning=0���� M-2 �����Ž����⡪��`quality_gate.py` �� `exclusive_lock(GATE_LOCK)`��`loop/.quality-gate.lock`��gitignored�����л���main ���� RuntimeError ��� exit_code=15���ĵ�ע���Ž����봮�У��� L-2 `_serve_static` ���� text/* ׷�� charset���� L-3 ��ʻ����Ӧͷ����`_send_bytes` �ֵ�Ĭ��ͷ��nosniff/no-store/no-referrer����̬�ɸ��� Cache-Control Ϊ public max-age=300����index/API �������Ҳ�й¶ referrer������/e2e ���ԣ��� L-4 �鵵��ֵ�µ���verification keep_recent 60��30��size 1M��500K��+ �����ĵ�ͬ�� + ���Թ̶����� secret_scan �� `loop/` ��¼�ļ����� pem/pgp/key_assignment �о�ģʽ����������ȫ·�����أ�+ ���⣻����ͬ����quality_gate.py ��ϣ / python-script-lock.tsv / toolchain-lock script_inventory+source_sha256 / make.cs ScriptInventorySha256����",
      "code": [
        "src/coevo/cockpit/server.py",
        "scripts/quality_gate.py",
        "scripts/secret_scan.py",
        "scripts/archive_records.py",
        "scripts/tool-shims/make.cs",
        "docs/dependencies/python-script-lock.tsv",
        "docs/dependencies/toolchain-lock.json",
        "docs/process/records-archiving-policy.md"
      ],
      "tests": [
        "tests/unit/test_cockpit_http.py",
        "tests/unit/test_quality_gate_lock.py",
        "tests/unit/test_secret_scan.py",
        "tests/unit/test_records_archive.py",
        "tests/integration/test_cockpit_http_server.py",
        "tests/e2e/test_cockpit_launcher.py",
        "test_cockpit_offline_frontend.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/archive_records.py",
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
          "path": "docs/process/records-archiving-policy.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_cockpit_http.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_lock.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_records_archive.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "test_cockpit_offline_frontend.py",
          "exists": false
        }
      ],
      "kind": "missing"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-1",
      "title": "���ļ���������ģ���ĵ�ϸ����2026-08-06���û�ָ����� ȫ�־�̬ɨ�裨AST���﷨/�ɱ�Ĭ�ϲ���/�� except/eval/TODO��+ ���ļ������߲飨���ݽṹ/�㷨/�ܹ����������﷨�����޿ɱ�Ĭ�ϲ��������� except���� ���� 14 �������루`report/builder.py`��`audit_governance/models.py`��`config.py`��`knowledge_base/store.py`��`talent/*`��`task_decomposition/*`��`task_flow/*`��`workspace/init_service.py`��`benchmarks/__init__.py`������ �޸� `health_check.check_audit` ����ì�ܡ������� `verify --allow-tail`�����β��δ�ܷ� = degraded��ԭʵ������ status ��Ϊ critical�����ĵ����������� 4 ��⣨fully-sealed ok / δ�ܷ�β�� degraded / ��ʵʧ�� critical / ��ʱ critical������ `docs/modules/` 22 ��ģ�� README ��ͳһģ��ϸ������λ/ְ��߽�/�ļ���ؼ�����/������/��ȫ������/���Ը���/���������Σ���",
      "code": [
        "scripts/health_check.py",
        "src/coevo",
        "docs/modules/*.md"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/*.md",
          "exists": false
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "missing"
    }
  ]
}

```

## 2026-08-06T15:56:50.702907Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `1`
```text
sts.test_us_1_ac_1_is_done_with_evidence) ... ok
test_us_1_ac_2_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_1_ac_2_matrix_lists_src_and_test) ... ok
test_us_2_ac_1_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_2_ac_1_is_done_with_evidence) ... ok
test_us_2_ac_1_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_2_ac_1_matrix_lists_src_and_test) ... ok
test_us_3_ac_1_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_3_ac_1_is_done_with_evidence) ... ok
test_us_3_ac_1_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_3_ac_1_matrix_lists_src_and_test) ... ok
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
test_sanitize_id_accepts_safe (test_workspace_init.TestWorkspacePath.test_sanitize_id_accepts_safe) ... ok
test_sanitize_id_rejects_empty (test_workspace_init.TestWorkspacePath.test_sanitize_id_rejects_empty) ... ok
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
FAIL: test_eng_base_is_fully_covered (test_traceability_check.TraceabilityTests.test_eng_base_is_fully_covered)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\unit\test_traceability_check.py", line 12, in test_eng_base_is_fully_covered
    self.assertEqual(40,result["checked"])
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 40 != 42

----------------------------------------------------------------------
Ran 933 tests in 62.701s

FAILED (failures=1, skipped=3)

```

## 2026-08-06T16:06:33.719879Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
ailure_requires_recovery_and_reopen_commits_exactly_once) ... ok
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
Ran 97 tests in 51.266s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
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
Ran 14 tests in 151.588s

OK
audit seal: fully-sealed

```

## 2026-08-06T16:35:54.435622Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `1`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m compileall -q -f scripts src tests
$ E:\Workspace\Coevo\.venv\Scripts\python.exe E:\Workspace\Coevo\scripts\validate_opencode.py
PASS required: AGENTS.md
PASS required: opencode.jsonc
PASS required: Makefile
PASS required: docs/README.md
PASS required: loop/STATE.json
PASS required: loop/BACKLOG.yaml
PASS required: loop/VERIFICATION.md
PASS required: loop/tool-audit.jsonl
PASS required: .opencode/plugins/loop-guard.ts
PASS required: .opencode/tools/loop_state.ts
PASS required: .opencode/tools/quality_gate.ts
PASS required: .opencode/tools/traceability_check.ts
PASS required: tests/unit
PASS required: tests/integration
PASS required: tests/security
PASS required: tests/e2e
PASS denied: webfetch
PASS denied: websearch
PASS denied: external_directory
PASS bash defaults to ask
PASS bash denied: git push*
PASS bash denied: curl *
PASS bash denied: wget *
PASS bash denied: pip install*
PASS bash denied: npm install*
PASS current tool API: loop_state.ts
PASS current tool API: quality_gate.ts
PASS current tool API: traceability_check.ts
{"ok": true, "failures": []}
$ E:\Workspace\Coevo\.venv\Scripts\python.exe E:\Workspace\Coevo\.tools\control\control.pyz traceability_check
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "E:\Workspace\Coevo\.tools\control\control.pyz\__main__.py", line 18, in <module>
    runpy.run_module(name, run_name="__main__", alter_sys=True)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen runpy>", line 226, in run_module
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "E:\Workspace\Coevo\.tools\control\control.pyz\traceability_check.py", line 40, in <module>
    if __name__=="__main__": raise SystemExit(main())
                                              ~~~~^^
  File "E:\Workspace\Coevo\.tools\control\control.pyz\traceability_check.py", line 39, in main
    summary=check(args.story,not args.all_statuses); print(json.dumps(summary,ensure_ascii=False,indent=2)); return 0 if summary["checked"] and not summary["missing"] else 10
                                                     ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'gbk' codec can't encode character '\u21c4' in position 148475: illegal multibyte sequence

```

## 2026-08-06T16:46:25.824233Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
ailure_requires_recovery_and_reopen_commits_exactly_once) ... ok
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
Ran 97 tests in 50.095s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
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
Ran 14 tests in 151.315s

OK
audit seal: fully-sealed

```

## 2026-08-06T17:09:38.962780Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
ailure_requires_recovery_and_reopen_commits_exactly_once) ... ok
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
Ran 97 tests in 58.508s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
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
Ran 14 tests in 184.289s

OK
audit seal: fully-sealed

```

## 2026-08-06T17:37:35.125298Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
ailure_requires_recovery_and_reopen_commits_exactly_once) ... ok
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
Ran 97 tests in 58.408s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
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
Ran 14 tests in 170.443s

OK
audit seal: fully-sealed

```

## 2026-08-06T18:05:10.274755Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
ailure_requires_recovery_and_reopen_commits_exactly_once) ... ok
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
Ran 97 tests in 67.441s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
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
Ran 14 tests in 182.904s

OK
audit seal: fully-sealed

```

## 2026-08-06T18:28:18.323450Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
ailure_requires_recovery_and_reopen_commits_exactly_once) ... ok
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
Ran 97 tests in 65.079s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
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
Ran 14 tests in 165.916s

OK
audit seal: fully-sealed

```

## 2026-08-06T18:52:36.842205Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
ailure_requires_recovery_and_reopen_commits_exactly_once) ... ok
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
Ran 97 tests in 65.329s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
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
Ran 14 tests in 162.252s

OK
audit seal: fully-sealed

```

## 2026-08-06T19:15:09.832426Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
ailure_requires_recovery_and_reopen_commits_exactly_once) ... ok
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
Ran 97 tests in 63.364s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
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
Ran 14 tests in 152.908s

OK
audit seal: fully-sealed

```

## 2026-08-06T19:38:11.195584Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
ailure_requires_recovery_and_reopen_commits_exactly_once) ... ok
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
Ran 97 tests in 70.969s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
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
Ran 14 tests in 166.635s

OK
audit seal: fully-sealed

```

## 2026-08-06T19:42:28.477410Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `1`
```text
rc_and_test (test_traceability_check.TraceabilityTests.test_us_5_ac_1_matrix_lists_src_and_test) ... ok
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
FAIL: test_probe_completes_with_zero_errors (test_benchmark_http.CockpitHttpProbeTests.test_probe_completes_with_zero_errors)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\unit\test_benchmark_http.py", line 25, in test_probe_completes_with_zero_errors
    self.assertTrue(result.ok, result.detail)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true : p50=0.0091s max=1.1117s errors=0

======================================================================
FAIL: test_eng_base_is_fully_covered (test_traceability_check.TraceabilityTests.test_eng_base_is_fully_covered)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\unit\test_traceability_check.py", line 12, in test_eng_base_is_fully_covered
    self.assertEqual(42,result["checked"])
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 42 != 43

----------------------------------------------------------------------
Ran 938 tests in 68.612s

FAILED (failures=2, skipped=3)

```

## 2026-08-06T19:53:02.604955Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
ailure_requires_recovery_and_reopen_commits_exactly_once) ... ok
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
Ran 97 tests in 66.147s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
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
Ran 14 tests in 166.205s

OK
audit seal: fully-sealed

```

## 2026-08-06T20:17:58.381339Z — target=`quality` fingerprint=`5c884c0872eb4b9a`
- exit_code: `0`
```text
ailure_requires_recovery_and_reopen_commits_exactly_once) ... ok
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
Ran 97 tests in 66.389s

OK
$ E:\Workspace\Coevo\.tools\node\24.14.0\node.exe tests/security/path_policy_test.mjs
$ E:\Workspace\Coevo\.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
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
Ran 14 tests in 161.501s

OK
audit seal: fully-sealed

```
## 2026-08-07T04:19:58.587Z — OPTIMIZE-12（用户指令：不用做全量质量门）
- 本轮仅定向验证：python -m unittest tests.unit.test_split_packages 5 项全绿。
- 按用户指示豁免全量质量门；下次全量门禁时回归。
- 改动：	ests/unit/test_split_packages.py（新，5 项）、examples/tool-dev-project/README.md（维护说明）。
## 2026-08-07T04:23:52.084Z — OPTIMIZE-13（用户指令：不用做全量质量门）
- 本轮仅定向验证：python -m unittest tests.unit.test_task_flow_models tests.unit.test_supervision_meeting tests.unit.test_knowledge_base 59 项全绿（含 3 项新增边界测试）。
- 按用户指示豁免全量质量门；下次全量门禁时回归。
- 改动：	ests/unit/test_task_flow_models.py、	ests/unit/test_supervision_meeting.py、	ests/unit/test_knowledge_base.py（各 +1 边界测试）。
## 2026-08-07T04:26:42.183Z — OPTIMIZE-14（用户指令：不做全量质量门）
- 本轮仅定向验证：E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m unittest tests.unit.test_run_validation 4 项全绿。
- 按用户指示豁免全量质量门；下次全量门禁时回归。
- 改动：	ests/unit/test_run_validation.py（新，4 项：JSONC 剥离/字符串斜杠保留/指标采集/文本渲染）。
## 2026-08-07T04:28:43.808Z — OPTIMIZE-15（用户指令：不做全量质量门）
- 本轮仅定向验证：python -m unittest tests.unit.test_control_main 4 项全绿。
- 按用户指示豁免全量质量门；下次全量门禁时回归。
- 改动：	ests/unit/test_control_main.py（新，4 项：缺参/未知模块退出、runpy 分派、模块清单）。
## 2026-08-07T04:30:49.282Z — OPTIMIZE-16（用户指令：不做全量质量门）
- 本轮仅定向验证：python -m unittest tests.unit.test_module_docs 4 项全绿。
- 按用户指示豁免全量质量门；下次全量门禁时回归。
- 改动：	ests/unit/test_module_docs.py（新，4 项文档治理守卫）。
## 2026-08-07T04:32:49.035Z — OPTIMIZE-17（用户指令：不做全量质量门）
- 本轮仅定向验证：python -m unittest tests.security.test_force_remove_safety 2 项全绿。
- 按用户指示豁免全量质量门；下次全量门禁时回归。
- 改动：	ests/security/test_force_remove_safety.py（新，2 项破坏性脚本静态安全守卫）。

## 2026-08-07T04:55:25.634242Z — target=`lint` fingerprint=`4800c1ade060c9f3`
- exit_code: `0`
```text
": true
        },
        {
          "kind": "code",
          "path": "docs/operations/known-limitations.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ci_restore.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "RECORDS-2",
      "title": "BACKLOG 状态补正（2026-08-04，用户指令：继续生产落地优化）：`loop/BACKLOG.yaml` 19 个已完成项 `ready → done`（恢复早期状态补正惯例，`ready` 仅用于未开始项），消除与 STATE/matrix 的矛盾——release_check 的 backlog 检查由\"19 ready item(s) explicitly deferred\"变为\"all items done\"；新增回归测试：BACKLOG 非 done 项必须恰为 STATE `current_item`（三源一致性不变量）。",
      "code": [
        "loop/BACKLOG.yaml",
        "tests/unit/test_release_check.py"
      ],
      "tests": [
        "tests/unit/test_release_check.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "loop/BACKLOG.yaml",
          "exists": true
        },
        {
          "kind": "code",
          "path": "tests/unit/test_release_check.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_release_check.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "REVIEW-FIX-3",
      "title": "整体审查问题修复（2026-08-06，用户指令：进行所有问题的修复与优化）：① H-1 单实例锁——`SingleInstanceLock` 心跳刷新（默认 60s `os.utime`）+ `_recover_stale` 双判定（mtime 过期且记录 pid 不再存活才接管），Windows 存活探测 `OpenProcess`+`GetExitCodeProcess(STILL_ACTIVE)` 且显式声明 64 位 HANDLE restype，心跳线程随 start/stop 启停；② M-1 e2e ResourceWarning——launcher 关闭子进程 stdout/stderr、offline_frontend/integration 的 HTTPError `finally close`，e2e 日志 ResourceWarning=0；③ M-2 质量门禁互斥——`quality_gate.py` 用 `exclusive_lock(GATE_LOCK)`（`loop/.quality-gate.lock`，gitignored）串行化，main 捕获 RuntimeError 输出 exit_code=15，文档注明门禁必须串行；④ L-2 `_serve_static` 仅对 text/* 追加 charset；⑤ L-3 驾驶舱响应头——`_send_bytes` 字典默认头（nosniff/no-store/no-referrer，静态可覆盖 Cache-Control 为 public max-age=300），index/API 不缓存且不泄露 referrer，集成/e2e 断言；⑥ L-4 归档阈值下调（verification keep_recent 60→30、size 1M→500K）+ 策略文档同步 + 测试固定；⑦ secret_scan 对 `loop/` 记录文件豁免 pem/pgp/key_assignment 夹具模式（令牌类仍全路径拦截）+ 单测；锁链同步（quality_gate.py 哈希 / python-script-lock.tsv / toolchain-lock script_inventory+source_sha256 / make.cs ScriptInventorySha256）。",
      "code": [
        "src/coevo/cockpit/server.py",
        "scripts/quality_gate.py",
        "scripts/secret_scan.py",
        "scripts/archive_records.py",
        "scripts/tool-shims/make.cs",
        "docs/dependencies/python-script-lock.tsv",
        "docs/dependencies/toolchain-lock.json",
        "docs/process/records-archiving-policy.md"
      ],
      "tests": [
        "tests/unit/test_cockpit_http.py",
        "tests/unit/test_quality_gate_lock.py",
        "tests/unit/test_secret_scan.py",
        "tests/unit/test_records_archive.py",
        "tests/integration/test_cockpit_http_server.py",
        "tests/e2e/test_cockpit_launcher.py",
        "tests/e2e/test_cockpit_offline_frontend.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/archive_records.py",
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
          "path": "docs/process/records-archiving-policy.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_cockpit_http.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_lock.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_records_archive.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_offline_frontend.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-1",
      "title": "逐文件深度审查与模块文档细化（2026-08-06，用户指令）：① 全仓静态扫描（AST：语法/可变默认参数/裸 except/eval/TODO）+ 逐文件代码走查（数据结构/算法/架构）——无语法错误、无可变默认参数、无裸 except；② 清理 14 处死导入（`report/builder.py`、`audit_governance/models.py`、`config.py`、`knowledge_base/store.py`、`talent/*`、`task_decomposition/*`、`task_flow/*`、`workspace/init_service.py`、`benchmarks/__init__.py`）；③ 修复 `health_check.check_audit` 语义矛盾——改用 `verify --allow-tail`，审计尾部未密封 = degraded（原实现因无 status 判为 critical，与文档不符），补 4 项单测（fully-sealed ok / 未密封尾部 degraded / 真实失败 critical / 超时 critical）；④ `docs/modules/` 22 份模块 README 按统一模板细化（定位/职责边界/文件与关键类型/数据流/安全不变量/测试覆盖/依赖与下游）。",
      "code": [
        "scripts/health_check.py",
        "src/coevo",
        "docs/modules/"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-10",
      "title": "第十轮逐文件深度审查与文档细化（2026-08-07，用户指令，延续 OPTIMIZE-9）：① 依赖图环检测边界探针——自环拒绝、双节点环、三节点环（a→b→c→a）、拓扑确定性、未知任务 ID 拒绝均已有测试，覆盖完备无需补；② 补完剩余 16 个模块英文全量文档（app/benchmarks/cockpit/decision_brief/knowledge_base/model/orchestrator/progress_capture/report/risk/root_modules/supervision/talent/task_decomposition/task_flow/workspace 的 .en.md），至此 21/21 模块中英文文档全覆盖，README.en.md 链接齐全。",
      "code": [
        "docs/modules/",
        "docs/modules/README.en.md"
      ],
      "tests": [
        "tests/unit/test_task_decomposition.py",
        "tests/unit/test_optimizations.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/README.en.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_task_decomposition.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_optimizations.py",
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

## 2026-08-07T05:23:28.318720Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```

## 2026-08-07T05:27:40.722676Z — target=`quality` fingerprint=`34d637f035600903`
- exit_code: `1`
```text
d_test (test_traceability_check.TraceabilityTests.test_us_2_ac_1_matrix_lists_src_and_test) ... ok
test_us_3_ac_1_is_done_with_evidence (test_traceability_check.TraceabilityTests.test_us_3_ac_1_is_done_with_evidence) ... ok
test_us_3_ac_1_matrix_lists_src_and_test (test_traceability_check.TraceabilityTests.test_us_3_ac_1_matrix_lists_src_and_test) ... ok
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
FAIL: test_probe_completes_with_zero_errors (test_benchmark_http.CockpitHttpProbeTests.test_probe_completes_with_zero_errors)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\unit\test_benchmark_http.py", line 25, in test_probe_completes_with_zero_errors
    self.assertTrue(result.ok, result.detail)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true : p50=0.0120s max=1.3297s errors=0

----------------------------------------------------------------------
Ran 964 tests in 95.092s

FAILED (failures=1, skipped=3)

```

## 2026-08-07T05:43:03.122512Z — target=`quality` fingerprint=`34d637f035600903`
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
Ran 99 tests in 127.970s

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
Ran 14 tests in 214.314s

OK
audit seal: fully-sealed

```

## 2026-08-07T05:58:16.264988Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```

## 2026-08-07T05:58:30.452042Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text

        },
        {
          "kind": "test",
          "path": "tests/unit/test_cockpit_http.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_lock.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_records_archive.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_offline_frontend.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-1",
      "title": "���ļ���������ģ���ĵ�ϸ����2026-08-06���û�ָ����� ȫ�־�̬ɨ�裨AST���﷨/�ɱ�Ĭ�ϲ���/�� except/eval/TODO��+ ���ļ������߲飨���ݽṹ/�㷨/�ܹ����������﷨�����޿ɱ�Ĭ�ϲ��������� except���� ���� 14 �������루`report/builder.py`��`audit_governance/models.py`��`config.py`��`knowledge_base/store.py`��`talent/*`��`task_decomposition/*`��`task_flow/*`��`workspace/init_service.py`��`benchmarks/__init__.py`������ �޸� `health_check.check_audit` ����ì�ܡ������� `verify --allow-tail`�����β��δ�ܷ� = degraded��ԭʵ������ status ��Ϊ critical�����ĵ����������� 4 ��⣨fully-sealed ok / δ�ܷ�β�� degraded / ��ʵʧ�� critical / ��ʱ critical������ `docs/modules/` 22 ��ģ�� README ��ͳһģ��ϸ������λ/ְ��߽�/�ļ���ؼ�����/������/��ȫ������/���Ը���/���������Σ���",
      "code": [
        "scripts/health_check.py",
        "src/coevo",
        "docs/modules/"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-10",
      "title": "��ʮ�����ļ����������ĵ�ϸ����2026-08-07���û�ָ����� OPTIMIZE-9������ ����ͼ�����߽�̽�롪���Ի��ܾ���˫�ڵ㻷�����ڵ㻷��a��b��c��a��������ȷ���ԡ�δ֪���� ID �ܾ������в��ԣ������걸���貹���� ����ʣ�� 16 ��ģ��Ӣ��ȫ���ĵ���app/benchmarks/cockpit/decision_brief/knowledge_base/model/orchestrator/progress_capture/report/risk/root_modules/supervision/talent/task_decomposition/task_flow/workspace �� .en.md�������� 21/21 ģ����Ӣ���ĵ�ȫ���ǣ�README.en.md ������ȫ��",
      "code": [
        "docs/modules/",
        "docs/modules/README.en.md"
      ],
      "tests": [
        "tests/unit/test_task_decomposition.py",
        "tests/unit/test_optimizations.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/README.en.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_task_decomposition.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_optimizations.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "GO-MIGRATE",
      "ac": "GO-ENV-1",
      "title": "Go �����������뻷������������Դ `D:\\Go` go1.18.8��toolchain-lock �Ǽ� + ����֤�ļ���+ �׸�Ǩ����Ƭ��`task_flow` ��ģ����׶�ӳ�� Go ��ֲ��SourceKind / StandardStage / Traced / SourceMapping / ProcessFlow / WithOverrides / ApplyMapping / 27 ��Ĭ��ӳ�������Ϊ�� Python ���룩+ `go test ./...` ���������Ž���`GOPROXY=off` ǿ�����ߡ�stdlib-only��",
      "code": [
        "docs/dependencies/toolchain-lock.json",
        "docs/dependencies/licenses/go-BSD-3-Clause.txt",
        "go/go.mod",
        "go/taskflow/doc.go",
        "go/taskflow/models.go",
        "go/taskflow/mapping.go",
        "scripts/quality_gate.py",
        "scripts/tool-shims/make.cs",
        "docs/dependencies/python-script-lock.tsv"
      ],
      "tests": [
        "go/taskflow/models_test.go",
        "go/taskflow/mapping_test.go"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/licenses/go-BSD-3-Clause.txt",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/go.mod",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/models.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/mapping.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
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
          "kind": "test",
          "path": "go/taskflow/models_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/mapping_test.go",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "GO-MIGRATE",
      "ac": "GO-PARSER-1",
      "title": "�ڶ�Ǩ����Ƭ��`task_flow` ȷ���Խ������� service ���� Go ��ֲ����Ϊ�� Python �ο�ʵ�ֶ��룩����parser.go ֧�� canonical/tabular/tree �� schema��tabular/tree ��Լ�� canonical����fail-closed��δ֪ format���ظ� stage/node/role id��ȱ unit_id/������/��������Ƿ� id��ȱʡ�б��ֶΡ����ַ��� stage_hint��tree �ṹ�𻵡�tabular δ֪�У���created_at �ÿ�ע��ʱ�ӣ�Ĭ�� UTC ISO-8601 Z���� informational����service.go ʵ�� FlowUnderstandingService��Understand/Confirm/ToAuditRecord����StageGraph���׶�˳��/��Ա/�ڵ���׶�/��׼�׶� O(1) ��������ReviewerView��source-mapping �����ŶȲ�ѯ����TaskFlowValidationError������ ProcessFlowError ����Լ��",
      "code": [
        "go/taskflow/parser.go",
        "go/taskflow/service.go",
        "go/taskflow/doc.go"
      ],
      "tests": [
        "go/taskflow/parser_test.go",
        "go/taskflow/service_test.go"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "go/taskflow/parser.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/service.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/parser_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/service_test.go",
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

## 2026-08-07T05:59:59.936580Z — target=`quality` fingerprint=`34d637f035600903`
- exit_code: `10`
```text
s",
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
          "path": "docs/process/records-archiving-policy.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_cockpit_http.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_lock.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_records_archive.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_offline_frontend.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-1",
      "title": "���ļ���������ģ���ĵ�ϸ����2026-08-06���û�ָ����� ȫ�־�̬ɨ�裨AST���﷨/�ɱ�Ĭ�ϲ���/�� except/eval/TODO��+ ���ļ������߲飨���ݽṹ/�㷨/�ܹ����������﷨�����޿ɱ�Ĭ�ϲ��������� except���� ���� 14 �������루`report/builder.py`��`audit_governance/models.py`��`config.py`��`knowledge_base/store.py`��`talent/*`��`task_decomposition/*`��`task_flow/*`��`workspace/init_service.py`��`benchmarks/__init__.py`������ �޸� `health_check.check_audit` ����ì�ܡ������� `verify --allow-tail`�����β��δ�ܷ� = degraded��ԭʵ������ status ��Ϊ critical�����ĵ����������� 4 ��⣨fully-sealed ok / δ�ܷ�β�� degraded / ��ʵʧ�� critical / ��ʱ critical������ `docs/modules/` 22 ��ģ�� README ��ͳһģ��ϸ������λ/ְ��߽�/�ļ���ؼ�����/������/��ȫ������/���Ը���/���������Σ���",
      "code": [
        "scripts/health_check.py",
        "src/coevo",
        "docs/modules/"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-10",
      "title": "��ʮ�����ļ����������ĵ�ϸ����2026-08-07���û�ָ����� OPTIMIZE-9������ ����ͼ�����߽�̽�롪���Ի��ܾ���˫�ڵ㻷�����ڵ㻷��a��b��c��a��������ȷ���ԡ�δ֪���� ID �ܾ������в��ԣ������걸���貹���� ����ʣ�� 16 ��ģ��Ӣ��ȫ���ĵ���app/benchmarks/cockpit/decision_brief/knowledge_base/model/orchestrator/progress_capture/report/risk/root_modules/supervision/talent/task_decomposition/task_flow/workspace �� .en.md�������� 21/21 ģ����Ӣ���ĵ�ȫ���ǣ�README.en.md ������ȫ��",
      "code": [
        "docs/modules/",
        "docs/modules/README.en.md"
      ],
      "tests": [
        "tests/unit/test_task_decomposition.py",
        "tests/unit/test_optimizations.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/README.en.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_task_decomposition.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_optimizations.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "GO-MIGRATE",
      "ac": "GO-ENV-1",
      "title": "Go �����������뻷������������Դ `D:\\Go` go1.18.8��toolchain-lock �Ǽ� + ����֤�ļ���+ �׸�Ǩ����Ƭ��`task_flow` ��ģ����׶�ӳ�� Go ��ֲ��SourceKind / StandardStage / Traced / SourceMapping / ProcessFlow / WithOverrides / ApplyMapping / 27 ��Ĭ��ӳ�������Ϊ�� Python ���룩+ `go test ./...` ���������Ž���`GOPROXY=off` ǿ�����ߡ�stdlib-only��",
      "code": [
        "docs/dependencies/toolchain-lock.json",
        "docs/dependencies/licenses/go-BSD-3-Clause.txt",
        "go/go.mod",
        "go/taskflow/doc.go",
        "go/taskflow/models.go",
        "go/taskflow/mapping.go",
        "scripts/quality_gate.py",
        "scripts/tool-shims/make.cs",
        "docs/dependencies/python-script-lock.tsv"
      ],
      "tests": [
        "go/taskflow/models_test.go",
        "go/taskflow/mapping_test.go"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/licenses/go-BSD-3-Clause.txt",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/go.mod",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/models.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/mapping.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
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
          "kind": "test",
          "path": "go/taskflow/models_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/mapping_test.go",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "GO-MIGRATE",
      "ac": "GO-PARSER-1",
      "title": "�ڶ�Ǩ����Ƭ��`task_flow` ȷ���Խ������� service ���� Go ��ֲ����Ϊ�� Python �ο�ʵ�ֶ��룩����parser.go ֧�� canonical/tabular/tree �� schema��tabular/tree ��Լ�� canonical����fail-closed��δ֪ format���ظ� stage/node/role id��ȱ unit_id/������/��������Ƿ� id��ȱʡ�б��ֶΡ����ַ��� stage_hint��tree �ṹ�𻵡�tabular δ֪�У���created_at �ÿ�ע��ʱ�ӣ�Ĭ�� UTC ISO-8601 Z���� informational����service.go ʵ�� FlowUnderstandingService��Understand/Confirm/ToAuditRecord����StageGraph���׶�˳��/��Ա/�ڵ���׶�/��׼�׶� O(1) ��������ReviewerView��source-mapping �����ŶȲ�ѯ����TaskFlowValidationError������ ProcessFlowError ����Լ��",
      "code": [
        "go/taskflow/parser.go",
        "go/taskflow/service.go",
        "go/taskflow/doc.go"
      ],
      "tests": [
        "go/taskflow/parser_test.go",
        "go/taskflow/service_test.go"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "go/taskflow/parser.go",
          "exists": false
        },
        {
          "kind": "code",
          "path": "go/taskflow/service.go",
          "exists": false
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/parser_test.go",
          "exists": false
        },
        {
          "kind": "test",
          "path": "go/taskflow/service_test.go",
          "exists": false
        }
      ],
      "kind": "missing"
    }
  ]
}

```

## 2026-08-07T06:00:57.251371Z — target=`quality` fingerprint=`34d637f035600903`
- exit_code: `1`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\validate_opencode.py
PASS required: AGENTS.md
PASS required: opencode.jsonc
PASS required: Makefile
PASS required: docs/README.md
PASS required: loop/STATE.json
PASS required: loop/BACKLOG.yaml
PASS required: loop/VERIFICATION.md
PASS required: loop/tool-audit.jsonl
PASS required: .opencode/plugins/loop-guard.ts
PASS required: .opencode/tools/loop_state.ts
PASS required: .opencode/tools/quality_gate.ts
PASS required: .opencode/tools/traceability_check.ts
PASS required: tests/unit
PASS required: tests/integration
PASS required: tests/security
PASS required: tests/e2e
PASS denied: webfetch
PASS denied: websearch
PASS denied: external_directory
PASS bash defaults to ask
PASS bash denied: git push*
PASS bash denied: curl *
PASS bash denied: wget *
PASS bash denied: pip install*
PASS bash denied: npm install*
PASS current tool API: loop_state.ts
PASS current tool API: quality_gate.ts
PASS current tool API: traceability_check.ts
{"ok": true, "failures": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz traceability_check
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "E:\Workspace\Coevo\.tools\control\control.pyz\__main__.py", line 18, in <module>
    runpy.run_module(name, run_name="__main__", alter_sys=True)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen runpy>", line 226, in run_module
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "E:\Workspace\Coevo\.tools\control\control.pyz\traceability_check.py", line 40, in <module>
    if __name__=="__main__": raise SystemExit(main())
                                              ~~~~^^
  File "E:\Workspace\Coevo\.tools\control\control.pyz\traceability_check.py", line 39, in main
    summary=check(args.story,not args.all_statuses); print(json.dumps(summary,ensure_ascii=False,indent=2)); return 0 if summary["checked"] and not summary["missing"] else 10
  File "E:\Workspace\Coevo\.tools\control\control.pyz\traceability_check.py", line 24, in check
    for row in parse(MATRIX.read_text(encoding="utf-8")):
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "E:\Workspace\Coevo\.tools\python\3.14.3\Lib\pathlib\__init__.py", line 788, in read_text
    return f.read()
           ~~~~~~^^
  File "<frozen codecs>", line 325, in decode
UnicodeDecodeError: 'utf-8' codec can't decode bytes in position 15-16: invalid continuation byte

```

## 2026-08-07T06:15:50.080326Z — target=`quality` fingerprint=`34d637f035600903`
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
Ran 99 tests in 111.798s

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
Ran 14 tests in 215.443s

OK
audit seal: fully-sealed

```

## 2026-08-07T11:36:18.398856Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
.cs",
        "docs/dependencies/python-script-lock.tsv",
        "docs/dependencies/toolchain-lock.json",
        "docs/process/records-archiving-policy.md"
      ],
      "tests": [
        "tests/unit/test_cockpit_http.py",
        "tests/unit/test_quality_gate_lock.py",
        "tests/unit/test_secret_scan.py",
        "tests/unit/test_records_archive.py",
        "tests/integration/test_cockpit_http_server.py",
        "tests/e2e/test_cockpit_launcher.py",
        "tests/e2e/test_cockpit_offline_frontend.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/archive_records.py",
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
          "path": "docs/process/records-archiving-policy.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_cockpit_http.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_lock.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_records_archive.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_offline_frontend.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-1",
      "title": "���ļ���������ģ���ĵ�ϸ����2026-08-06���û�ָ����� ȫ�־�̬ɨ�裨AST���﷨/�ɱ�Ĭ�ϲ���/�� except/eval/TODO��+ ���ļ������߲飨���ݽṹ/�㷨/�ܹ����������﷨�����޿ɱ�Ĭ�ϲ��������� except���� ���� 14 �������루`report/builder.py`��`audit_governance/models.py`��`config.py`��`knowledge_base/store.py`��`talent/*`��`task_decomposition/*`��`task_flow/*`��`workspace/init_service.py`��`benchmarks/__init__.py`������ �޸� `health_check.check_audit` ����ì�ܡ������� `verify --allow-tail`�����β��δ�ܷ� = degraded��ԭʵ������ status ��Ϊ critical�����ĵ����������� 4 ��⣨fully-sealed ok / δ�ܷ�β�� degraded / ��ʵʧ�� critical / ��ʱ critical������ `docs/modules/` 22 ��ģ�� README ��ͳһģ��ϸ������λ/ְ��߽�/�ļ���ؼ�����/������/��ȫ������/���Ը���/���������Σ���",
      "code": [
        "scripts/health_check.py",
        "src/coevo",
        "docs/modules/"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-10",
      "title": "��ʮ�����ļ����������ĵ�ϸ����2026-08-07���û�ָ����� OPTIMIZE-9������ ����ͼ�����߽�̽�롪���Ի��ܾ���˫�ڵ㻷�����ڵ㻷��a��b��c��a��������ȷ���ԡ�δ֪���� ID �ܾ������в��ԣ������걸���貹���� ����ʣ�� 16 ��ģ��Ӣ��ȫ���ĵ���app/benchmarks/cockpit/decision_brief/knowledge_base/model/orchestrator/progress_capture/report/risk/root_modules/supervision/talent/task_decomposition/task_flow/workspace �� .en.md�������� 21/21 ģ����Ӣ���ĵ�ȫ���ǣ�README.en.md ������ȫ��",
      "code": [
        "docs/modules/",
        "docs/modules/README.en.md"
      ],
      "tests": [
        "tests/unit/test_task_decomposition.py",
        "tests/unit/test_optimizations.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/README.en.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_task_decomposition.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_optimizations.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "GO-MIGRATE",
      "ac": "GO-ENV-1",
      "title": "Go �����������뻷������������Դ `D:\\Go` go1.18.8��toolchain-lock �Ǽ� + ����֤�ļ���+ �׸�Ǩ����Ƭ��`task_flow` ��ģ����׶�ӳ�� Go ��ֲ��SourceKind / StandardStage / Traced / SourceMapping / ProcessFlow / WithOverrides / ApplyMapping / 27 ��Ĭ��ӳ�������Ϊ�� Python ���룩+ `go test ./...` ���������Ž���`GOPROXY=off` ǿ�����ߡ�stdlib-only��",
      "code": [
        "docs/dependencies/toolchain-lock.json",
        "docs/dependencies/licenses/go-BSD-3-Clause.txt",
        "go/go.mod",
        "go/taskflow/doc.go",
        "go/taskflow/models.go",
        "go/taskflow/mapping.go",
        "scripts/quality_gate.py",
        "scripts/tool-shims/make.cs",
        "docs/dependencies/python-script-lock.tsv"
      ],
      "tests": [
        "go/taskflow/models_test.go",
        "go/taskflow/mapping_test.go"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/licenses/go-BSD-3-Clause.txt",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/go.mod",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/models.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/mapping.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
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
          "kind": "test",
          "path": "go/taskflow/models_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/mapping_test.go",
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

## 2026-08-07T11:59:49.359530Z — target=`quality` fingerprint=`34d637f035600903`
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
Ran 99 tests in 110.551s

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
Ran 14 tests in 256.568s

OK
audit seal: fully-sealed

```

## 2026-08-07 — US-16-AC-1 双签记录（mvp-verifier + security-reviewer 独立放行）

- 工作项：`US-16-AC-1-framework-manifest-checker-v0.1`（框架层 manifest-checker，CTAF §5.3 / M1a）。
- 提交：`5536c92`（实现）+ `9fcc906`（security-review M1 硬化修复）。
- **mvp-verifier**：PASS。10/10 AC 均有断言级测试并实测通过（31/31 定向）；主仓库
  `make quality` exit=0 fingerprint=`34d637f035600903`（2026-08-07T11:59:49Z，audit
  fully-sealed）；沙箱定向 25+2 OK、单元 991 OK、集成 256 OK、安全 97 OK。
  环境性说明：沙箱内全量门禁 exit=1 仅因既有 `test_force_remove_safety` 路径钉死
  （主机器路径）与 e2e 预检对未封尾的拒绝，均与 US-16 无关；沙箱 check 零违规。
- **security-reviewer**：PASS。STRIDE 逐项通过，无 Critical/High、无阻断项；
  非阻断发现 7 条：M1（深层嵌套/无大小上限）与 L3（failure_reason 截断）、L5
  （NaN/Infinity 拒绝）、L6（注入依赖异常收敛）已就地修复于 `9fcc906`；L2
  （trusted_anchor 语义，信任委托注入 resolver 已文档化）、L4（审计脱敏接线）、
  L7（semver/时间格式校验）记入 DECISIONS 与后续轮次。
- 追溯矩阵新增 US-16 | AC-1 行（无悬空）；BACKLOG `US-16-AC-1-*` 置 done；
  STATE 置 US-16 / US-16-AC-1 / phase=decide / status=done。

## 2026-08-07T14:22:36.264908Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
.cs",
        "docs/dependencies/python-script-lock.tsv",
        "docs/dependencies/toolchain-lock.json",
        "docs/process/records-archiving-policy.md"
      ],
      "tests": [
        "tests/unit/test_cockpit_http.py",
        "tests/unit/test_quality_gate_lock.py",
        "tests/unit/test_secret_scan.py",
        "tests/unit/test_records_archive.py",
        "tests/integration/test_cockpit_http_server.py",
        "tests/e2e/test_cockpit_launcher.py",
        "tests/e2e/test_cockpit_offline_frontend.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/cockpit/server.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/secret_scan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/archive_records.py",
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
          "path": "docs/process/records-archiving-policy.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_cockpit_http.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_lock.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_records_archive.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_offline_frontend.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-1",
      "title": "���ļ���������ģ���ĵ�ϸ����2026-08-06���û�ָ����� ȫ�־�̬ɨ�裨AST���﷨/�ɱ�Ĭ�ϲ���/�� except/eval/TODO��+ ���ļ������߲飨���ݽṹ/�㷨/�ܹ����������﷨�����޿ɱ�Ĭ�ϲ��������� except���� ���� 14 �������루`report/builder.py`��`audit_governance/models.py`��`config.py`��`knowledge_base/store.py`��`talent/*`��`task_decomposition/*`��`task_flow/*`��`workspace/init_service.py`��`benchmarks/__init__.py`������ �޸� `health_check.check_audit` ����ì�ܡ������� `verify --allow-tail`�����β��δ�ܷ� = degraded��ԭʵ������ status ��Ϊ critical�����ĵ����������� 4 ��⣨fully-sealed ok / δ�ܷ�β�� degraded / ��ʵʧ�� critical / ��ʱ critical������ `docs/modules/` 22 ��ģ�� README ��ͳһģ��ϸ������λ/ְ��߽�/�ļ���ؼ�����/������/��ȫ������/���Ը���/���������Σ���",
      "code": [
        "scripts/health_check.py",
        "src/coevo",
        "docs/modules/"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-10",
      "title": "��ʮ�����ļ����������ĵ�ϸ����2026-08-07���û�ָ����� OPTIMIZE-9������ ����ͼ�����߽�̽�롪���Ի��ܾ���˫�ڵ㻷�����ڵ㻷��a��b��c��a��������ȷ���ԡ�δ֪���� ID �ܾ������в��ԣ������걸���貹���� ����ʣ�� 16 ��ģ��Ӣ��ȫ���ĵ���app/benchmarks/cockpit/decision_brief/knowledge_base/model/orchestrator/progress_capture/report/risk/root_modules/supervision/talent/task_decomposition/task_flow/workspace �� .en.md�������� 21/21 ģ����Ӣ���ĵ�ȫ���ǣ�README.en.md ������ȫ��",
      "code": [
        "docs/modules/",
        "docs/modules/README.en.md"
      ],
      "tests": [
        "tests/unit/test_task_decomposition.py",
        "tests/unit/test_optimizations.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/README.en.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_task_decomposition.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_optimizations.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "GO-MIGRATE",
      "ac": "GO-ENV-1",
      "title": "Go �����������뻷������������Դ `D:\\Go` go1.18.8��toolchain-lock �Ǽ� + ����֤�ļ���+ �׸�Ǩ����Ƭ��`task_flow` ��ģ����׶�ӳ�� Go ��ֲ��SourceKind / StandardStage / Traced / SourceMapping / ProcessFlow / WithOverrides / ApplyMapping / 27 ��Ĭ��ӳ�������Ϊ�� Python ���룩+ `go test ./...` ���������Ž���`GOPROXY=off` ǿ�����ߡ�stdlib-only��",
      "code": [
        "docs/dependencies/toolchain-lock.json",
        "docs/dependencies/licenses/go-BSD-3-Clause.txt",
        "go/go.mod",
        "go/taskflow/doc.go",
        "go/taskflow/models.go",
        "go/taskflow/mapping.go",
        "scripts/quality_gate.py",
        "scripts/tool-shims/make.cs",
        "docs/dependencies/python-script-lock.tsv"
      ],
      "tests": [
        "go/taskflow/models_test.go",
        "go/taskflow/mapping_test.go"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/licenses/go-BSD-3-Clause.txt",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/go.mod",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/models.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/mapping.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
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
          "kind": "test",
          "path": "go/taskflow/models_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/mapping_test.go",
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

## 2026-08-07T14:28:15.349691Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
oolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/process/records-archiving-policy.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_cockpit_http.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_lock.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_records_archive.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_offline_frontend.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-1",
      "title": "���ļ���������ģ���ĵ�ϸ����2026-08-06���û�ָ����� ȫ�־�̬ɨ�裨AST���﷨/�ɱ�Ĭ�ϲ���/�� except/eval/TODO��+ ���ļ������߲飨���ݽṹ/�㷨/�ܹ����������﷨�����޿ɱ�Ĭ�ϲ��������� except���� ���� 14 �������루`report/builder.py`��`audit_governance/models.py`��`config.py`��`knowledge_base/store.py`��`talent/*`��`task_decomposition/*`��`task_flow/*`��`workspace/init_service.py`��`benchmarks/__init__.py`������ �޸� `health_check.check_audit` ����ì�ܡ������� `verify --allow-tail`�����β��δ�ܷ� = degraded��ԭʵ������ status ��Ϊ critical�����ĵ����������� 4 ��⣨fully-sealed ok / δ�ܷ�β�� degraded / ��ʵʧ�� critical / ��ʱ critical������ `docs/modules/` 22 ��ģ�� README ��ͳһģ��ϸ������λ/ְ��߽�/�ļ���ؼ�����/������/��ȫ������/���Ը���/���������Σ���",
      "code": [
        "scripts/health_check.py",
        "src/coevo",
        "docs/modules/"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-10",
      "title": "��ʮ�����ļ����������ĵ�ϸ����2026-08-07���û�ָ����� OPTIMIZE-9������ ����ͼ�����߽�̽�롪���Ի��ܾ���˫�ڵ㻷�����ڵ㻷��a��b��c��a��������ȷ���ԡ�δ֪���� ID �ܾ������в��ԣ������걸���貹���� ����ʣ�� 16 ��ģ��Ӣ��ȫ���ĵ���app/benchmarks/cockpit/decision_brief/knowledge_base/model/orchestrator/progress_capture/report/risk/root_modules/supervision/talent/task_decomposition/task_flow/workspace �� .en.md�������� 21/21 ģ����Ӣ���ĵ�ȫ���ǣ�README.en.md ������ȫ��",
      "code": [
        "docs/modules/",
        "docs/modules/README.en.md"
      ],
      "tests": [
        "tests/unit/test_task_decomposition.py",
        "tests/unit/test_optimizations.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/README.en.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_task_decomposition.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_optimizations.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "GO-MIGRATE",
      "ac": "GO-ENV-1",
      "title": "Go �����������뻷������������Դ `D:\\Go` go1.18.8��toolchain-lock �Ǽ� + ����֤�ļ���+ �׸�Ǩ����Ƭ��`task_flow` ��ģ����׶�ӳ�� Go ��ֲ��SourceKind / StandardStage / Traced / SourceMapping / ProcessFlow / WithOverrides / ApplyMapping / 27 ��Ĭ��ӳ�������Ϊ�� Python ���룩+ `go test ./...` ���������Ž���`GOPROXY=off` ǿ�����ߡ�stdlib-only��",
      "code": [
        "docs/dependencies/toolchain-lock.json",
        "docs/dependencies/licenses/go-BSD-3-Clause.txt",
        "go/go.mod",
        "go/taskflow/doc.go",
        "go/taskflow/models.go",
        "go/taskflow/mapping.go",
        "scripts/quality_gate.py",
        "scripts/tool-shims/make.cs",
        "docs/dependencies/python-script-lock.tsv"
      ],
      "tests": [
        "go/taskflow/models_test.go",
        "go/taskflow/mapping_test.go"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/licenses/go-BSD-3-Clause.txt",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/go.mod",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/models.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/mapping.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
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
          "kind": "test",
          "path": "go/taskflow/models_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/mapping_test.go",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-1",
      "title": "��ܲ� manifest-checker��CTAF ��5.3 / M1a����Agent Manifest ǿ��У�飨�����ռ� T2 / �˹�ȷ��ȱʡ true T3 / crypto_scope �ռ� T4 / ��������Ӽ� T5 / spec_hash �ų���ָ�ֶ� F5 / policy_ref ���ΰ��ҹ�Կȡ��֤���� F8 / policy_version �� F7 / ʧ�ܲ�ע�� / �������������������� L15��+ `.agent` v1.0 wire �ֽڼ��ع� T6",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_agent_wire_regression.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
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

## 2026-08-07T15:28:48.032631Z — target=`quality` fingerprint=`34d637f035600903`
- exit_code: `1`
```text
eck.TraceabilityTests.test_us_5_ac_1_matrix_lists_src_and_test) ... ok
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
FAIL: test_probe_completes_with_zero_errors (test_benchmark_http.CockpitHttpProbeTests.test_probe_completes_with_zero_errors)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\unit\test_benchmark_http.py", line 25, in test_probe_completes_with_zero_errors
    self.assertTrue(result.ok, result.detail)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true : p50=0.0371s max=8.7947s errors=0

======================================================================
FAIL: test_probe_reports_latency_bounds (test_benchmark_http.CockpitHttpProbeTests.test_probe_reports_latency_bounds)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\Workspace\Coevo\tests\unit\test_benchmark_http.py", line 31, in test_probe_reports_latency_bounds
    self.assertLess(result.value, result.limit)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 2.1047 not less than 1.0

----------------------------------------------------------------------
Ran 1034 tests in 451.072s

FAILED (failures=2, skipped=3)

```

## 2026-08-07T16:32:24.018002Z — target=`quality` fingerprint=`34d637f035600903`
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
Ran 99 tests in 90.039s

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
Ran 14 tests in 146.606s

OK
audit seal: fully-sealed

```

## 2026-08-08 — US-16-AC-4 双签记录（mvp-verifier + security-reviewer）

- 工作项：`US-16-AC-4-framework-memory-interface-v0.1`（Memory 抽象，CTAF §6.2 / M3）。
- 提交：`c988cd9`（实现）+ `727e739`（security-review Low 硬化修复）。
- **验证（增量门禁口径，用户指示豁免全量 quality）**：主仓库定向 104/104 全绿 +
  `--target lint` exit=0 fingerprint=`252ad24e526f6728`（audit fully-sealed）；
  security-reviewer 在钉扎沙箱内实测 memory 13 项 + 模块文档守卫 4 项全绿；
  mvp-verifier 子代理本轮被中断未交付文本报告，验证证据以主仓库增量门禁 +
  沙箱审查实测为准（已记录偏差）。
- **security-reviewer**：PASS。STRIDE 逐项通过，无 Critical/High、无阻断项；
  Low 3 观察项：① 畸形 kind 下审计投影防御取值（已就地修复 `727e739`）；
  ② Semantic 审批检查器接收脱敏前明文（信任边界已写入 memory-interface.md）；
  ③ 拒绝写入审计含 record_id 指纹（设计使然，生产 Redactor 须加盐/密钥化）。
- 环境发现：沙箱副本缺 `.tools/control/control.pyz`，沙箱内 gate 无法启动
  （exit 2，环境问题与实现无关）；主仓库增量门禁作为本轮证据。
- 追溯矩阵新增 US-16 | AC-4 行（无悬空）；BACKLOG `US-16-AC-4-*` 置 done；
  STATE 置 US-16 / US-16-AC-4 / phase=decide / status=done。

## 2026-08-07 — US-16-AC-2 双签记录（mvp-verifier + security-reviewer 独立放行）

- 工作项：`US-16-AC-2-framework-policy-abstractions-v0.1`（Policy 抽象 +
  validate_plan，CTAF §6.5 / M2）。
- 提交：`7a3ed8b`（实现）+ `b23d85b`（security-review Low 硬化修复）。
- **mvp-verifier**：PASS（10/10 AC）。沙箱定向 4 文件 68 项全绿；主仓库
  `make quality` exit=0 fingerprint=`34d637f035600903`（2026-08-07T16:32:24Z，
  audit fully-sealed）；沙箱内门禁失败均为环境性（benchmark 延迟抖动、沙箱
  `.tools` 重解析点/SM2 ACL、主机路径钉死），与 US-16-AC-2 无关；沙箱 check
  零违规。
- **security-reviewer**：PASS。STRIDE 逐项通过，无 Critical/High、无阻断项；
  非阻断发现 5 条：Low1（Plan/tool_args 规模上限）、Low2（tool_args 重复键
  语义不一致）、Info3（validated_at 必填）已就地修复于 `b23d85b`；Info4
  （非 EMERGENCY 超时上界）、Info5（宽捕获设计取舍）记入 DECISIONS 与后续轮次。
- 追溯矩阵新增 US-16 | AC-2 行（无悬空）；BACKLOG `US-16-AC-2-*` 置 done；
  STATE 置 US-16 / US-16-AC-2 / phase=decide / status=done。

## 2026-08-07T16:33:12.328271Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
oolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/process/records-archiving-policy.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_cockpit_http.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_quality_gate_lock.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_secret_scan.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_records_archive.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/integration/test_cockpit_http_server.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_launcher.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/e2e/test_cockpit_offline_frontend.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-1",
      "title": "���ļ���������ģ���ĵ�ϸ����2026-08-06���û�ָ����� ȫ�־�̬ɨ�裨AST���﷨/�ɱ�Ĭ�ϲ���/�� except/eval/TODO��+ ���ļ������߲飨���ݽṹ/�㷨/�ܹ����������﷨�����޿ɱ�Ĭ�ϲ��������� except���� ���� 14 �������루`report/builder.py`��`audit_governance/models.py`��`config.py`��`knowledge_base/store.py`��`talent/*`��`task_decomposition/*`��`task_flow/*`��`workspace/init_service.py`��`benchmarks/__init__.py`������ �޸� `health_check.check_audit` ����ì�ܡ������� `verify --allow-tail`�����β��δ�ܷ� = degraded��ԭʵ������ status ��Ϊ critical�����ĵ����������� 4 ��⣨fully-sealed ok / δ�ܷ�β�� degraded / ��ʵʧ�� critical / ��ʱ critical������ `docs/modules/` 22 ��ģ�� README ��ͳһģ��ϸ������λ/ְ��߽�/�ļ���ؼ�����/������/��ȫ������/���Ը���/���������Σ���",
      "code": [
        "scripts/health_check.py",
        "src/coevo",
        "docs/modules/"
      ],
      "tests": [
        "tests/unit/test_ops_tooling.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "scripts/health_check.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-10",
      "title": "��ʮ�����ļ����������ĵ�ϸ����2026-08-07���û�ָ����� OPTIMIZE-9������ ����ͼ�����߽�̽�롪���Ի��ܾ���˫�ڵ㻷�����ڵ㻷��a��b��c��a��������ȷ���ԡ�δ֪���� ID �ܾ������в��ԣ������걸���貹���� ����ʣ�� 16 ��ģ��Ӣ��ȫ���ĵ���app/benchmarks/cockpit/decision_brief/knowledge_base/model/orchestrator/progress_capture/report/risk/root_modules/supervision/talent/task_decomposition/task_flow/workspace �� .en.md�������� 21/21 ģ����Ӣ���ĵ�ȫ���ǣ�README.en.md ������ȫ��",
      "code": [
        "docs/modules/",
        "docs/modules/README.en.md"
      ],
      "tests": [
        "tests/unit/test_task_decomposition.py",
        "tests/unit/test_optimizations.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/README.en.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_task_decomposition.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_optimizations.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "GO-MIGRATE",
      "ac": "GO-ENV-1",
      "title": "Go �����������뻷������������Դ `D:\\Go` go1.18.8��toolchain-lock �Ǽ� + ����֤�ļ���+ �׸�Ǩ����Ƭ��`task_flow` ��ģ����׶�ӳ�� Go ��ֲ��SourceKind / StandardStage / Traced / SourceMapping / ProcessFlow / WithOverrides / ApplyMapping / 27 ��Ĭ��ӳ�������Ϊ�� Python ���룩+ `go test ./...` ���������Ž���`GOPROXY=off` ǿ�����ߡ�stdlib-only��",
      "code": [
        "docs/dependencies/toolchain-lock.json",
        "docs/dependencies/licenses/go-BSD-3-Clause.txt",
        "go/go.mod",
        "go/taskflow/doc.go",
        "go/taskflow/models.go",
        "go/taskflow/mapping.go",
        "scripts/quality_gate.py",
        "scripts/tool-shims/make.cs",
        "docs/dependencies/python-script-lock.tsv"
      ],
      "tests": [
        "go/taskflow/models_test.go",
        "go/taskflow/mapping_test.go"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/licenses/go-BSD-3-Clause.txt",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/go.mod",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/models.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/mapping.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
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
          "kind": "test",
          "path": "go/taskflow/models_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/mapping_test.go",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-1",
      "title": "��ܲ� manifest-checker��CTAF ��5.3 / M1a����Agent Manifest ǿ��У�飨�����ռ� T2 / �˹�ȷ��ȱʡ true T3 / crypto_scope �ռ� T4 / ��������Ӽ� T5 / spec_hash �ų���ָ�ֶ� F5 / policy_ref ���ΰ��ҹ�Կȡ��֤���� F8 / policy_version �� F7 / ʧ�ܲ�ע�� / �������������������� L15��+ `.agent` v1.0 wire �ֽڼ��ع� T6",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_agent_wire_regression.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
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

## 2026-08-07T16:37:59.882042Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text

          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-10",
      "title": "��ʮ�����ļ����������ĵ�ϸ����2026-08-07���û�ָ����� OPTIMIZE-9������ ����ͼ�����߽�̽�롪���Ի��ܾ���˫�ڵ㻷�����ڵ㻷��a��b��c��a��������ȷ���ԡ�δ֪���� ID �ܾ������в��ԣ������걸���貹���� ����ʣ�� 16 ��ģ��Ӣ��ȫ���ĵ���app/benchmarks/cockpit/decision_brief/knowledge_base/model/orchestrator/progress_capture/report/risk/root_modules/supervision/talent/task_decomposition/task_flow/workspace �� .en.md�������� 21/21 ģ����Ӣ���ĵ�ȫ���ǣ�README.en.md ������ȫ��",
      "code": [
        "docs/modules/",
        "docs/modules/README.en.md"
      ],
      "tests": [
        "tests/unit/test_task_decomposition.py",
        "tests/unit/test_optimizations.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/README.en.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_task_decomposition.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_optimizations.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "GO-MIGRATE",
      "ac": "GO-ENV-1",
      "title": "Go �����������뻷������������Դ `D:\\Go` go1.18.8��toolchain-lock �Ǽ� + ����֤�ļ���+ �׸�Ǩ����Ƭ��`task_flow` ��ģ����׶�ӳ�� Go ��ֲ��SourceKind / StandardStage / Traced / SourceMapping / ProcessFlow / WithOverrides / ApplyMapping / 27 ��Ĭ��ӳ�������Ϊ�� Python ���룩+ `go test ./...` ���������Ž���`GOPROXY=off` ǿ�����ߡ�stdlib-only��",
      "code": [
        "docs/dependencies/toolchain-lock.json",
        "docs/dependencies/licenses/go-BSD-3-Clause.txt",
        "go/go.mod",
        "go/taskflow/doc.go",
        "go/taskflow/models.go",
        "go/taskflow/mapping.go",
        "scripts/quality_gate.py",
        "scripts/tool-shims/make.cs",
        "docs/dependencies/python-script-lock.tsv"
      ],
      "tests": [
        "go/taskflow/models_test.go",
        "go/taskflow/mapping_test.go"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/licenses/go-BSD-3-Clause.txt",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/go.mod",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/models.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/mapping.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
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
          "kind": "test",
          "path": "go/taskflow/models_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/mapping_test.go",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-1",
      "title": "��ܲ� manifest-checker��CTAF ��5.3 / M1a����Agent Manifest ǿ��У�飨�����ռ� T2 / �˹�ȷ��ȱʡ true T3 / crypto_scope �ռ� T4 / ��������Ӽ� T5 / spec_hash �ų���ָ�ֶ� F5 / policy_ref ���ΰ��ҹ�Կȡ��֤���� F8 / policy_version �� F7 / ʧ�ܲ�ע�� / �������������������� L15��+ `.agent` v1.0 wire �ֽڼ��ع� T6",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_agent_wire_regression.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-2",
      "title": "��ܲ� Policy ������ validate_plan��CTAF ��6.5 / M2����Policy �ֶ��� policy_version ���F7����4 Ĭ�� Profile��max_recover_attempts �� 3 ���� L16����EMERGENCY fail-fast��1 ������ / 60s / �º� 30 ����ȷ�� / ���ظ澯��F1+F9����L18 ��������tool_args ��ֵ�� schema ������F6����validate_plan ������� + L18 + L19��A9/F4����L19 ״̬����ESCALATED��ACTIVE ���뾭 HELD��RETIRED ֱ�ˣ�������������������������L15��+ L17 �ĵ�����",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/plan.py",
        "src/coevo/framework/lifecycle.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_policy.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py",
        "tests/unit/test_framework_validate_plan.py"
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
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/lifecycle.py",
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
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_policy.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
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

## 2026-08-07T16:40:58.727263Z — target=`fmt` fingerprint=`8d456a2ce09245c7`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ C:\Python314\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```

## 2026-08-07T16:41:08.676007Z — target=`lint` fingerprint=`4800c1ade060c9f3`
- exit_code: `0`
```text
rue
        },
        {
          "kind": "code",
          "path": "src/coevo",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-10",
      "title": "��ʮ�����ļ����������ĵ�ϸ����2026-08-07���û�ָ����� OPTIMIZE-9������ ����ͼ�����߽�̽�롪���Ի��ܾ���˫�ڵ㻷�����ڵ㻷��a��b��c��a��������ȷ���ԡ�δ֪���� ID �ܾ������в��ԣ������걸���貹���� ����ʣ�� 16 ��ģ��Ӣ��ȫ���ĵ���app/benchmarks/cockpit/decision_brief/knowledge_base/model/orchestrator/progress_capture/report/risk/root_modules/supervision/talent/task_decomposition/task_flow/workspace �� .en.md�������� 21/21 ģ����Ӣ���ĵ�ȫ���ǣ�README.en.md ������ȫ��",
      "code": [
        "docs/modules/",
        "docs/modules/README.en.md"
      ],
      "tests": [
        "tests/unit/test_task_decomposition.py",
        "tests/unit/test_optimizations.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/README.en.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_task_decomposition.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_optimizations.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "GO-MIGRATE",
      "ac": "GO-ENV-1",
      "title": "Go �����������뻷������������Դ `D:\\Go` go1.18.8��toolchain-lock �Ǽ� + ����֤�ļ���+ �׸�Ǩ����Ƭ��`task_flow` ��ģ����׶�ӳ�� Go ��ֲ��SourceKind / StandardStage / Traced / SourceMapping / ProcessFlow / WithOverrides / ApplyMapping / 27 ��Ĭ��ӳ�������Ϊ�� Python ���룩+ `go test ./...` ���������Ž���`GOPROXY=off` ǿ�����ߡ�stdlib-only��",
      "code": [
        "docs/dependencies/toolchain-lock.json",
        "docs/dependencies/licenses/go-BSD-3-Clause.txt",
        "go/go.mod",
        "go/taskflow/doc.go",
        "go/taskflow/models.go",
        "go/taskflow/mapping.go",
        "scripts/quality_gate.py",
        "scripts/tool-shims/make.cs",
        "docs/dependencies/python-script-lock.tsv"
      ],
      "tests": [
        "go/taskflow/models_test.go",
        "go/taskflow/mapping_test.go"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/licenses/go-BSD-3-Clause.txt",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/go.mod",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/models.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/mapping.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
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
          "kind": "test",
          "path": "go/taskflow/models_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/mapping_test.go",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-1",
      "title": "��ܲ� manifest-checker��CTAF ��5.3 / M1a����Agent Manifest ǿ��У�飨�����ռ� T2 / �˹�ȷ��ȱʡ true T3 / crypto_scope �ռ� T4 / ��������Ӽ� T5 / spec_hash �ų���ָ�ֶ� F5 / policy_ref ���ΰ��ҹ�Կȡ��֤���� F8 / policy_version �� F7 / ʧ�ܲ�ע�� / �������������������� L15��+ `.agent` v1.0 wire �ֽڼ��ع� T6",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_agent_wire_regression.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-2",
      "title": "��ܲ� Policy ������ validate_plan��CTAF ��6.5 / M2����Policy �ֶ��� policy_version ���F7����4 Ĭ�� Profile��max_recover_attempts �� 3 ���� L16����EMERGENCY fail-fast��1 ������ / 60s / �º� 30 ����ȷ�� / ���ظ澯��F1+F9����L18 ��������tool_args ��ֵ�� schema ������F6����validate_plan ������� + L18 + L19��A9/F4����L19 ״̬����ESCALATED��ACTIVE ���뾭 HELD��RETIRED ֱ�ˣ�������������������������L15��+ L17 �ĵ�����",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/plan.py",
        "src/coevo/framework/lifecycle.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_policy.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py",
        "tests/unit/test_framework_validate_plan.py"
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
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/lifecycle.py",
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
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_policy.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
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

## 2026-08-07T16:42:14.128841Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```

## 2026-08-07T16:42:23.186872Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text

          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_ops_tooling.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "ENG-BASE",
      "ac": "OPTIMIZE-10",
      "title": "��ʮ�����ļ����������ĵ�ϸ����2026-08-07���û�ָ����� OPTIMIZE-9������ ����ͼ�����߽�̽�롪���Ի��ܾ���˫�ڵ㻷�����ڵ㻷��a��b��c��a��������ȷ���ԡ�δ֪���� ID �ܾ������в��ԣ������걸���貹���� ����ʣ�� 16 ��ģ��Ӣ��ȫ���ĵ���app/benchmarks/cockpit/decision_brief/knowledge_base/model/orchestrator/progress_capture/report/risk/root_modules/supervision/talent/task_decomposition/task_flow/workspace �� .en.md�������� 21/21 ģ����Ӣ���ĵ�ȫ���ǣ�README.en.md ������ȫ��",
      "code": [
        "docs/modules/",
        "docs/modules/README.en.md"
      ],
      "tests": [
        "tests/unit/test_task_decomposition.py",
        "tests/unit/test_optimizations.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/modules/",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/README.en.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_task_decomposition.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_optimizations.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "GO-MIGRATE",
      "ac": "GO-ENV-1",
      "title": "Go �����������뻷������������Դ `D:\\Go` go1.18.8��toolchain-lock �Ǽ� + ����֤�ļ���+ �׸�Ǩ����Ƭ��`task_flow` ��ģ����׶�ӳ�� Go ��ֲ��SourceKind / StandardStage / Traced / SourceMapping / ProcessFlow / WithOverrides / ApplyMapping / 27 ��Ĭ��ӳ�������Ϊ�� Python ���룩+ `go test ./...` ���������Ž���`GOPROXY=off` ǿ�����ߡ�stdlib-only��",
      "code": [
        "docs/dependencies/toolchain-lock.json",
        "docs/dependencies/licenses/go-BSD-3-Clause.txt",
        "go/go.mod",
        "go/taskflow/doc.go",
        "go/taskflow/models.go",
        "go/taskflow/mapping.go",
        "scripts/quality_gate.py",
        "scripts/tool-shims/make.cs",
        "docs/dependencies/python-script-lock.tsv"
      ],
      "tests": [
        "go/taskflow/models_test.go",
        "go/taskflow/mapping_test.go"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "docs/dependencies/toolchain-lock.json",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/dependencies/licenses/go-BSD-3-Clause.txt",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/go.mod",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/models.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/mapping.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
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
          "kind": "test",
          "path": "go/taskflow/models_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/mapping_test.go",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-1",
      "title": "��ܲ� manifest-checker��CTAF ��5.3 / M1a����Agent Manifest ǿ��У�飨�����ռ� T2 / �˹�ȷ��ȱʡ true T3 / crypto_scope �ռ� T4 / ��������Ӽ� T5 / spec_hash �ų���ָ�ֶ� F5 / policy_ref ���ΰ��ҹ�Կȡ��֤���� F8 / policy_version �� F7 / ʧ�ܲ�ע�� / �������������������� L15��+ `.agent` v1.0 wire �ֽڼ��ع� T6",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_agent_wire_regression.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-2",
      "title": "��ܲ� Policy ������ validate_plan��CTAF ��6.5 / M2����Policy �ֶ��� policy_version ���F7����4 Ĭ�� Profile��max_recover_attempts �� 3 ���� L16����EMERGENCY fail-fast��1 ������ / 60s / �º� 30 ����ȷ�� / ���ظ澯��F1+F9����L18 ��������tool_args ��ֵ�� schema ������F6����validate_plan ������� + L18 + L19��A9/F4����L19 ״̬����ESCALATED��ACTIVE ���뾭 HELD��RETIRED ֱ�ˣ�������������������������L15��+ L17 �ĵ�����",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/plan.py",
        "src/coevo/framework/lifecycle.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_policy.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py",
        "tests/unit/test_framework_validate_plan.py"
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
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/lifecycle.py",
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
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_policy.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
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

## 2026-08-07T16:53:30.508637Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
SD-3-Clause.txt",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/go.mod",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/models.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/mapping.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
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
          "kind": "test",
          "path": "go/taskflow/models_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/mapping_test.go",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-1",
      "title": "��ܲ� manifest-checker��CTAF ��5.3 / M1a����Agent Manifest ǿ��У�飨�����ռ� T2 / �˹�ȷ��ȱʡ true T3 / crypto_scope �ռ� T4 / ��������Ӽ� T5 / spec_hash �ų���ָ�ֶ� F5 / policy_ref ���ΰ��ҹ�Կȡ��֤���� F8 / policy_version �� F7 / ʧ�ܲ�ע�� / �������������������� L15��+ `.agent` v1.0 wire �ֽڼ��ع� T6",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_agent_wire_regression.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-2",
      "title": "��ܲ� Policy ������ validate_plan��CTAF ��6.5 / M2����Policy �ֶ��� policy_version ���F7����4 Ĭ�� Profile��max_recover_attempts �� 3 ���� L16����EMERGENCY fail-fast��1 ������ / 60s / �º� 30 ����ȷ�� / ���ظ澯��F1+F9����L18 ��������tool_args ��ֵ�� schema ������F6����validate_plan ������� + L18 + L19��A9/F4����L19 ״̬����ESCALATED��ACTIVE ���뾭 HELD��RETIRED ֱ�ˣ�������������������������L15��+ L17 �ĵ�����",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/plan.py",
        "src/coevo/framework/lifecycle.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_policy.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py",
        "tests/unit/test_framework_validate_plan.py"
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
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/lifecycle.py",
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
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_policy.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-3",
      "title": "��ܲ������ռ�������CTAF ��5.2 / M1b��������ע��� 19 �12 MVP ӳ�� AgentCapability / CRYPTO_PROXY �� approved-product / 6 ��ܳ��� PLANNER..HUMAN_GATE����˫��������ö��ֵ / CTAF �淶�� / ��Ա��ͬ��Ŀ���ռ������Сд���� fail-closed����manifest-checker У���л���MVP δӳ��ܾ���CRYPTO_PROXY approved scope����ܳ�����ã���˫��һ�����������޹¶� / ��δӳ�� MVP����capability-closedset.md �ĵ� + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/capability.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "src/coevo/orchestrator/models.py",
        "docs/framework/capability-closedset.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_capability.py",
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_framework_validate_plan.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/capability.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
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
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/capability-closedset.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_capability.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
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
          "path": "tests/unit/test_framework_lifecycle.py",
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

## 2026-08-07T16:53:50.484355Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
SD-3-Clause.txt",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/go.mod",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/models.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/mapping.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
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
          "kind": "test",
          "path": "go/taskflow/models_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/mapping_test.go",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-1",
      "title": "��ܲ� manifest-checker��CTAF ��5.3 / M1a����Agent Manifest ǿ��У�飨�����ռ� T2 / �˹�ȷ��ȱʡ true T3 / crypto_scope �ռ� T4 / ��������Ӽ� T5 / spec_hash �ų���ָ�ֶ� F5 / policy_ref ���ΰ��ҹ�Կȡ��֤���� F8 / policy_version �� F7 / ʧ�ܲ�ע�� / �������������������� L15��+ `.agent` v1.0 wire �ֽڼ��ع� T6",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_agent_wire_regression.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-2",
      "title": "��ܲ� Policy ������ validate_plan��CTAF ��6.5 / M2����Policy �ֶ��� policy_version ���F7����4 Ĭ�� Profile��max_recover_attempts �� 3 ���� L16����EMERGENCY fail-fast��1 ������ / 60s / �º� 30 ����ȷ�� / ���ظ澯��F1+F9����L18 ��������tool_args ��ֵ�� schema ������F6����validate_plan ������� + L18 + L19��A9/F4����L19 ״̬����ESCALATED��ACTIVE ���뾭 HELD��RETIRED ֱ�ˣ�������������������������L15��+ L17 �ĵ�����",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/plan.py",
        "src/coevo/framework/lifecycle.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_policy.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py",
        "tests/unit/test_framework_validate_plan.py"
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
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/lifecycle.py",
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
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_policy.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-3",
      "title": "��ܲ������ռ�������CTAF ��5.2 / M1b��������ע��� 19 �12 MVP ӳ�� AgentCapability / CRYPTO_PROXY �� approved-product / 6 ��ܳ��� PLANNER..HUMAN_GATE����˫��������ö��ֵ / CTAF �淶�� / ��Ա��ͬ��Ŀ���ռ������Сд���� fail-closed����manifest-checker У���л���MVP δӳ��ܾ���CRYPTO_PROXY approved scope����ܳ�����ã���˫��һ�����������޹¶� / ��δӳ�� MVP����capability-closedset.md �ĵ� + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/capability.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "src/coevo/orchestrator/models.py",
        "docs/framework/capability-closedset.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_capability.py",
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_framework_validate_plan.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/capability.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
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
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/capability-closedset.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_capability.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
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
          "path": "tests/unit/test_framework_lifecycle.py",
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

## 2026-08-07T17:00:42.403342Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
SD-3-Clause.txt",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/go.mod",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/doc.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/models.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "go/taskflow/mapping.go",
          "exists": true
        },
        {
          "kind": "code",
          "path": "scripts/quality_gate.py",
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
          "kind": "test",
          "path": "go/taskflow/models_test.go",
          "exists": true
        },
        {
          "kind": "test",
          "path": "go/taskflow/mapping_test.go",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-1",
      "title": "��ܲ� manifest-checker��CTAF ��5.3 / M1a����Agent Manifest ǿ��У�飨�����ռ� T2 / �˹�ȷ��ȱʡ true T3 / crypto_scope �ռ� T4 / ��������Ӽ� T5 / spec_hash �ų���ָ�ֶ� F5 / policy_ref ���ΰ��ҹ�Կȡ��֤���� F8 / policy_version �� F7 / ʧ�ܲ�ע�� / �������������������� L15��+ `.agent` v1.0 wire �ֽڼ��ع� T6",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_agent_wire_regression.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-2",
      "title": "��ܲ� Policy ������ validate_plan��CTAF ��6.5 / M2����Policy �ֶ��� policy_version ���F7����4 Ĭ�� Profile��max_recover_attempts �� 3 ���� L16����EMERGENCY fail-fast��1 ������ / 60s / �º� 30 ����ȷ�� / ���ظ澯��F1+F9����L18 ��������tool_args ��ֵ�� schema ������F6����validate_plan ������� + L18 + L19��A9/F4����L19 ״̬����ESCALATED��ACTIVE ���뾭 HELD��RETIRED ֱ�ˣ�������������������������L15��+ L17 �ĵ�����",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/plan.py",
        "src/coevo/framework/lifecycle.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_policy.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py",
        "tests/unit/test_framework_validate_plan.py"
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
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/lifecycle.py",
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
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_policy.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-3",
      "title": "��ܲ������ռ�������CTAF ��5.2 / M1b��������ע��� 19 �12 MVP ӳ�� AgentCapability / CRYPTO_PROXY �� approved-product / 6 ��ܳ��� PLANNER..HUMAN_GATE����˫��������ö��ֵ / CTAF �淶�� / ��Ա��ͬ��Ŀ���ռ������Сд���� fail-closed����manifest-checker У���л���MVP δӳ��ܾ���CRYPTO_PROXY approved scope����ܳ�����ã���˫��һ�����������޹¶� / ��δӳ�� MVP����capability-closedset.md �ĵ� + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/capability.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "src/coevo/orchestrator/models.py",
        "docs/framework/capability-closedset.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_capability.py",
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_framework_validate_plan.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/capability.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
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
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/capability-closedset.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_capability.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
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
          "path": "tests/unit/test_framework_lifecycle.py",
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

## 2026-08-07T17:05:07.532510Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
_ref ���ΰ��ҹ�Կȡ��֤���� F8 / policy_version �� F7 / ʧ�ܲ�ע�� / �������������������� L15��+ `.agent` v1.0 wire �ֽڼ��ع� T6",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_agent_wire_regression.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-2",
      "title": "��ܲ� Policy ������ validate_plan��CTAF ��6.5 / M2����Policy �ֶ��� policy_version ���F7����4 Ĭ�� Profile��max_recover_attempts �� 3 ���� L16����EMERGENCY fail-fast��1 ������ / 60s / �º� 30 ����ȷ�� / ���ظ澯��F1+F9����L18 ��������tool_args ��ֵ�� schema ������F6����validate_plan ������� + L18 + L19��A9/F4����L19 ״̬����ESCALATED��ACTIVE ���뾭 HELD��RETIRED ֱ�ˣ�������������������������L15��+ L17 �ĵ�����",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/plan.py",
        "src/coevo/framework/lifecycle.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_policy.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py",
        "tests/unit/test_framework_validate_plan.py"
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
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/lifecycle.py",
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
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_policy.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-3",
      "title": "��ܲ������ռ�������CTAF ��5.2 / M1b��������ע��� 19 �12 MVP ӳ�� AgentCapability / CRYPTO_PROXY �� approved-product / 6 ��ܳ��� PLANNER..HUMAN_GATE����˫��������ö��ֵ / CTAF �淶�� / ��Ա��ͬ��Ŀ���ռ������Сд���� fail-closed����manifest-checker У���л���MVP δӳ��ܾ���CRYPTO_PROXY approved scope����ܳ�����ã���˫��һ�����������޹¶� / ��δӳ�� MVP����capability-closedset.md �ĵ� + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/capability.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "src/coevo/orchestrator/models.py",
        "docs/framework/capability-closedset.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_capability.py",
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_framework_validate_plan.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/capability.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
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
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/capability-closedset.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_capability.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
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
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-4",
      "title": "��ܲ� Memory ����CTAF ��6.2 / M3����MemoryRecord ͳһģ�ͣ�EPISODIC/SEMANTIC + �淶��ָ�ƣ���Episodic ���ͶӰ����̶��������Semantic ������ӳ�� knowledge_base ReviewDecisionKind.APPROVE��δ�����ܾ�����L12 �����ֶξ�ע�� Redactor ת `REDACTED:<sha256>` ժҪ�����Ĳ��õ��� store����ע�� store/����/Redactor �쳣 fail-closed��memory-interface.md + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/memory.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/memory-interface.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_memory.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/memory-interface.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_memory.py",
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

## 2026-08-07T17:07:12.809560Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```

## 2026-08-07T17:07:23.424233Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
_ref ���ΰ��ҹ�Կȡ��֤���� F8 / policy_version �� F7 / ʧ�ܲ�ע�� / �������������������� L15��+ `.agent` v1.0 wire �ֽڼ��ع� T6",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_agent_wire_regression.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-2",
      "title": "��ܲ� Policy ������ validate_plan��CTAF ��6.5 / M2����Policy �ֶ��� policy_version ���F7����4 Ĭ�� Profile��max_recover_attempts �� 3 ���� L16����EMERGENCY fail-fast��1 ������ / 60s / �º� 30 ����ȷ�� / ���ظ澯��F1+F9����L18 ��������tool_args ��ֵ�� schema ������F6����validate_plan ������� + L18 + L19��A9/F4����L19 ״̬����ESCALATED��ACTIVE ���뾭 HELD��RETIRED ֱ�ˣ�������������������������L15��+ L17 �ĵ�����",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/plan.py",
        "src/coevo/framework/lifecycle.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_policy.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py",
        "tests/unit/test_framework_validate_plan.py"
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
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/lifecycle.py",
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
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_policy.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-3",
      "title": "��ܲ������ռ�������CTAF ��5.2 / M1b��������ע��� 19 �12 MVP ӳ�� AgentCapability / CRYPTO_PROXY �� approved-product / 6 ��ܳ��� PLANNER..HUMAN_GATE����˫��������ö��ֵ / CTAF �淶�� / ��Ա��ͬ��Ŀ���ռ������Сд���� fail-closed����manifest-checker У���л���MVP δӳ��ܾ���CRYPTO_PROXY approved scope����ܳ�����ã���˫��һ�����������޹¶� / ��δӳ�� MVP����capability-closedset.md �ĵ� + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/capability.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "src/coevo/orchestrator/models.py",
        "docs/framework/capability-closedset.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_capability.py",
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_framework_validate_plan.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/capability.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
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
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/capability-closedset.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_capability.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
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
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-4",
      "title": "��ܲ� Memory ����CTAF ��6.2 / M3����MemoryRecord ͳһģ�ͣ�EPISODIC/SEMANTIC + �淶��ָ�ƣ���Episodic ���ͶӰ����̶��������Semantic ������ӳ�� knowledge_base ReviewDecisionKind.APPROVE��δ�����ܾ�����L12 �����ֶξ�ע�� Redactor ת `REDACTED:<sha256>` ժҪ�����Ĳ��õ��� store����ע�� store/����/Redactor �쳣 fail-closed��memory-interface.md + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/memory.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/memory-interface.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_memory.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/memory-interface.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_memory.py",
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

## 2026-08-07T17:07:30.149245Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```

## 2026-08-07T17:07:40.537921Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
_ref ���ΰ��ҹ�Կȡ��֤���� F8 / policy_version �� F7 / ʧ�ܲ�ע�� / �������������������� L15��+ `.agent` v1.0 wire �ֽڼ��ع� T6",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_agent_wire_regression.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-2",
      "title": "��ܲ� Policy ������ validate_plan��CTAF ��6.5 / M2����Policy �ֶ��� policy_version ���F7����4 Ĭ�� Profile��max_recover_attempts �� 3 ���� L16����EMERGENCY fail-fast��1 ������ / 60s / �º� 30 ����ȷ�� / ���ظ澯��F1+F9����L18 ��������tool_args ��ֵ�� schema ������F6����validate_plan ������� + L18 + L19��A9/F4����L19 ״̬����ESCALATED��ACTIVE ���뾭 HELD��RETIRED ֱ�ˣ�������������������������L15��+ L17 �ĵ�����",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/plan.py",
        "src/coevo/framework/lifecycle.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_policy.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py",
        "tests/unit/test_framework_validate_plan.py"
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
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/lifecycle.py",
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
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_policy.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-3",
      "title": "��ܲ������ռ�������CTAF ��5.2 / M1b��������ע��� 19 �12 MVP ӳ�� AgentCapability / CRYPTO_PROXY �� approved-product / 6 ��ܳ��� PLANNER..HUMAN_GATE����˫��������ö��ֵ / CTAF �淶�� / ��Ա��ͬ��Ŀ���ռ������Сд���� fail-closed����manifest-checker У���л���MVP δӳ��ܾ���CRYPTO_PROXY approved scope����ܳ�����ã���˫��һ�����������޹¶� / ��δӳ�� MVP����capability-closedset.md �ĵ� + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/capability.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "src/coevo/orchestrator/models.py",
        "docs/framework/capability-closedset.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_capability.py",
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_framework_validate_plan.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/capability.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
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
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/capability-closedset.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_capability.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
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
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-4",
      "title": "��ܲ� Memory ����CTAF ��6.2 / M3����MemoryRecord ͳһģ�ͣ�EPISODIC/SEMANTIC + �淶��ָ�ƣ���Episodic ���ͶӰ����̶��������Semantic ������ӳ�� knowledge_base ReviewDecisionKind.APPROVE��δ�����ܾ�����L12 �����ֶξ�ע�� Redactor ת `REDACTED:<sha256>` ժҪ�����Ĳ��õ��� store����ע�� store/����/Redactor �쳣 fail-closed��memory-interface.md + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/memory.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/memory-interface.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_memory.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/memory-interface.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_memory.py",
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

## 2026-08-07T17:09:45.594471Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```

## 2026-08-07T17:09:53.385791Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
_ref ���ΰ��ҹ�Կȡ��֤���� F8 / policy_version �� F7 / ʧ�ܲ�ע�� / �������������������� L15��+ `.agent` v1.0 wire �ֽڼ��ع� T6",
      "code": [
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_agent_wire_regression.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-2",
      "title": "��ܲ� Policy ������ validate_plan��CTAF ��6.5 / M2����Policy �ֶ��� policy_version ���F7����4 Ĭ�� Profile��max_recover_attempts �� 3 ���� L16����EMERGENCY fail-fast��1 ������ / 60s / �º� 30 ����ȷ�� / ���ظ澯��F1+F9����L18 ��������tool_args ��ֵ�� schema ������F6����validate_plan ������� + L18 + L19��A9/F4����L19 ״̬����ESCALATED��ACTIVE ���뾭 HELD��RETIRED ֱ�ˣ�������������������������L15��+ L17 �ĵ�����",
      "code": [
        "src/coevo/framework/policy.py",
        "src/coevo/framework/plan.py",
        "src/coevo/framework/lifecycle.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_policy.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py",
        "tests/unit/test_framework_validate_plan.py"
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
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/lifecycle.py",
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
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_policy.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-3",
      "title": "��ܲ������ռ�������CTAF ��5.2 / M1b��������ע��� 19 �12 MVP ӳ�� AgentCapability / CRYPTO_PROXY �� approved-product / 6 ��ܳ��� PLANNER..HUMAN_GATE����˫��������ö��ֵ / CTAF �淶�� / ��Ա��ͬ��Ŀ���ռ������Сд���� fail-closed����manifest-checker У���л���MVP δӳ��ܾ���CRYPTO_PROXY approved scope����ܳ�����ã���˫��һ�����������޹¶� / ��δӳ�� MVP����capability-closedset.md �ĵ� + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/capability.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "src/coevo/orchestrator/models.py",
        "docs/framework/capability-closedset.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_capability.py",
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_framework_validate_plan.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/capability.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
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
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/capability-closedset.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_capability.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
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
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-4",
      "title": "��ܲ� Memory ����CTAF ��6.2 / M3����MemoryRecord ͳһģ�ͣ�EPISODIC/SEMANTIC + �淶��ָ�ƣ���Episodic ���ͶӰ����̶��������Semantic ������ӳ�� knowledge_base ReviewDecisionKind.APPROVE��δ�����ܾ�����L12 �����ֶξ�ע�� Redactor ת `REDACTED:<sha256>` ժҪ�����Ĳ��õ��� store����ע�� store/����/Redactor �쳣 fail-closed��memory-interface.md + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/memory.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/memory-interface.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_memory.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/memory-interface.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_memory.py",
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

## 2026-08-07T17:13:40.721006Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `1`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\scripts\validate_opencode.py
PASS required: AGENTS.md
PASS required: opencode.jsonc
PASS required: Makefile
PASS required: docs/README.md
PASS required: loop/STATE.json
PASS required: loop/BACKLOG.yaml
PASS required: loop/VERIFICATION.md
PASS required: loop/tool-audit.jsonl
PASS required: .opencode/plugins/loop-guard.ts
PASS required: .opencode/tools/loop_state.ts
PASS required: .opencode/tools/quality_gate.ts
PASS required: .opencode/tools/traceability_check.ts
PASS required: tests/unit
PASS required: tests/integration
PASS required: tests/security
PASS required: tests/e2e
PASS denied: webfetch
PASS denied: websearch
PASS denied: external_directory
PASS bash defaults to ask
PASS bash denied: git push*
PASS bash denied: curl *
PASS bash denied: wget *
PASS bash denied: pip install*
PASS bash denied: npm install*
PASS current tool API: loop_state.ts
PASS current tool API: quality_gate.ts
PASS current tool API: traceability_check.ts
{"ok": true, "failures": []}
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe E:\Workspace\Coevo\.tools\control\control.pyz traceability_check
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "E:\Workspace\Coevo\.tools\control\control.pyz\__main__.py", line 18, in <module>
    runpy.run_module(name, run_name="__main__", alter_sys=True)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen runpy>", line 226, in run_module
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "E:\Workspace\Coevo\.tools\control\control.pyz\traceability_check.py", line 40, in <module>
    if __name__=="__main__": raise SystemExit(main())
                                              ~~~~^^
  File "E:\Workspace\Coevo\.tools\control\control.pyz\traceability_check.py", line 39, in main
    summary=check(args.story,not args.all_statuses); print(json.dumps(summary,ensure_ascii=False,indent=2)); return 0 if summary["checked"] and not summary["missing"] else 10
                                                     ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'gbk' codec can't encode character '\u2194' in position 159429: illegal multibyte sequence

```

## 2026-08-07T17:14:17.765941Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
ts/unit/test_framework_policy.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py",
        "tests/unit/test_framework_validate_plan.py"
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
          "path": "src/coevo/framework/plan.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/lifecycle.py",
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
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_policy.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_plan_l18.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_validate_plan.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-3",
      "title": "��ܲ������ռ�������CTAF ��5.2 / M1b��������ע��� 19 �12 MVP ӳ�� AgentCapability / CRYPTO_PROXY �� approved-product / 6 ��ܳ��� PLANNER..HUMAN_GATE����˫��������ö��ֵ / CTAF �淶�� / ��Ա��ͬ��Ŀ���ռ������Сд���� fail-closed����manifest-checker У���л���MVP δӳ��ܾ���CRYPTO_PROXY approved scope����ܳ�����ã���˫��һ�����������޹¶� / ��δӳ�� MVP����capability-closedset.md �ĵ� + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/capability.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "src/coevo/orchestrator/models.py",
        "docs/framework/capability-closedset.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_capability.py",
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_framework_validate_plan.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/capability.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
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
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/capability-closedset.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_capability.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
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
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-4",
      "title": "��ܲ� Memory ����CTAF ��6.2 / M3����MemoryRecord ͳһģ�ͣ�EPISODIC/SEMANTIC + �淶��ָ�ƣ���Episodic ���ͶӰ����̶��������Semantic ������ӳ�� knowledge_base ReviewDecisionKind.APPROVE��δ�����ܾ�����L12 �����ֶξ�ע�� Redactor ת `REDACTED:<sha256>` ժҪ�����Ĳ��õ��� store����ע�� store/����/Redactor �쳣 fail-closed��memory-interface.md + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/memory.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/memory-interface.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_memory.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/memory-interface.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_memory.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-5",
      "title": "��ܲ� Tool ������ MCP schema ·�� A��CTAF ��6.3 / ��7.2 / M4����Tool ͳһģ�ͣ�tool_id safe-id / tool_version P2 ���� semver / side_effects �ռ� / requires_consent / timeout_sec �ϸ������� / size_in_bytes_max �ϸ�Ǹ����� / crypto_scope ProviderScope �ռ� / audit_required / input/output schema��������ע�����У��ע����롢�ظ��ܾ������� 128����Tool<->MCP ����˫��ת����name/description/inputSchema/outputSchema + x-coevo ��չ�飬�Ӽ������ֽڼ�һ�£�ȱʧ��չ��/δ֪��������չ����ʽ�ܾ�����JSON Schema �Ӽ�У�飨type/properties/required/items/enum/description ��������object �ش� properties��required Ϊ properties �Ӽ���array �ش� items��enum �ǿա�64��δ֪�ؼ���/���>16/��С>16KiB �ܾ���fail-closed�������������� stdlib���� MCP SDK��L15��+ L17 �ĵ�������tool-registry.md��",
      "code": [
        "src/coevo/framework/tools.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/tool-registry.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_tools.py",
        "tests/unit/test_module_docs.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/tool-registry.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_tools.py",
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

## 2026-08-08 — US-16-AC-6 增量门禁与安全/协议审查记录（主仓库，豁免全量 quality）
- target=`test (定向)` exit_code=`0`
```text
python -m unittest tests.unit.test_framework_a2a tests.unit.test_framework_manifest_checker
  tests.unit.test_framework_capability tests.unit.test_framework_tools
  tests.unit.test_framework_memory tests.unit.test_framework_policy
  tests.unit.test_framework_plan_l18 tests.unit.test_framework_lifecycle
  tests.unit.test_framework_validate_plan tests.unit.test_agent_wire_regression
  tests.unit.test_module_docs
Ran 126 tests; OK（AC-6.1..6.5 全部断言 + 框架族相邻回归 + wire T6 + L17 文档守卫）
```
- target=`fmt` exit_code=`0` fingerprint=`fe39766e2048d2bc`（2026-08-08）
- target=`lint` exit_code=`0` fingerprint=`252ad24e526f6728`（audit fully-sealed）
- security-review（只读沙箱 ac6-sec，pin=`28c26ac`）：check ok violations=[]；
  沙箱内定向 45 项 OK（a2a + manifest_checker + wire 回归）；
  判定 PASS：Critical/High 0，Low 2——① manifest_spec_hash 深度嵌套 RecursionError
  未收敛（verify_policy_ref 非 fail-closed）；② policy_ref.signature 无长度上限；
  均就地修复于 `6ed67b0`（SIGNATURE_MAX_HEX_LEN=1024 + 深度异常拒绝 + 2 项负例测试）
- protocol-review（只读沙箱 ac6-proto，pin=`28c26ac`）：check ok violations=[]；
  沙箱内 13 项 OK（a2a + wire 回归）；判定 PASS：A2A 仅为 `.agent` v1.0 payload 层
  约定、信封字节 T6 不变、字段映射无信息丢失/语义漂移、policy_ref 验签数据
  （spec_hash|fingerprint）与规范化一致、无需主版本升级；观察项 1（a2a.py 引用
  manifest_checker 私有符号 _InvalidManifest，同包内可接受）
- 治理偏差：子代理并发额度受限（agent thread limit reached），审查由编排者按只读
  契约在钉扎沙箱内实际执行（只读、零违规、证据为沙箱内命令输出）；沙箱已 discard
- 全量 `make quality` 按用户指示本轮豁免，留待后续回归

## 2026-08-07T17:37:52.136546Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
vo/framework/capability.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "src/coevo/orchestrator/models.py",
        "docs/framework/capability-closedset.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_capability.py",
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_framework_validate_plan.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/capability.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
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
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/capability-closedset.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_capability.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
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
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-4",
      "title": "��ܲ� Memory ����CTAF ��6.2 / M3����MemoryRecord ͳһģ�ͣ�EPISODIC/SEMANTIC + �淶��ָ�ƣ���Episodic ���ͶӰ����̶��������Semantic ������ӳ�� knowledge_base ReviewDecisionKind.APPROVE��δ�����ܾ�����L12 �����ֶξ�ע�� Redactor ת `REDACTED:<sha256>` ժҪ�����Ĳ��õ��� store����ע�� store/����/Redactor �쳣 fail-closed��memory-interface.md + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/memory.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/memory-interface.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_memory.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/memory-interface.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_memory.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-5",
      "title": "��ܲ� Tool ������ MCP schema ·�� A��CTAF ��6.3 / ��7.2 / M4����Tool ͳһģ�ͣ�tool_id safe-id / tool_version P2 ���� semver / side_effects �ռ� / requires_consent / timeout_sec �ϸ������� / size_in_bytes_max �ϸ�Ǹ����� / crypto_scope ProviderScope �ռ� / audit_required / input/output schema��������ע�����У��ע����롢�ظ��ܾ������� 128����Tool<->MCP ����˫��ת����name/description/inputSchema/outputSchema + x-coevo ��չ�飬�Ӽ������ֽڼ�һ�£�ȱʧ��չ��/δ֪��������չ����ʽ�ܾ�����JSON Schema �Ӽ�У�飨type/properties/required/items/enum/description ��������object �ش� properties��required Ϊ properties �Ӽ���array �ش� items��enum �ǿա�64��δ֪�ؼ���/���>16/��С>16KiB �ܾ���fail-closed�������������� stdlib���� MCP SDK��L15��+ L17 �ĵ�������tool-registry.md��",
      "code": [
        "src/coevo/framework/tools.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/tool-registry.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_tools.py",
        "tests/unit/test_module_docs.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/tool-registry.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_tools.py",
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
      "ac": "AC-6",
      "title": "��ܲ� A2A wire 0.1 �� policy_ref ���ΰ󶨣�CTAF ��7.3 / M5����A2A ��Ϣģ��ȫ�ֶ�У�� fail-closed��AC-6.1���� signature �������� 1024 hex����policy_ref ���ΰ󶨣�spec_hash �ų���ָ�ֶ� / ֤���� DER ָ�� / SM2 ��ǩ��Կȡ��֤�������� ��7.3.3 �岽ʱ����֤��ע���쳣����� manifest ��Ⱦ� fail-closed��AC-6.2����A2A<->`.agent` �ֶ�ӳ������һ���� `.agent` v1.0 wire �ֽڲ��䣨T6 �ػ���AC-6.3����ҵ���غ� >64KiB ���� RESULT_SUBMISSION+payload_ref ��֣�AC-6.4�������������� stdlib + ���ͶӰ + L17 �ĵ�������AC-6.5��a2a-protocol.md��",
      "code": [
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/a2a-protocol.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_a2a.py",
        "tests/unit/test_agent_wire_regression.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/a2a-protocol.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_a2a.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
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

## 2026-08-07T17:39:39.625304Z — target=`fmt` fingerprint=`fe39766e2048d2bc`
- exit_code: `0`
```text
preflight audit seal: fully-sealed
$ E:\Workspace\Coevo\.tools\python\3.14.3\python.exe -m compileall -q -f scripts src tests
audit seal: fully-sealed

```

## 2026-08-07T17:39:46.952153Z — target=`lint` fingerprint=`252ad24e526f6728`
- exit_code: `0`
```text
vo/framework/capability.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/validation.py",
        "src/coevo/framework/__init__.py",
        "src/coevo/orchestrator/models.py",
        "docs/framework/capability-closedset.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_capability.py",
        "tests/unit/test_framework_manifest_checker.py",
        "tests/unit/test_framework_validate_plan.py",
        "tests/unit/test_framework_plan_l18.py",
        "tests/unit/test_framework_lifecycle.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/capability.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
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
          "path": "src/coevo/orchestrator/models.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/capability-closedset.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_capability.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_manifest_checker.py",
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
          "path": "tests/unit/test_framework_lifecycle.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-4",
      "title": "��ܲ� Memory ����CTAF ��6.2 / M3����MemoryRecord ͳһģ�ͣ�EPISODIC/SEMANTIC + �淶��ָ�ƣ���Episodic ���ͶӰ����̶��������Semantic ������ӳ�� knowledge_base ReviewDecisionKind.APPROVE��δ�����ܾ�����L12 �����ֶξ�ע�� Redactor ת `REDACTED:<sha256>` ժҪ�����Ĳ��õ��� store����ע�� store/����/Redactor �쳣 fail-closed��memory-interface.md + L15 stdlib / L17 �ĵ�����",
      "code": [
        "src/coevo/framework/memory.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/memory-interface.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_memory.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/memory.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/memory-interface.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_memory.py",
          "exists": true
        }
      ],
      "kind": "covered"
    },
    {
      "story": "US-16",
      "ac": "AC-5",
      "title": "��ܲ� Tool ������ MCP schema ·�� A��CTAF ��6.3 / ��7.2 / M4����Tool ͳһģ�ͣ�tool_id safe-id / tool_version P2 ���� semver / side_effects �ռ� / requires_consent / timeout_sec �ϸ������� / size_in_bytes_max �ϸ�Ǹ����� / crypto_scope ProviderScope �ռ� / audit_required / input/output schema��������ע�����У��ע����롢�ظ��ܾ������� 128����Tool<->MCP ����˫��ת����name/description/inputSchema/outputSchema + x-coevo ��չ�飬�Ӽ������ֽڼ�һ�£�ȱʧ��չ��/δ֪��������չ����ʽ�ܾ�����JSON Schema �Ӽ�У�飨type/properties/required/items/enum/description ��������object �ش� properties��required Ϊ properties �Ӽ���array �ش� items��enum �ǿա�64��δ֪�ؼ���/���>16/��С>16KiB �ܾ���fail-closed�������������� stdlib���� MCP SDK��L15��+ L17 �ĵ�������tool-registry.md��",
      "code": [
        "src/coevo/framework/tools.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/tool-registry.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_tools.py",
        "tests/unit/test_module_docs.py"
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
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/tool-registry.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_tools.py",
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
      "ac": "AC-6",
      "title": "��ܲ� A2A wire 0.1 �� policy_ref ���ΰ󶨣�CTAF ��7.3 / M5����A2A ��Ϣģ��ȫ�ֶ�У�� fail-closed��AC-6.1���� signature �������� 1024 hex����policy_ref ���ΰ󶨣�spec_hash �ų���ָ�ֶ� / ֤���� DER ָ�� / SM2 ��ǩ��Կȡ��֤�������� ��7.3.3 �岽ʱ����֤��ע���쳣����� manifest ��Ⱦ� fail-closed��AC-6.2����A2A<->`.agent` �ֶ�ӳ������һ���� `.agent` v1.0 wire �ֽڲ��䣨T6 �ػ���AC-6.3����ҵ���غ� >64KiB ���� RESULT_SUBMISSION+payload_ref ��֣�AC-6.4�������������� stdlib + ���ͶӰ + L17 �ĵ�������AC-6.5��a2a-protocol.md��",
      "code": [
        "src/coevo/framework/a2a.py",
        "src/coevo/framework/manifest_checker.py",
        "src/coevo/framework/__init__.py",
        "docs/framework/a2a-protocol.md",
        "docs/modules/framework.md"
      ],
      "tests": [
        "tests/unit/test_framework_a2a.py",
        "tests/unit/test_agent_wire_regression.py",
        "tests/unit/test_module_docs.py"
      ],
      "status": "done",
      "evidence": [
        {
          "kind": "code",
          "path": "src/coevo/framework/a2a.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/manifest_checker.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "src/coevo/framework/__init__.py",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/framework/a2a-protocol.md",
          "exists": true
        },
        {
          "kind": "code",
          "path": "docs/modules/framework.md",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_framework_a2a.py",
          "exists": true
        },
        {
          "kind": "test",
          "path": "tests/unit/test_agent_wire_regression.py",
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
