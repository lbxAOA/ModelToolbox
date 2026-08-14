import 'package:flutter/foundation.dart';

import '../bridge/bridge_client.dart';
import '../bridge/bridge_error.dart';
import '../model/view_snapshot.dart';

enum WorkbenchPhase { loading, ready, unavailable, error }

class AppController extends ChangeNotifier {
  AppController(this._bridge);

  final BridgeClient _bridge;
  WorkbenchPhase _phase = WorkbenchPhase.loading;
  ViewSnapshot? _snapshot;
  String? _message;
  int _selectedNavigation = 0;

  WorkbenchPhase get phase => _phase;
  ViewSnapshot? get snapshot => _snapshot;
  String? get message => _message;
  int get selectedNavigation => _selectedNavigation;

  Future<void> start() => refresh(initial: true);

  Future<void> refresh({bool initial = false}) async {
    _phase = WorkbenchPhase.loading;
    _message = null;
    notifyListeners();
    try {
      _snapshot = initial ? await _bridge.snapshot() : await _bridge.refresh();
      _phase = WorkbenchPhase.ready;
    } on BridgeError catch (error) {
      _phase = error.code == 'runtime-unavailable' ? WorkbenchPhase.unavailable : WorkbenchPhase.error;
      _message = error.message;
    } on FormatException {
      _phase = WorkbenchPhase.error;
      _message = 'The local bridge returned an unsupported data format.';
    } catch (_) {
      _phase = WorkbenchPhase.unavailable;
      _message = 'The local ModelToolbox runtime is not configured.';
    }
    notifyListeners();
  }

  void selectNavigation(int value) {
    _selectedNavigation = value;
    notifyListeners();
  }

  @override
  void dispose() {
    _bridge.close();
    super.dispose();
  }
}
