import 'package:flutter/material.dart';

import '../application/app_controller.dart';

class DesktopShell extends StatelessWidget {
  const DesktopShell({super.key, required this.controller});

  final AppController controller;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) => Scaffold(
        body: SafeArea(
          child: Row(
            children: [
              NavigationRail(
                selectedIndex: controller.selectedNavigation,
                onDestinationSelected: controller.selectNavigation,
                labelType: NavigationRailLabelType.all,
                destinations: const [
                  NavigationRailDestination(icon: Text('O'), selectedIcon: Text('O'), label: Text('Overview')),
                  NavigationRailDestination(icon: Text('W'), selectedIcon: Text('W'), label: Text('Workspace')),
                  NavigationRailDestination(icon: Text('D'), selectedIcon: Text('D'), label: Text('Design')),
                ],
              ),
              const VerticalDivider(width: 1),
              Expanded(child: _Content(controller: controller)),
            ],
          ),
        ),
      ),
    );
  }
}

class _Content extends StatelessWidget {
  const _Content({required this.controller});
  final AppController controller;

  @override
  Widget build(BuildContext context) {
    final title = ['Overview', 'Workspace', 'Design'][controller.selectedNavigation];
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Expanded(child: Text(title, style: Theme.of(context).textTheme.headlineMedium)),
            TextButton(onPressed: controller.refresh, child: const Text('Refresh')),
          ]),
          const SizedBox(height: 24),
          Expanded(child: _Body(controller: controller, title: title)),
        ],
      ),
    );
  }
}

class _Body extends StatelessWidget {
  const _Body({required this.controller, required this.title});
  final AppController controller;
  final String title;

  @override
  Widget build(BuildContext context) {
    if (controller.phase == WorkbenchPhase.loading) {
      return Center(child: Semantics(label: 'Loading local workspace', child: const CircularProgressIndicator()));
    }
    if (controller.phase != WorkbenchPhase.ready) {
      return Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
        Text(controller.message ?? 'The local workbench is unavailable.'),
        const SizedBox(height: 12),
        TextButton(onPressed: controller.start, child: const Text('Retry bridge')),
      ]));
    }
    if (title != 'Overview') {
      return Text('$title tools will appear here as their first-party specifications are approved.');
    }
    final snapshot = controller.snapshot!;
    return ListView(children: [
      Text('Connected to ModelToolbox ${snapshot.version}'),
      const SizedBox(height: 16),
      if (snapshot.entries.isEmpty) const Text('No local state is available yet.'),
      ...snapshot.entries.map((entry) => Card(child: ListTile(title: Text(entry.key), subtitle: Text(entry.displayValue), trailing: Text(entry.valueType)))),
    ]);
  }
}
