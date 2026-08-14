import 'dart:convert';

import 'bridge_error.dart';

const bridgeProtocol = 'mtb.bridge/1';

String encodeRequest({
  required String requestId,
  required String operation,
  Map<String, Object?> payload = const {},
}) {
  return jsonEncode({
    'protocol': bridgeProtocol,
    'request_id': requestId,
    'operation': operation,
    'payload': payload,
  });
}

Object? decodeResponse(String line, String expectedRequestId) {
  final decoded = jsonDecode(line);
  if (decoded is! Map<Object?, Object?> ||
      decoded['protocol'] != bridgeProtocol ||
      decoded['request_id'] != expectedRequestId ||
      decoded['ok'] is! bool) {
    throw const BridgeError('invalid-response', 'The local bridge returned an invalid response.');
  }
  if (decoded['ok'] == false) {
    final error = decoded['error'];
    if (error is Map<Object?, Object?> && error['code'] is String && error['message'] is String) {
      throw BridgeError(error['code']! as String, error['message']! as String);
    }
    throw const BridgeError('bridge-failure', 'The local bridge rejected the request.');
  }
  return decoded['data'];
}
