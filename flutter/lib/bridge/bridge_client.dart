import 'bridge_error.dart';
import 'bridge_process.dart';
import '../model/profile.dart';
import '../model/management.dart';
import '../model/view_snapshot.dart';

class BridgeClient {
  BridgeClient(this._transport);
  final BridgeTransport _transport;
  Future<ViewSnapshot> snapshot() async => ViewSnapshot.fromJson(await _transport.request('view.snapshot', const {}));
  Future<ViewSnapshot> refresh() async => ViewSnapshot.fromJson(await _transport.request('view.refresh', const {}));
  Future<AdapterList> profileAdapters() async => AdapterList.fromJson(await _transport.request('profiles.adapters', const {}));
  Future<ProfileList> profiles() async => ProfileList.fromJson(await _transport.request('profiles.list', const {}));
  Future<ProfileSummary> selectProfile(String profileId) async => ProfileSummary.fromJson(await _transport.request('profiles.select', {'profile_id': profileId}));
  Future<ProfileSummary> createProfile(ProfileInput input) async => ProfileSummary.fromJson(await _transport.request('profiles.create', input.toCreateJson()));
  Future<ProfileSummary> updateProfile(ProfileInput input) async => ProfileSummary.fromJson(await _transport.request('profiles.update', {'profile_id': input.id, 'profile': input.toUpdateJson()}));
  Future<void> deleteProfile(String profileId) async { await _transport.request('profiles.delete', {'profile_id': profileId}); }
  Future<Object?> inspectProfile(String profileId) => _transport.request('profiles.inspect', {'profile_id': profileId});
  Future<ProfilePlan> planProfile(String profileId) async => ProfilePlan.fromJson(await _transport.request('profiles.plan-apply', {'profile_id': profileId}));
  Future<void> applyProfile(ProfilePlan plan) async {
    if (!plan.ready || plan.revision == null) throw const BridgeError('adapter-unavailable', 'This application adapter is not available for configuration changes.');
    await _transport.request('profiles.apply', {'profile_id': plan.profileId, 'revision': plan.revision});
  }
  Future<RouterStatus> routerStatus() async => RouterStatus.fromJson(await _transport.request('router.status', const {}));
  Future<RouterPlan> planRouter(String profileId, String inbound, String upstream) async => RouterPlan.fromJson(await _transport.request('router.plan-activate', {'profile_id': profileId, 'inbound_protocol': inbound, 'upstream_protocol': upstream}));
  Future<RouterStatus> activateRouter(String profileId, String inbound, String upstream, int revision) async => RouterStatus.fromJson(await _transport.request('router.activate', {'profile_id': profileId, 'inbound_protocol': inbound, 'upstream_protocol': upstream, 'expected_revision': revision}));
  Future<RouterStatus> directRouter(int revision) async => RouterStatus.fromJson(await _transport.request('router.direct', {'expected_revision': revision}));
  Future<RouterStatus> rollbackRouter(int revision) async => RouterStatus.fromJson(await _transport.request('router.rollback', {'expected_revision': revision}));
  Future<ListenerStatus> listenerStatus() async => ListenerStatus.fromJson(await _transport.request('router.listener-status', const {}));
  Future<ListenerStatus> startListener() async => ListenerStatus.fromJson(await _transport.request('router.listener-start', const {'host': '127.0.0.1', 'port': 15721}));
  Future<ListenerStatus> stopListener() async => ListenerStatus.fromJson(await _transport.request('router.listener-stop', const {}));
  Future<List<RouterActivity>> activity() async {
    final data = await _transport.request('router.activity', const {});
    if (data is! Map<Object?, Object?> || data['events'] is! List<Object?>) throw const FormatException('Router activity is invalid.');
    return (data['events']! as List<Object?>).map(RouterActivity.fromJson).toList(growable: false);
  }
  Future<MarketplaceStatus> marketplaceStatus() async => MarketplaceStatus.fromJson(await _transport.request('marketplace.status', const {}));
  Future<List<MarketplaceItem>> marketplaceCatalog([String query = '']) async {
    final data = await _transport.request('marketplace.catalog', {'query': query});
    if (data is! Map<Object?, Object?> || data['items'] is! List<Object?>) throw const FormatException('Marketplace catalog is invalid.');
    return (data['items']! as List<Object?>).map(MarketplaceItem.fromJson).toList(growable: false);
  }
  Future<List<MarketplaceItem>> marketplaceRecommendations() async {
    final data = await _transport.request('marketplace.recommendations', const {});
    if (data is! Map<Object?, Object?> || data['items'] is! List<Object?>) throw const FormatException('Marketplace recommendations are invalid.');
    return (data['items']! as List<Object?>).map(MarketplaceItem.fromJson).toList(growable: false);
  }
  Future<List<IntegrationSummary>> integrations() async {
    final data = await _transport.request('integrations.list', const {});
    if (data is! Map<Object?, Object?> || data['adapters'] is! List<Object?>) throw const FormatException('Integration list is invalid.');
    return (data['adapters']! as List<Object?>).map(IntegrationSummary.fromJson).toList(growable: false);
  }
  Future<void> close() => _transport.close();
}
