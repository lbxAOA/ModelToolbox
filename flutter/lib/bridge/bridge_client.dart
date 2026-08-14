import 'bridge_process.dart';
import '../model/view_snapshot.dart';

class BridgeClient {
  BridgeClient(this._transport);

  final BridgeTransport _transport;

  Future<ViewSnapshot> snapshot() async {
    final data = await _transport.request('view.snapshot', const {});
    return ViewSnapshot.fromJson(data);
  }

  Future<ViewSnapshot> refresh() async {
    final data = await _transport.request('view.refresh', const {});
    return ViewSnapshot.fromJson(data);
  }

  Future<void> close() => _transport.close();
}
