class AdapterSummary {
  const AdapterSummary({required this.id, required this.name, required this.available, required this.message});
  final String id;
  final String name;
  final bool available;
  final String message;
  factory AdapterSummary.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['id'] is! String || source['name'] is! String || source['available'] is! bool || source['message'] is! String) throw const FormatException('Adapter data is incomplete.');
    return AdapterSummary(id: source['id']! as String, name: source['name']! as String, available: source['available']! as bool, message: source['message']! as String);
  }
}

class AdapterList {
  const AdapterList({required this.adapters});
  final List<AdapterSummary> adapters;
  factory AdapterList.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['adapters'] is! List<Object?>) throw const FormatException('Adapter list is invalid.');
    return AdapterList(adapters: (source['adapters']! as List<Object?>).map(AdapterSummary.fromJson).toList(growable: false));
  }
}

class ProfileInput {
  const ProfileInput({required this.id, required this.name, required this.adapterId, required this.baseUrl, this.model, this.credentialSource});
  final String id;
  final String name;
  final String adapterId;
  final String baseUrl;
  final String? model;
  final String? credentialSource;
  Map<String, Object?> toCreateJson() => {'id': id, 'name': name, 'adapter_id': adapterId, 'base_url': baseUrl, 'model': model, 'credential_source': credentialSource};
  Map<String, Object?> toUpdateJson() => {'name': name, 'base_url': baseUrl, 'model': model, 'credential_source': credentialSource};
}

class ProfileSummary {
  const ProfileSummary({required this.id, required this.name, required this.adapterId, required this.adapterName, required this.adapterAvailable, required this.adapterMessage, required this.baseUrl, required this.model, required this.selected});
  final String id;
  final String name;
  final String adapterId;
  final String adapterName;
  final bool adapterAvailable;
  final String adapterMessage;
  final String baseUrl;
  final String? model;
  final bool selected;
  ProfileInput toInput() => ProfileInput(id: id, name: name, adapterId: adapterId, baseUrl: baseUrl, model: model);
  factory ProfileSummary.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['id'] is! String || source['name'] is! String || source['adapter_id'] is! String || source['adapter_name'] is! String || source['adapter_available'] is! bool || source['adapter_message'] is! String || source['base_url'] is! String || source['selected'] is! bool) throw const FormatException('Profile data is incomplete.');
    final model = source['model'];
    if (model != null && model is! String) throw const FormatException('Profile model is invalid.');
    return ProfileSummary(id: source['id']! as String, name: source['name']! as String, adapterId: source['adapter_id']! as String, adapterName: source['adapter_name']! as String, adapterAvailable: source['adapter_available']! as bool, adapterMessage: source['adapter_message']! as String, baseUrl: source['base_url']! as String, model: model as String?, selected: source['selected']! as bool);
  }
}

class ProfileList {
  const ProfileList({required this.selectedProfileId, required this.profiles});
  final String? selectedProfileId;
  final List<ProfileSummary> profiles;
  factory ProfileList.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['profiles'] is! List<Object?>) throw const FormatException('Profile list is invalid.');
    final selected = source['selected_profile_id'];
    if (selected != null && selected is! String) throw const FormatException('Profile selection is invalid.');
    return ProfileList(selectedProfileId: selected as String?, profiles: (source['profiles']! as List<Object?>).map(ProfileSummary.fromJson).toList(growable: false));
  }
}

class ProfileChange {
  const ProfileChange({required this.field, required this.from, required this.to});
  final String field;
  final String? from;
  final String? to;
  factory ProfileChange.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['field'] is! String || source['to'] != null && source['to'] is! String || source['from'] != null && source['from'] is! String) throw const FormatException('Profile preview change is invalid.');
    return ProfileChange(field: source['field']! as String, from: source['from'] as String?, to: source['to'] as String?);
  }
}

class ProfilePlan {
  const ProfilePlan({required this.profileId, required this.target, required this.revision, required this.changes, required this.ready, required this.message});
  final String profileId;
  final String target;
  final String? revision;
  final List<ProfileChange> changes;
  final bool ready;
  final String? message;
  factory ProfilePlan.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['profile_id'] is! String || source['target'] is! String || source['changes'] is! List<Object?> || source['ready'] is! bool) throw const FormatException('Profile preview is invalid.');
    final revision = source['revision']; final message = source['message'];
    if (revision != null && revision is! String || message != null && message is! String) throw const FormatException('Profile preview is invalid.');
    return ProfilePlan(profileId: source['profile_id']! as String, target: source['target']! as String, revision: revision as String?, changes: (source['changes']! as List<Object?>).map(ProfileChange.fromJson).toList(growable: false), ready: source['ready']! as bool, message: message as String?);
  }
}

class RouterStatus {
  const RouterStatus({required this.revision, required this.state, required this.active, required this.previous});
  final int revision; final String state; final Map<Object?, Object?>? active; final Map<Object?, Object?>? previous;
  factory RouterStatus.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['revision'] is! int || source['state'] is! String || source['active'] != null && source['active'] is! Map<Object?, Object?> || source['previous'] != null && source['previous'] is! Map<Object?, Object?>) throw const FormatException('Router status is invalid.');
    return RouterStatus(revision: source['revision']! as int, state: source['state']! as String, active: source['active'] as Map<Object?, Object?>?, previous: source['previous'] as Map<Object?, Object?>?);
  }
}

class RouterPlan {
  const RouterPlan({required this.revision, required this.nextRevision, required this.proposed, required this.ready, required this.message});
  final int revision; final int nextRevision; final Map<Object?, Object?> proposed; final bool ready; final String? message;
  factory RouterPlan.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['revision'] is! int || source['next_revision'] is! int || source['proposed'] is! Map<Object?, Object?> || source['ready'] is! bool || source['message'] != null && source['message'] is! String) throw const FormatException('Router plan is invalid.');
    return RouterPlan(revision: source['revision']! as int, nextRevision: source['next_revision']! as int, proposed: source['proposed']! as Map<Object?, Object?>, ready: source['ready']! as bool, message: source['message'] as String?);
  }
}

class ListenerStatus {
  const ListenerStatus({required this.running, this.host, this.port});
  final bool running; final String? host; final int? port;
  factory ListenerStatus.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['running'] is! bool || source['host'] != null && source['host'] is! String || source['port'] != null && source['port'] is! int) throw const FormatException('Router listener is invalid.');
    return ListenerStatus(running: source['running']! as bool, host: source['host'] as String?, port: source['port'] as int?);
  }
}

class RouterActivity {
  const RouterActivity({required this.inbound, required this.outcome, required this.status, required this.elapsedMs});
  final String inbound; final String outcome; final int? status; final int elapsedMs;
  factory RouterActivity.fromJson(Object? source) {
    if (source is! Map<Object?, Object?> || source['inbound_protocol'] is! String || source['outcome'] is! String || source['elapsed_ms'] is! int || source['status'] != null && source['status'] is! int) throw const FormatException('Router activity is invalid.');
    return RouterActivity(inbound: source['inbound_protocol']! as String, outcome: source['outcome']! as String, status: source['status'] as int?, elapsedMs: source['elapsed_ms']! as int);
  }
}
