import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'bridge_error.dart';
import 'bridge_protocol.dart';

abstract class BridgeTransport {
  Future<void> start();
  Future<Object?> request(String operation, Map<String, Object?> payload);
  Future<void> close();
}

class ProcessBridgeTransport implements BridgeTransport {
  ProcessBridgeTransport(this._executable, this._arguments, {this.timeout = const Duration(seconds: 5)});

  final String _executable;
  final List<String> _arguments;
  final Duration timeout;
  Process? _process;
  StreamIterator<String>? _responses;
  Future<void> _pending = Future<void>.value();
  int _sequence = 0;

  @override
  Future<void> start() async {
    if (_process != null) return;
    try {
      final process = await Process.start(_executable, _arguments, runInShell: false);
      _process = process;
      _responses = StreamIterator(
        process.stdout.transform(utf8.decoder).transform(const LineSplitter()),
      );
    } on ProcessException {
      throw const BridgeError('runtime-unavailable', 'The local ModelToolbox runtime could not be started.');
    }
  }

  @override
  Future<Object?> request(String operation, Map<String, Object?> payload) {
    final completion = Completer<Object?>();
    _pending = _pending.then((_) async {
      try {
        completion.complete(await _requestOnce(operation, payload));
      } catch (error, stackTrace) {
        await _reset();
        completion.completeError(error, stackTrace);
      }
    });
    return completion.future;
  }

  Future<Object?> _requestOnce(String operation, Map<String, Object?> payload) async {
    await start();
    final process = _process;
    final responses = _responses;
    if (process == null || responses == null) {
      throw const BridgeError('bridge-terminated', 'The local bridge is unavailable.');
    }
    final requestId = 'flutter-${++_sequence}';
    process.stdin.writeln(encodeRequest(requestId: requestId, operation: operation, payload: payload));
    await process.stdin.flush();
    try {
      final hasResponse = await responses.moveNext().timeout(timeout);
      if (!hasResponse) {
        throw const BridgeError('bridge-terminated', 'The local bridge stopped before responding.');
      }
      final line = responses.current;
      if (utf8.encode(line).length > 1024 * 1024) {
        throw const BridgeError('response-too-large', 'The local bridge response is too large.');
      }
      return decodeResponse(line, requestId);
    } on TimeoutException {
      throw const BridgeError('bridge-timeout', 'The local bridge did not respond in time.');
    }
  }

  Future<void> _reset() async {
    final process = _process;
    _process = null;
    await _responses?.cancel();
    _responses = null;
    if (process == null) return;
    process.kill();
    await process.exitCode.timeout(const Duration(seconds: 1), onTimeout: () => -1);
  }

  @override
  Future<void> close() async {
    final process = _process;
    _process = null;
    await _responses?.cancel();
    _responses = null;
    if (process == null) return;
    await process.stdin.close();
    final exited = await process.exitCode.timeout(const Duration(seconds: 2), onTimeout: () => -1);
    if (exited == -1) process.kill();
  }
}
