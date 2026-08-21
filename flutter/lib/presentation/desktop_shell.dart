import 'package:flutter/material.dart';

import '../application/app_controller.dart';
import '../model/management.dart';
import '../model/profile.dart';

class DesktopShell extends StatelessWidget {
  const DesktopShell({super.key, required this.controller});
  final AppController controller;
  @override
  Widget build(BuildContext context) => AnimatedBuilder(animation: controller, builder: (context, _) => Scaffold(body: SafeArea(child: Row(children: [NavigationRail(selectedIndex: controller.selectedNavigation, onDestinationSelected: controller.selectNavigation, labelType: NavigationRailLabelType.all, destinations: const [NavigationRailDestination(icon: Text('O'), selectedIcon: Text('O'), label: Text('Overview')), NavigationRailDestination(icon: Text('P'), selectedIcon: Text('P'), label: Text('Profiles')), NavigationRailDestination(icon: Text('R'), selectedIcon: Text('R'), label: Text('Router')), NavigationRailDestination(icon: Text('I'), selectedIcon: Text('I'), label: Text('Integrations')), NavigationRailDestination(icon: Text('S'), selectedIcon: Text('S'), label: Text('Skills')), NavigationRailDestination(icon: Text('M'), selectedIcon: Text('M'), label: Text('Marketplace'))]), const VerticalDivider(width: 1), Expanded(child: _Content(controller: controller))]))));
}

class _Content extends StatelessWidget {
  const _Content({required this.controller}); final AppController controller;
  @override Widget build(BuildContext context) {
    const titles = ['Overview', 'Profiles', 'Router', 'Integrations', 'Skills', 'Marketplace']; final title = titles[controller.selectedNavigation];
    return Padding(padding: const EdgeInsets.all(24), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Row(children: [Expanded(child: Text(title, style: Theme.of(context).textTheme.headlineMedium)), TextButton(onPressed: controller.refresh, child: const Text('Refresh'))]), const SizedBox(height: 24), Expanded(child: _Body(controller: controller, title: title))]));
  }
}

class _Body extends StatelessWidget {
  const _Body({required this.controller, required this.title}); final AppController controller; final String title;
  @override Widget build(BuildContext context) {
    if (controller.phase == WorkbenchPhase.loading) return const Center(child: CircularProgressIndicator());
    if (controller.phase != WorkbenchPhase.ready) return Center(child: Column(mainAxisSize: MainAxisSize.min, children: [Text(controller.message ?? 'The local workbench is unavailable.'), TextButton(onPressed: controller.start, child: const Text('Retry bridge'))]));
    if (title == 'Profiles') return _Profiles(controller: controller);
    if (title == 'Router') return _Router(controller: controller);
    if (title == 'Integrations') return _Integrations(controller: controller);
    if (title == 'Skills') return const _Skills();
    if (title == 'Marketplace') return _Marketplace(controller: controller);
    final snapshot = controller.snapshot!; return ListView(children: [Text('Connected to ModelToolbox ${snapshot.version}'), ...snapshot.entries.map((entry) => Card(child: ListTile(title: Text(entry.key), subtitle: Text(entry.displayValue), trailing: Text(entry.valueType))))]);
  }
}

class _Integrations extends StatelessWidget {
  const _Integrations({required this.controller});
  final AppController controller;
  @override Widget build(BuildContext context) => ListView(children: [const Text('MCP and Skill integrations use verified contracts. Pending adapters are inspection/export-only.'), const SizedBox(height: 12), ...controller.integrations.map((item) => Card(child: ListTile(title: Text(item.name), subtitle: Text('${item.contractStatus} · config: ${item.configStatus}\n${item.message}'), isThreeLine: true, trailing: Chip(label: Text(item.writeEnabled ? 'Writable' : item.contractStatus)))))]);
}

class _Skills extends StatelessWidget {
  const _Skills();
  @override Widget build(BuildContext context) => const Center(child: Text('Managed Skills inventory is available through the local bridge. Marketplace installation remains explicitly confirmed.'));
}

class _Marketplace extends StatelessWidget {
  const _Marketplace({required this.controller});
  final AppController controller;
  @override Widget build(BuildContext context) {
    final status = controller.marketplaceStatus;
    return ListView(children: [Text(status?.message ?? 'Marketplace status is unavailable.'), const SizedBox(height: 8), Text('Online catalog: ${status?.onlineEnabled == true ? 'enabled' : 'disabled'} · cached items: ${status?.catalogItems ?? 0}'), const SizedBox(height: 16), const Text('Recommendations'), if (controller.recommendations.isEmpty) const Padding(padding: EdgeInsets.only(top: 8), child: Text('No trusted marketplace items are cached. Online refresh must be explicitly enabled.')), ...controller.recommendations.map((item) => _MarketplaceCard(item: item))]);
  }
}

class _MarketplaceCard extends StatelessWidget {
  const _MarketplaceCard({required this.item});
  final MarketplaceItem item;
  @override Widget build(BuildContext context) => Card(child: ListTile(title: Text('${item.name} ${item.version}'), subtitle: Text('${item.kind} · ${item.trust} source · risk: ${item.riskLevel}\n${item.description}'), isThreeLine: true, trailing: Chip(label: Text(item.installable ? 'Review' : 'Manual'))));
}

class _Profiles extends StatelessWidget {
  const _Profiles({required this.controller}); final AppController controller;
  @override Widget build(BuildContext context) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [const Text('Profiles store non-secret endpoints and model preferences. API keys are not managed.'), if (controller.message != null) Padding(padding: const EdgeInsets.only(top: 8), child: Text(controller.message!, style: TextStyle(color: Theme.of(context).colorScheme.error))), const SizedBox(height: 8), Align(alignment: Alignment.centerLeft, child: FilledButton(onPressed: () => _editProfile(context, controller), child: const Text('Add profile'))), Text('Integrations: ${controller.adapters.adapters.map((a) => '${a.name} (${a.available ? 'enabled' : 'pending'})').join(' · ')}'), Expanded(child: controller.profiles.profiles.isEmpty ? const Center(child: Text('No profiles yet.')) : ListView(children: controller.profiles.profiles.map((p) => _ProfileCard(profile: p, controller: controller)).toList())), if (controller.plan != null) _PlanCard(controller: controller)]);
}

class _ProfileCard extends StatelessWidget {
  const _ProfileCard({required this.profile, required this.controller}); final ProfileSummary profile; final AppController controller;
  @override Widget build(BuildContext context) => Card(child: ListTile(title: Text(profile.name), subtitle: Text('${profile.adapterName} · ${profile.adapterAvailable ? 'enabled' : 'pending'}\n${profile.baseUrl}\nModel: ${profile.model ?? 'default'} · API key: not managed'), isThreeLine: true, trailing: Wrap(spacing: 4, children: [if (!profile.selected) TextButton(onPressed: () => controller.selectProfile(profile.id), child: const Text('Select')) else const Chip(label: Text('Selected')), TextButton(onPressed: () => controller.previewProfile(profile.id), child: const Text('Preview')), TextButton(onPressed: () => _editProfile(context, controller, profile), child: const Text('Edit')), TextButton(onPressed: () async { if (await _confirm(context, 'Delete profile?', 'This deletes only the local non-secret profile.')) await controller.deleteProfile(profile.id); }, child: const Text('Delete'))])));
}

class _PlanCard extends StatelessWidget { const _PlanCard({required this.controller}); final AppController controller;
  @override Widget build(BuildContext context) { final plan = controller.plan!; return Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('Apply to ${plan.target}'), ...plan.changes.map((c) => Text('${c.field}: ${c.from ?? 'unset'} → ${c.to ?? 'unset'}')), if (plan.message != null) Text(plan.message!), TextButton(onPressed: plan.ready ? () async { if (await _confirm(context, 'Apply profile?', 'This writes only supported non-secret fields after rechecking the target configuration.')) await controller.applyProfile(); } : null, child: const Text('Confirm and apply'))]))); }
}

class _Router extends StatelessWidget { const _Router({required this.controller}); final AppController controller;
  @override Widget build(BuildContext context) { final router = controller.router; final listener = controller.listener; if (router == null) return const Text('Router status is unavailable.'); final selectedProfiles = controller.profiles.profiles.where((p) => p.selected); final selected = selectedProfiles.isNotEmpty ? selectedProfiles.first : (controller.profiles.profiles.isEmpty ? null : controller.profiles.profiles.first); return ListView(children: [const Text('Local loopback router: bounded, text-only, non-streaming. Authorization and request/response content are never stored or shown.'), const SizedBox(height: 12), Text('Mode: ${router.state} · revision ${router.revision}'), Text(listener?.running == true ? 'Listener: running at ${listener!.host}:${listener.port}' : 'Listener: stopped'), Wrap(spacing: 8, children: [FilledButton(onPressed: selected == null ? null : () => controller.previewRouter(selected.id), child: const Text('Preview route')), TextButton(onPressed: controller.routerPlan?.ready == true ? () async { if (await _confirm(context, 'Activate route?', 'This changes the local route policy.')) await controller.activateRouter(); } : null, child: const Text('Activate')), TextButton(onPressed: () async { if (await _confirm(context, 'Enter direct mode?', 'Requests through the listener will have no active route.')) await controller.directRouter(); }, child: const Text('Direct mode')), TextButton(onPressed: router.previous == null ? null : () async { if (await _confirm(context, 'Roll back route?', 'This swaps the active and previous route policies.')) await controller.rollbackRouter(); }, child: const Text('Rollback')), TextButton(onPressed: () async { if (await _confirm(context, listener?.running == true ? 'Stop listener?' : 'Start listener?', 'The listener is owned by this local bridge session and stops when it exits.')) await controller.toggleListener(); }, child: Text(listener?.running == true ? 'Stop listener' : 'Start listener'))]), if (controller.routerPlan != null) Card(child: ListTile(title: Text('Route preview ${controller.routerPlan!.revision} → ${controller.routerPlan!.nextRevision}'), subtitle: Text(controller.routerPlan!.message ?? 'Ready to activate.'))), const SizedBox(height: 12), const Text('Recent redacted activity'), ...controller.activity.map((a) => ListTile(dense: true, title: Text('${a.inbound} · ${a.outcome}'), trailing: Text('${a.status ?? '-'} · ${a.elapsedMs} ms')))]); }
}

Future<bool> _confirm(BuildContext context, String title, String content) async => await showDialog<bool>(context: context, builder: (context) => AlertDialog(title: Text(title), content: Text(content), actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Confirm'))])) ?? false;

Future<void> _editProfile(BuildContext context, AppController controller, [ProfileSummary? existing]) async { final id = TextEditingController(text: existing?.id ?? ''); final name = TextEditingController(text: existing?.name ?? ''); final base = TextEditingController(text: existing?.baseUrl ?? ''); final model = TextEditingController(text: existing?.model ?? ''); String adapter = existing?.adapterId ?? (controller.adapters.adapters.isEmpty ? 'claude-code' : controller.adapters.adapters.first.id); final saved = await showDialog<bool>(context: context, builder: (context) => AlertDialog(title: Text(existing == null ? 'Create profile' : 'Edit profile'), content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [TextField(controller: id, enabled: existing == null, decoration: const InputDecoration(labelText: 'ID')), TextField(controller: name, decoration: const InputDecoration(labelText: 'Name')), DropdownButtonFormField<String>(initialValue: adapter, items: controller.adapters.adapters.map((a) => DropdownMenuItem(value: a.id, child: Text(a.name))).toList(), onChanged: existing == null ? (v) => adapter = v ?? adapter : null, decoration: const InputDecoration(labelText: 'Adapter')), TextField(controller: base, decoration: const InputDecoration(labelText: 'Base URL')), TextField(controller: model, decoration: const InputDecoration(labelText: 'Model (optional)'))])), actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Save'))])); if (saved == true) { final input = ProfileInput(id: id.text.trim(), name: name.text.trim(), adapterId: adapter, baseUrl: base.text.trim(), model: model.text.trim().isEmpty ? null : model.text.trim()); if (existing == null) await controller.createProfile(input); else await controller.updateProfile(input); } }
