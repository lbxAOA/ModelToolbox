import 'package:flutter/material.dart';

import 'application/app_controller.dart';
import 'bridge/bridge_client.dart';
import 'bridge/python_resolver.dart';
import 'presentation/desktop_shell.dart';

void main() {
  final controller = AppController(BridgeClient(defaultBridgeTransport()));
  runApp(ModelToolboxWorkbench(controller: controller));
  controller.start();
}

class ModelToolboxWorkbench extends StatelessWidget {
  const ModelToolboxWorkbench({super.key, required this.controller});

  final AppController controller;

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xff2459a8);
    return MaterialApp(
      title: 'ModelToolbox Workbench',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: seed, brightness: Brightness.light),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: seed, brightness: Brightness.dark),
        useMaterial3: true,
      ),
      home: DesktopShell(controller: controller),
    );
  }
}
