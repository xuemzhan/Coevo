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
