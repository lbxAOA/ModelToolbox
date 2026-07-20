# kicad-mcp-pro 工具映射（常用）

> 工具名前缀 `mcp__kicad-mcp-pro__`。先 `kicad_set_project`，再操作。

## 项目 / 概览
- `kicad_get_version`、`kicad_get_server_info`、`kicad_get_project_info`
- `kicad_set_project`、`kicad_list_recent_projects`、`kicad_scan_directory`
- `pcb_get_board_summary`、`pcb_get_layers`、`pcb_get_stackup`、`pcb_get_nets`
- `project_design_report`、`project_quality_gate`

## 校验（ERC / DRC / DFM）
- `run_erc`、`run_drc`、`validate_design`、`validate_footprints_vs_schematic`
- `get_unconnected_nets`、`get_courtyard_violations`、`get_silk_to_pad_violations`
- `drc_list_rules`、`drc_add_exclusion`、`drc_list_exclusions`
- `dfm_run_manufacturer_check`、`dfm_calculate_manufacturing_cost`
- `pcb_quality_gate`、`pcb_placement_quality_report`

## 制造导出
- 铜层/钻孔：`export_gerber`、`export_drill`、`export_ipc2581`、`export_odb`
- 装配：`export_bom`、`export_pick_and_place`、`export_ipc_d356`
- 3D：`export_step` / `export_3d_step`、`export_glb`、`export_stl`、`export_vrml`
- 文档：`export_pcb_pdf`、`export_sch_pdf`、`export_svg`、`pcb_export_3d_pdf`

## 信号完整性 / 电源（进阶）
- `si_calculate_trace_impedance`、`si_calculate_trace_width_for_impedance`
- `si_check_differential_pair_skew`、`si_validate_length_matching`、`si_generate_stackup`
- `pdn_calculate_voltage_drop`、`pdn_recommend_decoupling_caps`、`check_power_integrity`
- `emc_run_full_compliance`、`emc_check_return_path_continuity`

## 原理图查询
- `sch_get_symbols`、`sch_get_net_names`、`sch_trace_net`、`sch_check_power_flags`
- `schematic_quality_gate`

## 库 / 元件
- `lib_search_components`、`lib_get_component_details`、`lib_get_bom_with_pricing`
- `lib_check_stock_availability`、`lib_find_alternative_parts`、`lib_recommend_part`

> 用 `kicad_list_tool_categories` / `kicad_get_tools_in_category` 浏览完整工具集。
