import 'dart:convert';

class StateEntry {
  const StateEntry({
    required this.key,
    required this.value,
    required this.valueType,
  });

  final String key;
  final Object? value;
  final String valueType;

  factory StateEntry.fromJson(Object? source) {
    if (source is! Map<Object?, Object?>) {
      throw const FormatException('State entry must be an object.');
    }
    final key = source['key'];
    final valueType = source['value_type'];
    if (key is! String || valueType is! String) {
      throw const FormatException('State entry is incomplete.');
    }
    return StateEntry(key: key, value: source['value'], valueType: valueType);
  }

  String get displayValue => jsonEncode(value);
}

class WorkbenchSection {
  const WorkbenchSection({
    required this.key,
    required this.title,
    required this.status,
    required this.message,
  });

  final String key;
  final String title;
  final String status;
  final String message;

  factory WorkbenchSection.fromJson(Object? source) {
    if (source is! Map<Object?, Object?>) {
      throw const FormatException('Workbench section must be an object.');
    }
    final key = source['key'];
    final title = source['title'];
    final status = source['status'];
    final message = source['message'];
    if (key is! String || title is! String || status is! String || message is! String) {
      throw const FormatException('Workbench section is incomplete.');
    }
    return WorkbenchSection(key: key, title: title, status: status, message: message);
  }
}

class ViewSnapshot {
  const ViewSnapshot({required this.version, required this.entries, required this.sections});

  final String version;
  final List<StateEntry> entries;
  final List<WorkbenchSection> sections;

  factory ViewSnapshot.fromJson(Object? source) {
    if (source is! Map<Object?, Object?>) {
      throw const FormatException('Snapshot must be an object.');
    }
    final version = source['version'];
    final entries = source['state_entries'];
    final workbench = source['workbench'];
    if (version is! String || entries is! List<Object?>) {
      throw const FormatException('Snapshot is incomplete.');
    }
    final sections = workbench is Map<Object?, Object?> && workbench['sections'] is List<Object?>
        ? (workbench['sections'] as List<Object?>).map(WorkbenchSection.fromJson).toList(growable: false)
        : const <WorkbenchSection>[];
    return ViewSnapshot(
      version: version,
      entries: entries.map(StateEntry.fromJson).toList(growable: false),
      sections: sections,
    );
  }
}
