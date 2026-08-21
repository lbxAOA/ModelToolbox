import 'package:flutter/foundation.dart';

import '../bridge/bridge_client.dart';
import '../bridge/bridge_error.dart';
import '../model/profile.dart';
import '../model/management.dart';
import '../model/view_snapshot.dart';

enum WorkbenchPhase { loading, ready, unavailable, error }

class AppController extends ChangeNotifier {
  AppController(this._bridge);
  final BridgeClient _bridge;
  WorkbenchPhase _phase = WorkbenchPhase.loading;
  ViewSnapshot? _snapshot;
  ProfileList _profiles = const ProfileList(selectedProfileId: null, profiles: []);
  AdapterList _adapters = const AdapterList(adapters: []);
  ProfilePlan? _plan;
  RouterStatus? _router;
  RouterPlan? _routerPlan;
  ListenerStatus? _listener;
  List<RouterActivity> _activity = const [];
  List<IntegrationSummary> _integrations = const [];
  MarketplaceStatus? _marketplaceStatus;
  List<MarketplaceItem> _recommendations = const [];
  String? _message;
  int _selectedNavigation = 0;
  WorkbenchPhase get phase => _phase;
  ViewSnapshot? get snapshot => _snapshot;
  ProfileList get profiles => _profiles;
  AdapterList get adapters => _adapters;
  ProfilePlan? get plan => _plan;
  RouterStatus? get router => _router;
  RouterPlan? get routerPlan => _routerPlan;
  ListenerStatus? get listener => _listener;
  List<RouterActivity> get activity => _activity;
  List<IntegrationSummary> get integrations => _integrations;
  MarketplaceStatus? get marketplaceStatus => _marketplaceStatus;
  List<MarketplaceItem> get recommendations => _recommendations;
  String? get message => _message;
  int get selectedNavigation => _selectedNavigation;
  Future<void> start() => refresh(initial: true);

  Future<void> refresh({bool initial = false}) async {
    _phase = WorkbenchPhase.loading; _message = null; notifyListeners();
    try {
      final results = await Future.wait<Object>([initial ? _bridge.snapshot() : _bridge.refresh(), _bridge.profiles(), _bridge.profileAdapters(), _bridge.routerStatus(), _bridge.listenerStatus(), _bridge.activity(), _bridge.integrations(), _bridge.marketplaceStatus(), _bridge.marketplaceRecommendations()]);
      _snapshot = results[0] as ViewSnapshot; _profiles = results[1] as ProfileList; _adapters = results[2] as AdapterList;
      _router = results[3] as RouterStatus; _listener = results[4] as ListenerStatus; _activity = results[5] as List<RouterActivity>; _integrations = results[6] as List<IntegrationSummary>; _marketplaceStatus = results[7] as MarketplaceStatus; _recommendations = results[8] as List<MarketplaceItem>;
      _plan = null; _routerPlan = null; _phase = WorkbenchPhase.ready;
    } on BridgeError catch (error) { _phase = error.code == 'runtime-unavailable' ? WorkbenchPhase.unavailable : WorkbenchPhase.error; _message = error.message;
    } on FormatException { _phase = WorkbenchPhase.error; _message = 'The local bridge returned an unsupported data format.';
    } catch (_) { _phase = WorkbenchPhase.unavailable; _message = 'The local ModelToolbox runtime is not configured.'; }
    notifyListeners();
  }

  Future<void> _action(Future<void> Function() operation) async {
    try { await operation(); _message = null; await refresh(); } on BridgeError catch (error) { _message = error.message; notifyListeners(); }
  }
  Future<void> selectProfile(String profileId) async { try { final selected = await _bridge.selectProfile(profileId); _profiles = ProfileList(selectedProfileId: selected.id, profiles: _profiles.profiles.map((item) => ProfileSummary(id: item.id, name: item.name, adapterId: item.adapterId, adapterName: item.adapterName, adapterAvailable: item.adapterAvailable, adapterMessage: item.adapterMessage, baseUrl: item.baseUrl, model: item.model, selected: item.id == selected.id)).toList(growable: false)); _message = 'Selected ${selected.name}. No external configuration changed.'; } on BridgeError catch (error) { _message = error.message; } notifyListeners(); }
  Future<void> createProfile(ProfileInput input) => _action(() async { await _bridge.createProfile(input); });
  Future<void> updateProfile(ProfileInput input) => _action(() async { await _bridge.updateProfile(input); });
  Future<void> deleteProfile(String id) => _action(() async { await _bridge.deleteProfile(id); });
  Future<void> previewProfile(String profileId) async { try { _plan = await _bridge.planProfile(profileId); _message = null; } on BridgeError catch (error) { _plan = null; _message = error.message; } notifyListeners(); }
  Future<void> applyProfile() async { final plan = _plan; if (plan == null) return; await _action(() async { await _bridge.applyProfile(plan); }); }
  Future<void> previewRouter(String profileId) async { try { _routerPlan = await _bridge.planRouter(profileId, 'anthropic', 'openai'); _message = null; } on BridgeError catch (error) { _routerPlan = null; _message = error.message; } notifyListeners(); }
  Future<void> activateRouter() async { final plan = _routerPlan; if (plan == null) return; final id = plan.proposed['profile_id']; if (id is! String) return; await _action(() async { await _bridge.activateRouter(id, 'anthropic', 'openai', plan.revision); }); }
  Future<void> directRouter() async { final router = _router; if (router != null) await _action(() async { await _bridge.directRouter(router.revision); }); }
  Future<void> rollbackRouter() async { final router = _router; if (router != null) await _action(() async { await _bridge.rollbackRouter(router.revision); }); }
  Future<void> toggleListener() async { if (_listener?.running == true) { await _action(() async { await _bridge.stopListener(); }); } else { await _action(() async { await _bridge.startListener(); }); } }
  void selectNavigation(int value) { _selectedNavigation = value; notifyListeners(); }
  @override void dispose() { _bridge.close(); super.dispose(); }
}
