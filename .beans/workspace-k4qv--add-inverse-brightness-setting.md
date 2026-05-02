---
# workspace-k4qv
title: Add inverse brightness setting
status: completed
type: feature
priority: normal
created_at: 2026-05-02T10:35:01Z
updated_at: 2026-05-02T13:04:02Z
---

Add inverse_brightness setting that flips normal adaptive brightness across the configured min/max brightness range while leaving sleep_brightness unchanged.\n\n- [x] Add tests for inverse brightness behavior before implementation\n- [x] Implement config, calculation, switch, and simulator support\n- [x] Update docs and generated strings\n- [x] Validate focused tests and checks\n- [x] Adversarially test behavior gaps\n- [x] Reassess architecture/docs and record summary\n- [x] Commit completed change with bean updates

## Summary of Changes\n\nAdded inverse_brightness through the existing Adaptive Lighting configuration pipeline. The option is validated with the other runtime-changeable settings, passed into SunLightSettings, exposed through change_switch_settings, documented in generated README/docs tables, added to strings/en translations, and available in the simulator. The brightness inversion is applied after the selected normal brightness curve is calculated and before returning non-sleep brightness, so sleep_brightness remains unchanged.\n\n## Architecture Reassessment\n\nNo new architecture document is needed. The change preserves the existing settings ownership boundary: const.py defines the option/schema/docs, switch.py transports config into SunLightSettings, color_and_brightness.py owns the calculation, generated docs/strings mirror const.py/services.yaml, and the simulator has a matching input.
