import 'package:flutter_test/flutter_test.dart';

import '../lib/model/management.dart';

void main() {
  test('decodes a trusted marketplace item', () {
    final item = MarketplaceItem.fromJson({
      'id': 'trusted:tools',
      'kind': 'mcp',
      'name': 'Tools',
      'version': '1.0.0',
      'description': 'A validated package.',
      'source': 'trusted',
      'trust': 'trusted',
      'risk_level': 'medium',
      'compatible_adapters': ['claude-code'],
      'tags': ['tools'],
      'installable': true,
    });

    expect(item.id, 'trusted:tools');
    expect(item.compatibleAdapters, ['claude-code']);
  });

  test('rejects malformed marketplace data', () {
    expect(() => MarketplaceItem.fromJson({'id': 'missing-fields'}), throwsFormatException);
  });
}
