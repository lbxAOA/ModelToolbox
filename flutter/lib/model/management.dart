class IntegrationSummary {
  const IntegrationSummary({required this.id, required this.name, required this.contractStatus, required this.writeEnabled, required this.mcpSupported, required this.skillsSupported, required this.message, required this.configStatus});
  final String id;
  final String name;
  final String contractStatus;
  final bool writeEnabled;
  final bool mcpSupported;
  final bool skillsSupported;
  final String message;
  final String configStatus;
  factory IntegrationSummary.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['id'] is! String || source['name'] is! String || source['contract_status'] is! String || source['write_enabled'] is! bool || source['mcp_supported'] is! bool || source['skills_supported'] is! bool || source['message'] is! String || source['config_status'] is! String) throw const FormatException('Integration data is invalid.');
    return IntegrationSummary(id: source['id']! as String, name: source['name']! as String, contractStatus: source['contract_status']! as String, writeEnabled: source['write_enabled']! as bool, mcpSupported: source['mcp_supported']! as bool, skillsSupported: source['skills_supported']! as bool, message: source['message']! as String, configStatus: source['config_status']! as String);
  }
}

class MarketplaceItem {
  const MarketplaceItem({required this.id, required this.kind, required this.name, required this.version, required this.description, required this.source, required this.trust, required this.riskLevel, required this.compatibleAdapters, required this.tags, required this.installable});
  final String id;
  final String kind;
  final String name;
  final String version;
  final String description;
  final String source;
  final String trust;
  final String riskLevel;
  final List<String> compatibleAdapters;
  final List<String> tags;
  final bool installable;
  factory MarketplaceItem.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['id'] is! String || source['kind'] is! String || source['name'] is! String || source['version'] is! String || source['description'] is! String || source['source'] is! String || source['trust'] is! String || source['risk_level'] is! String || source['compatible_adapters'] is! List<Object?> || source['tags'] is! List<Object?> || source['installable'] is! bool) throw const FormatException('Marketplace item is invalid.');
    final adapters = source['compatible_adapters']! as List<Object?>;
    final tags = source['tags']! as List<Object?>;
    if (adapters.any((value) => value is! String) || tags.any((value) => value is! String)) throw const FormatException('Marketplace item is invalid.');
    return MarketplaceItem(id: source['id']! as String, kind: source['kind']! as String, name: source['name']! as String, version: source['version']! as String, description: source['description']! as String, source: source['source']! as String, trust: source['trust']! as String, riskLevel: source['risk_level']! as String, compatibleAdapters: adapters.cast<String>(), tags: tags.cast<String>(), installable: source['installable']! as bool);
  }
}

class MarketplaceStatus {
  const MarketplaceStatus({required this.onlineEnabled, required this.catalogItems, required this.message});
  final bool onlineEnabled;
  final int catalogItems;
  final String message;
  factory MarketplaceStatus.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['online_enabled'] is! bool || source['catalog_items'] is! int || source['message'] is! String) throw const FormatException('Marketplace status is invalid.');
    return MarketplaceStatus(onlineEnabled: source['online_enabled']! as bool, catalogItems: source['catalog_items']! as int, message: source['message']! as String);
  }
}
