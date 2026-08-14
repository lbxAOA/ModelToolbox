import 'dart:io';

import 'bridge_process.dart';

BridgeTransport defaultBridgeTransport() {
  final executable = Platform.environment['MODELTOOLBOX_PYTHON'];
  final root = Platform.environment['MODELTOOLBOX_ROOT'];
  if (executable == null || executable.trim().isEmpty || root == null || root.trim().isEmpty) {
    return const UnavailableBridgeTransport();
  }
  final entrypoint = File('$root${Platform.pathSeparator}cli${Platform.pathSeparator}main.py');
  if (!File(executable).existsSync() || !entrypoint.existsSync()) {
    return const UnavailableBridgeTransport();
  }
  return ProcessBridgeTransport(executable, [entrypoint.path, 'bridge', '--protocol', 'mtb.bridge/1']);
}

class UnavailableBridgeTransport implements BridgeTransport {
  const UnavailableBridgeTransport();

  @override
  Future<void> close() async {}

  @override
  Future<Object?> request(String operation, Map<String, Object?> payload) async {
    throw const BridgeStartupConfigurationError();
  }

  @override
  Future<void> start() async {
    throw const BridgeStartupConfigurationError();
  }
}

class BridgeStartupConfigurationError implements Exception {
  const BridgeStartupConfigurationError();
}
